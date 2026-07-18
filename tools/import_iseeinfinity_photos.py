from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps


REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "assets" / "img" / "journey"
BASE = "https://iseeinfinity.com/wp-content/uploads/2021/04/"

PHOTOS = [
    ("brisbane-story-bridge", "123415319_990825808077574_876916776874469367_n_17886778534781199-1024x1024.jpg"),
    ("gates-of-heaven", "118395557_1461486964059544_269578318966666652_n_17868805009952983-819x1024.jpg"),
    ("cathedral-square", "118189815_1429194787268474_494528719244304839_n_18049225324249538-819x1024.jpg"),
    ("roma-street-art", "123216631_3129831863896619_3112005899628952188_n_17856732839255836-819x1024.jpg"),
    ("mooloolaba-main-beach", "123187322_365343031187628_7990134132409600941_n_17854161062307822-819x1024.jpg"),
    ("cape-byron-lookout", "123017251_187210946229152_6747146015634143463_n_17882832541824878-819x1024.jpg"),
    ("byron-lighthouse-birdseye", "122995882_484360659121093_1818578195444535914_n_17860203173218128-819x1024.jpg"),
    ("byron-lighthouse", "123285230_203538827905727_33128513272048276_n_17860403705221144-1024x1024.jpg"),
    ("byron-seeing-eye-to-eye", "123535475_771406580076221_4080650702618386538_n_17905748566532383-1024x1024.jpg"),
    ("byron-seeing-double", "123148535_856143158483851_4164846525547372067_n_17844585752454751-1024x1024.jpg"),
    ("byron-mirror-world", "123248454_287335762434019_906255225596759717_n_17856194453282020-1024x1024.jpg"),
    ("byron-hive-mind", "123390102_1934816296660496_4249572733451268613_n_17905611538527605-1024x1024.jpg"),
    ("byron-mega-mind", "123020963_117911673427238_4387805335304017453_n_17844606557467776-1024x1024.jpg"),
    ("byron-fractal-worlds", "123243705_775213206662131_7249110941424377797_n_17876831434943338-1024x1024.jpg"),
    ("byron-hall-of-mirrors", "123266790_207538144134012_523239296874322631_n_17888404675731307-1024x1024.jpg"),
    ("king-george-square", "Brisbane-King-George-Square-Tiny-Planet.png"),
    ("south-bank-arbour", "121053903_2364033887237571_3953816731448519211_n_17848036910355284-819x1024.jpg"),
    ("musgrave-park-festival", "126198517_135499674645908_14880498177244293_n_17932818139437127-819x1024.jpg"),
    ("wivenhoe-high-low", "123652055_195595075495190_817920102565894728_n_17912823022497763-819x1024.jpg"),
    ("wivenhoe-park", "123571136_684610685780869_6260009791280213291_n_17873073539009746-819x1024.jpg"),
    ("wivenhoe-lookout", "123538392_281220896536970_1218928869596457392_n_17911007443507613-819x1024.jpg"),
    ("summer-waters", "131933255_429070381554933_8413602293866089508_n_18083408875239985-1024x1024.jpg"),
    ("amity-point", "122831644_774157520033888_2851665653569622465_n_17865924500121212-819x1024.jpg"),
    ("amity-meditation", "122465126_843788309725600_5368482738299139529_n_17884209622786977-819x1024.jpg"),
    ("amity-camp-birdseye", "160252864_303616331175478_5199371928844016585_n_17899156546809287-819x1024.jpg"),
    ("amity-camping-ground", "160360423_486742465661178_8127495382945397743_n_17993622751323785-819x1024.jpg"),
    ("amity-schoolhouse-sunset", "133432944_2842161096024397_3214742818111482402_n_17879051399033053-819x1024.jpg"),
    ("amity-jetty-sunset", "132799858_814729732715761_2787944087971392538_n_18181492987018937-819x1024.jpg"),
]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    total_before = 0
    total_after = 0
    for slug, filename in PHOTOS:
        request = Request(BASE + filename, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=30) as response:
            payload = response.read()
        total_before += len(payload)
        with Image.open(BytesIO(payload)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
            target = OUTPUT / f"{slug}.webp"
            image.save(target, "WEBP", quality=82, method=6)
        total_after += target.stat().st_size
    print(f"Optimised {len(PHOTOS)} photographs: {total_before:,} -> {total_after:,} bytes")


if __name__ == "__main__":
    main()
