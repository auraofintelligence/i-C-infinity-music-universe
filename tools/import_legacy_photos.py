from __future__ import annotations

import hashlib
import json
import re
from html import unescape
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps


REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "assets" / "img" / "site-archive"
MANIFEST = REPO / "data" / "photo-archive.json"
USER_AGENT = "Mozilla/5.0 (compatible; i-C-infinity-photo-archive/1.0)"

SITES = {
    "i-see-infinity": {
        "name": "I See Infinity",
        "root": "https://iseeinfinity.com/",
        "api": "https://iseeinfinity.com/wp-json/wp/v2/",
    },
    "luke-catalyst": {
        "name": "Luke Catalyst",
        "root": "https://lukecatalyst.com/",
        "api": "https://lukecatalyst.com/wp-json/wp/v2/",
    },
}

# These are the 30 photographs and 360-degree variations in the large carousel
# on the I See Infinity home page, kept in the order shown on the original site.
ISEE_CAROUSEL_IDS = [
    277,
    72,
    148,
    151,
    150,
    147,
    146,
    145,
    144,
    134,
    135,
    133,
    157,
    160,
    155,
    156,
    158,
    69,
    140,
    139,
    138,
    137,
    136,
    130,
    142,
    141,
    127,
    128,
    132,
    131,
]

# Luke Catalyst's Life Gallery places the India travel photographs together in
# this media-ID block. The user explicitly asked for none of them in this repo.
EXCLUDED_MEDIA_IDS = {
    "luke-catalyst": set(range(125, 148)),
    "i-see-infinity": set(),
}

# Contact/link graphics, writing thumbnails and the two oversized empty-canvas
# graphics are not part of the preserved visual story.
EXCLUDED_ARCHIVE_MEDIA_IDS = {
    "luke-catalyst": {38, 39, 66, 68, 69, 73, 205, 209, 257, 286, 306},
    "i-see-infinity": set(),
}

CAPTION_OVERRIDES = {
    ("luke-catalyst", 26): "Luke Circle",
    ("luke-catalyst", 29): "Wizard, Poet and Spiritual Gamer",
    ("luke-catalyst", 31): "Luke Olympic Tiny Planet",
    ("luke-catalyst", 32): "Gates of Heaven",
    ("luke-catalyst", 33): "Luke",
    ("luke-catalyst", 35): "Brisbane 360",
    ("luke-catalyst", 38): "Aura of i - Universe",
    ("luke-catalyst", 39): "Luke Catalyst business card",
    ("luke-catalyst", 42): "ENFP-A",
    ("luke-catalyst", 43): "Luke Looks Twice",
    ("luke-catalyst", 44): "Aura Heart",
    ("luke-catalyst", 45): "Luke, Leeds and the Robot Cake",
    ("luke-catalyst", 50): "Luke Catalyst portrait with colourful artwork",
    ("luke-catalyst", 53): "500 Queens Venture Capital meetup",
    ("luke-catalyst", 54): "Aura of Intelligence interface",
    ("luke-catalyst", 55): "Global Group Marriages",
    ("luke-catalyst", 66): "G.A.J.R.A. Earth",
    ("luke-catalyst", 68): "Aura of Intelligence on Luke's LinkedIn profile",
    ("luke-catalyst", 69): "AngelList",
    ("luke-catalyst", 73): "Luke Universe",
    ("luke-catalyst", 78): "Aura of Australia",
    ("luke-catalyst", 79): "Aura Shared Living",
    ("luke-catalyst", 81): "Aura of Australia Agenda",
    ("luke-catalyst", 82): "Build an AI for Lab or Home",
    ("luke-catalyst", 83): "Aura of Asia",
    ("luke-catalyst", 90): "Aura Undies",
    ("luke-catalyst", 95): "King George Square Tiny Planet",
    ("luke-catalyst", 96): "Brisbane Tiny Planet",
    ("luke-catalyst", 97): "Gates of Heaven",
    ("luke-catalyst", 98): "Luke Olympic Tiny Planet",
    ("luke-catalyst", 104): "Weatherman's Guide to the Sun, Third Edition",
    ("luke-catalyst", 108): "Ophiuchus",
    ("luke-catalyst", 109): "Chinese Zodiac: Water Dog",
    ("luke-catalyst", 110): "Celtic Birth Totem: Hawk",
    ("luke-catalyst", 111): "Native American Birth Totem: Deer",
    ("luke-catalyst", 112): "The Meaning of Luke",
    ("luke-catalyst", 113): "The Meaning of Nathan",
    ("luke-catalyst", 114): "The Hayes Name",
    ("luke-catalyst", 162): "Luke's Enneagram",
    ("luke-catalyst", 205): "Global Group Marriages",
    ("luke-catalyst", 207): "Gamify Democracy: From Now to the Space Age",
    ("luke-catalyst", 209): "Aura Affinity Store",
    ("luke-catalyst", 214): "Luke Circle",
    ("luke-catalyst", 249): "Aura: What If?",
    ("luke-catalyst", 257): "Aura Live Aid 2025",
    ("luke-catalyst", 286): "Schedule",
    ("luke-catalyst", 306): "Luke's Start-up Vision",
    ("luke-catalyst", 323): "Aura Web",
}


def request_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        return response.read()


def request_json(url: str) -> object:
    return json.loads(request_bytes(url))


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", unescape(value or ""))
    return re.sub(r"\s+", " ", value).strip()


def normalise_stem(url: str) -> str:
    stem = Path(urlparse(url).path).stem.lower()
    stem = re.sub(r"-scaled$", "", stem)
    stem = re.sub(r"-\d+x\d+$", "", stem)
    return stem


def image_ids_from_html(page_html: str, media_by_stem: dict[str, int]) -> list[int]:
    ordered: list[int] = []

    def remember(media_id: int) -> None:
        if media_id not in ordered:
            ordered.append(media_id)

    for match in re.finditer(r"(?:wp-image-|data-id=[\"'])(\d+)", page_html, re.I):
        remember(int(match.group(1)))

    for match in re.finditer(r"<img[^>]+src=[\"']([^\"']+)", page_html, re.I):
        media_id = media_by_stem.get(normalise_stem(unescape(match.group(1))))
        if media_id:
            remember(media_id)

    return ordered


def collect_site(
    site_key: str, config: dict[str, str]
) -> tuple[list[dict], dict[int, list[str]], dict[int, dict[str, int]]]:
    media = request_json(f"{config['api']}media?per_page=100")
    pages = request_json(f"{config['api']}pages?per_page=100")
    image_media = [item for item in media if str(item.get("mime_type", "")).startswith("image/")]
    media_by_stem = {
        normalise_stem(item["source_url"]): int(item["id"])
        for item in image_media
        if item.get("source_url")
    }
    used_on: dict[int, list[str]] = {}
    page_positions: dict[int, dict[str, int]] = {}

    for page in pages:
        page_url = page.get("link")
        if not page_url:
            continue
        page_slug = page.get("slug") or "home"
        page_html = request_bytes(page_url).decode("utf-8", "replace")
        for position, media_id in enumerate(image_ids_from_html(page_html, media_by_stem), start=1):
            used_on.setdefault(media_id, []).append(page_slug)
            page_positions.setdefault(media_id, {})[page_slug] = position

    # The public carousel is authoritative even if WordPress changes its classes.
    if site_key == "i-see-infinity":
        for position, media_id in enumerate(ISEE_CAROUSEL_IDS, start=1):
            used_on.setdefault(media_id, []).append("i-see-infinity-carousel")
            page_positions.setdefault(media_id, {})["i-see-infinity-carousel"] = position

    return image_media, used_on, page_positions


def safe_filename(site_key: str, item: dict) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(item.get("slug", "")).lower()).strip("-")
    return f"{site_key}-{item['id']}-{slug or 'photo'}.webp"


def exclusion_reason(site_key: str, item: dict) -> str:
    if int(item["id"]) in EXCLUDED_MEDIA_IDS[site_key]:
        return "india"
    if int(item["id"]) in EXCLUDED_ARCHIVE_MEDIA_IDS[site_key]:
        return "archive_chaff"
    search_text = " ".join(
        [
            str(item.get("slug", "")),
            str(item.get("source_url", "")),
            clean_text(item.get("title", {}).get("rendered", "")),
            clean_text(item.get("caption", {}).get("rendered", "")),
        ]
    ).lower()
    if "india" in search_text:
        return "india"
    if "promo_card" in search_text or "promo-card" in search_text or "paypal" in search_text:
        return "promotional"
    return ""


def convert_image(payload: bytes, target: Path) -> tuple[int, int, int]:
    with Image.open(BytesIO(payload)) as source:
        image = ImageOps.exif_transpose(source)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        width, height = image.size
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, "WEBP", quality=84, method=6)
    return width, height, target.stat().st_size


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for existing in OUTPUT.glob("*.webp"):
        existing.unlink()
    records: list[dict] = []
    retained_hashes: dict[str, str] = {}
    source_bytes = 0
    webp_bytes = 0
    excluded_india = 0
    excluded_promotional = 0
    excluded_archive_chaff = 0

    for site_key, config in SITES.items():
        media, used_on, page_positions = collect_site(site_key, config)
        for item in media:
            media_id = int(item["id"])
            if media_id not in used_on:
                continue
            reason = exclusion_reason(site_key, item)
            if reason == "india":
                excluded_india += 1
                continue
            if reason == "promotional":
                excluded_promotional += 1
                continue
            if reason == "archive_chaff":
                excluded_archive_chaff += 1
                continue

            payload = request_bytes(item["source_url"])
            source_bytes += len(payload)
            digest = hashlib.sha256(payload).hexdigest()
            duplicate_of = retained_hashes.get(digest)
            filename = safe_filename(site_key, item)
            target = OUTPUT / filename

            if duplicate_of:
                filename = duplicate_of
                with Image.open(BytesIO(payload)) as source:
                    width, height = source.size
                size = (OUTPUT / filename).stat().st_size
            else:
                width, height, size = convert_image(payload, target)
                retained_hashes[digest] = filename
                webp_bytes += size

            title = clean_text(item.get("title", {}).get("rendered", ""))
            caption = clean_text(item.get("caption", {}).get("rendered", ""))
            display_caption = CAPTION_OVERRIDES.get((site_key, media_id), caption or title)
            records.append(
                {
                    "site": site_key,
                    "site_name": config["name"],
                    "media_id": media_id,
                    "title": title or caption or f"Archive image {media_id}",
                    "caption": display_caption,
                    "source_url": item["source_url"],
                    "file": f"assets/img/site-archive/{filename}",
                    "width": width,
                    "height": height,
                    "used_on": sorted(set(used_on[media_id])),
                    "page_positions": page_positions.get(media_id, {}),
                    "carousel_order": (
                        ISEE_CAROUSEL_IDS.index(media_id) + 1
                        if site_key == "i-see-infinity" and media_id in ISEE_CAROUSEL_IDS
                        else None
                    ),
                }
            )

    records.sort(
        key=lambda item: (
            0 if item["carousel_order"] else 1,
            item["carousel_order"] or 999,
            item["site"],
            item["media_id"],
        )
    )
    manifest = {
        "summary": {
            "records": len(records),
            "unique_webp_files": len(retained_hashes),
            "excluded_india_images": excluded_india,
            "excluded_promotional_images": excluded_promotional,
            "excluded_archive_chaff": excluded_archive_chaff,
            "source_bytes": source_bytes,
            "webp_bytes": webp_bytes,
        },
        "images": records,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Archived {len(records)} image records as {len(retained_hashes)} WebP files; "
        f"excluded {excluded_india} India images, {excluded_promotional} promotional images "
        f"and {excluded_archive_chaff} archive-chaff images; "
        f"{source_bytes:,} -> {webp_bytes:,} bytes."
    )


if __name__ == "__main__":
    main()
