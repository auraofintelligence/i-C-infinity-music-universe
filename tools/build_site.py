from __future__ import annotations

import html
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import quote


REPO = Path(__file__).resolve().parents[1]
LYRIC_SOURCE = Path(r"C:\Users\lukec\Downloads\4th i C. infinity album (24) A Protopian Gambit (24 lyrics).md")
STRADDIE_FUN_LYRIC_SOURCE = Path(r"C:\Users\lukec\Downloads\Straddie Fun 5th Album.md")
STARSEED_TEXT_LYRIC_SOURCE = Path(r"C:\Users\lukec\Downloads\3rd Album Starseed Code.txt")
ALBUM_LYRIC_ROOT = Path(r"C:\Users\lukec\Documents\Beyond\69 i C. infinity - Music\Albums")
SINGLES_LYRIC_ROOT = Path(r"C:\Users\lukec\Documents\Beyond\69 i C. infinity - Music\Singles")
ALBUM_LYRIC_FOLDERS = {
    "Songs of Straddie": "songs-of-straddie",
    "Chronicles of the Forgotten": "chronicles-of-the-forgotten",
    "Starseed Code - From Aura to Infinity": "starseed-code-from-aura-to-infinity",
}
LYRIC_SLUG_ALIASES = {
    ("songs-of-straddie", "straddie-summer-love"): "straddie-summer-love-by-he",
    ("chronicles-of-the-forgotten", "algorithm-of-hope"): "algorithm-hope",
    ("chronicles-of-the-forgotten", "echo-s-of-the-ancients"): "echos-of-the-ancients",
    ("starseed-code-from-aura-to-infinity", "from-straddy-s-shores"): "from-straddie-s-shores-to-galactic-plains",
    ("starseed-code-from-aura-to-infinity", "from-straddys-shores"): "from-straddie-s-shores-to-galactic-plains",
    ("starseed-code-from-aura-to-infinity", "from-straddy-s-shores-to-galactic-plains"): "from-straddie-s-shores-to-galactic-plains",
    ("starseed-code-from-aura-to-infinity", "from-straddys-shores-to-galactic-plains"): "from-straddie-s-shores-to-galactic-plains",
    ("starseed-code-from-aura-to-infinity", "gajra-rising"): "g-a-j-r-a-rising",
}
SINGLE_LYRIC_TARGETS = {
    "building-protopia-brick-by-brick": [
        ("singles-and-public-markers", "building-protopia-brick-by-brick"),
    ],
    "chatgpt-my-view-of-our-conversation": [
        ("singles-and-public-markers", "our-conversation-about-a-g-i"),
        ("early-stuff", "a-song-by-chatgpt-3-my-view-of-my-conversation-with-luke-catalyst"),
    ],
    "futuristic-frequencies-the-gajra-earth-vibe": [
        ("singles-and-public-markers", "futuristic-frequencies"),
        ("early-stuff", "futuristic-frequencies-the-g-a-j-r-a-earth-vibe"),
    ],
    "straddie-summer-love": [
        ("singles-and-public-markers", "straddie-summer-love-special-version-by-he"),
    ],
}


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "item"


def clean_text(value: str) -> str:
    replacements = {
        "\u00e2\u20ac\u2122": "'",
        "\u00e2\u20ac\u02dc": "'",
        "\u00e2\u20ac\u0153": '"',
        "\u00e2\u20ac\u009d": '"',
        "\u00e2\u20ac\u201d": "-",
        "\u00e2\u20ac\u201c": "-",
        "\u00e2\u20ac\u00a6": "...",
        "\u00c2\u00a0": " ",
        "\u00c3\u00a9": "e",
    }
    for bad, good in replacements.items():
        value = value.replace(bad, good)
    value = value.replace("\\[", "[").replace("\\]", "]")
    value = value.replace("â€™", "'").replace("â€œ", '"').replace("â€\u009d", '"')
    value = value.replace("â€”", "-").replace("â€“", "-").replace("â€¦", "...")
    value = value.replace("Â", "")
    return value.strip()


def read_repo_text(relative_path: str) -> str:
    path = REPO / relative_path
    if not path.exists():
        return ""
    return clean_text(path.read_text(encoding="utf-8", errors="replace"))


def load_photo_archive() -> list[dict]:
    if not PHOTO_ARCHIVE_DATA.exists():
        return []
    payload = json.loads(PHOTO_ARCHIVE_DATA.read_text(encoding="utf-8"))
    return payload.get("images", [])


def archive_photo(site: str, media_id: int, fallback: str = "") -> str:
    for image in load_photo_archive():
        if image.get("site") == site and image.get("media_id") == media_id:
            return str(image.get("file", fallback))
    return fallback


def archive_carousel_photo(order: int, fallback: str = "") -> str:
    for image in load_photo_archive():
        if image.get("carousel_order") == order:
            return str(image.get("file", fallback))
    return fallback


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def page_path(path: Path) -> str:
    return str(path).replace("\\", "/")


@dataclass
class Song:
    title: str
    album_slug: str
    album_title: str
    track_number: int | None = None
    year: str = ""
    release_url: str = ""
    apple_url: str = ""
    spotify_url: str = ""
    youtube_video_id: str = ""
    youtube_title: str = ""
    youtube_videos: list[dict[str, str]] = field(default_factory=list)
    lyrics: str = ""
    lyric_status: str = "Lyrics to import"
    status: str = "Draft brief"
    themes: list[str] = field(default_factory=list)
    meaning: str = ""
    video_seeds: list[dict[str, str]] = field(default_factory=list)
    slug: str = ""

    def ready(self) -> bool:
        return bool(self.lyrics.strip())


@dataclass
class Album:
    title: str
    slug: str
    year: str
    status: str
    summary: str
    deeper_system: str
    visual_world: str
    artwork: str
    source_url: str = ""
    spotify_url: str = ""
    tracks: list[Song] = field(default_factory=list)


APPLE_ARTIST = "https://music.apple.com/us/artist/i-c-infinity/1781660070"
SPOTIFY_ARTIST = "https://open.spotify.com/artist/3HK8H81lXFXOEJaSys7xfQ"
MAIN_SITE = "https://iseeinfinity.com/"
LUKE_CATALYST_SITE = "https://lukecatalyst.com/"
TRAVEL_ORACLE_SITE = "https://auraofintelligence.github.io/strange-but-true-travel-oracle/"
AUSTRALIAN_WORLD_TRAVEL_SITE = "https://auraofintelligence.github.io/Australian-world-travel/"
COSMIC_NEXUS_SITE = "https://auraofintelligence.github.io/strange-but-true-cosmic-nexus/"
RIGHT_PLACE_RIGHT_TIME_SITE = "https://auraofintelligence.github.io/right-place-right-time/"
GLOBAL_GROUP_MARRIAGES_SITE = "https://auraofintelligence.github.io/global-group-marriages/"
GREY_AREA_COMMONS_SITE = "https://auraofintelligence.github.io/grey-area-commons/"
AURA_OF_INTELLIGENCE_SITE = "https://auraofintelligence.github.io/"
GAJRA_EARTH_SITE = "https://auraofintelligence.github.io/gajra-earth-public-hub/"
STRANGE_BUT_TRUE_SITE = "https://auraofintelligence.github.io/strange-but-true/"
MUSIC_DOWNLOADS_PAGE = "https://auraofintelligence.github.io/i-C-infinity-music-universe/downloads.html"
SITE_ROOT = "https://auraofintelligence.github.io/i-C-infinity-music-universe/"
STREAMING_LINKS = REPO / "data" / "streaming-links.json"
PHOTO_ARCHIVE_DATA = REPO / "data" / "photo-archive.json"
ORDER_PAGE = f"{MUSIC_DOWNLOADS_PAGE}#order-music"
LEGACY_PHOTOS = [
    ("luke-catalyst-portrait", "Luke Catalyst"),
    ("wizard-poet-spiritual-gamer", "Wizard, poet and spiritual gamer"),
    ("luke-olympic-tiny-planet", "Luke Olympic tiny planet"),
    ("brisbane-tiny-planet", "Brisbane tiny planet"),
    ("brisbane-story-bridge", "Brisbane Story Bridge"),
    ("byron-bay-lighthouse", "Byron Bay Lighthouse"),
    ("musgrave-park-festival", "Meanjin Reggae Festival, Musgrave Park"),
    ("wivenhoe-lookout", "Wivenhoe Dam lookout"),
    ("amity-point", "Amity Point, Minjerribah"),
    ("amity-jetty-sunset", "Amity jetty at sunset"),
]
STARSEED_ALBUM_SLUG = "starseed-code-from-aura-to-infinity"
STARSEED_YOUTUBE_PLAYLIST_ID = "PLsN0U9hPJHBZyRTYmAwLCuVSpY9q_-tCd"
STARSEED_YOUTUBE_PLAYLIST_URL = f"https://www.youtube.com/playlist?list={STARSEED_YOUTUBE_PLAYLIST_ID}"
STRADDIE_YOUTUBE_PLAYLIST_ID = "PL9jLSm_Ni6aHZ9EYoZGKCJn-tfJHYO5fn"
STRADDIE_YOUTUBE_PLAYLIST_URL = f"https://www.youtube.com/playlist?list={STRADDIE_YOUTUBE_PLAYLIST_ID}"
CHRONICLES_YOUTUBE_PLAYLIST_ID = "PL9jLSm_Ni6aH7AgXFe9H8xCROWw9KS9uk"
CHRONICLES_YOUTUBE_PLAYLIST_URL = f"https://www.youtube.com/playlist?list={CHRONICLES_YOUTUBE_PLAYLIST_ID}"
EARLY_STUFF_YOUTUBE_PLAYLIST_ID = "PLsN0U9hPJHBY4UVdbnke0Aws6MwPfXlAt"
EARLY_STUFF_YOUTUBE_PLAYLIST_URL = f"https://www.youtube.com/playlist?list={EARLY_STUFF_YOUTUBE_PLAYLIST_ID}"
FOURTH_ALBUM_TEASER_VIDEO = {
    "id": "zgvb6PPlaRY",
    "title": "Untitled fourth album teaser video",
    "label": "Free Fourth-Album Teaser",
    "orientation": "landscape",
    "thumbnail": "maxresdefault",
    "url": "https://youtu.be/zgvb6PPlaRY?si=OC7gybUgeOu0ix5K",
}
SHIFTING_SANDS_VIDEOS = [
    {
        "id": "uKygQx_8dos",
        "title": "Shifting Sands of Timeless Redlands widescreen video",
        "label": "Widescreen Video",
        "orientation": "landscape",
        "thumbnail": "sddefault",
        "url": "https://youtu.be/uKygQx_8dos?si=EJ0uT78HYJ22zy7a",
    },
    {
        "id": "OZRZy6LYQkg",
        "title": "Shifting Sands of Timeless Redlands portrait video",
        "label": "Portrait Video",
        "orientation": "vertical",
        "thumbnail": "maxresdefault",
        "url": "https://youtu.be/OZRZy6LYQkg?si=a9qnTQiwTJCVSqNM",
    },
]


STRADDIE_LYRIC_VIDEOS = {
    "Our Island Home!": [
        {"id": "kiHNBKeT2zQ", "title": "Our Island Home lyric video", "label": "Landscape Lyric Video"},
    ],
    "Beachside Rhythm": [
        {"id": "Y7DiLtgc1Bw", "title": "Beachside Rhythm (By He) lyric video", "label": "Landscape Lyric Video (By He)"},
        {"id": "C2s5fGQ7txw", "title": "Beachside Rhythm (By She) lyric video", "label": "Landscape Lyric Video (By She)"},
    ],
    "Gather by the Fire": [
        {"id": "sxJESmM6LB4", "title": "Gather by the Fire lyric video", "label": "Landscape Lyric Video"},
    ],
    "Straddie Summer Love (By She)": [
        {"id": "D9hJ9kHxZZg", "title": "Straddie Summer Love (By She) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Straddie Summer Love (By He)": [
        {"id": "XeIDgiILzp8", "title": "Straddie Summer Love (By He) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Union of Souls (By She)": [
        {"id": "N4YwZmurJMc", "title": "Union of Souls (By She) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Union of Souls (By He)": [
        {"id": "yfH4-_IAFfs", "title": "Union of Souls (By He) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Born of the Goddess": [
        {"id": "gWNBYGNEJZs", "title": "Born of the Goddess lyric video", "label": "Landscape Lyric Video"},
    ],
}


STRADDIE_PLAYLIST_ONLY_VIDEOS = [
    {"id": "m5HfpL_1yi0", "title": "Dolphin Daze lyric video"},
    {"id": "rAzpWXaS9ko", "title": "Dance of the Dakini (By She) lyric video"},
    {"id": "BGStqXamlzw", "title": "Dance of the Dakini (By He) lyric video"},
]


CHRONICLES_LYRIC_VIDEOS = {
    "Echos of the Ancients": [
        {"id": "ybZ3oWjlcg8", "title": "Echos of the Ancients lyric video", "label": "Landscape Lyric Video"},
    ],
    "Shadows Over the Earth": [
        {"id": "adUke4EL0c8", "title": "Shadows over the Earth lyric video", "label": "Landscape Lyric Video"},
    ],
    "Dreams of Abundance (by she)": [
        {"id": "_UMJnq-VuRE", "title": "Dreams of Abundance (by she) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Dreams of Abundance (by he)": [
        {"id": "5wJP9cD-h2g", "title": "Dreams of Abundance (by he) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Signal From the Stars": [
        {"id": "gmTN9nlduOQ", "title": "Signal from the Stars lyric video", "label": "Landscape Lyric Video"},
    ],
    "Algorithm: Hope": [
        {"id": "iflDVjy8BeQ", "title": "Algorithm Hope lyric video", "label": "Landscape Lyric Video"},
    ],
    "Hearts and Circuits (by she)": [
        {"id": "mFsln7mlGtU", "title": "Hearts and Circuits (by she) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Hearts and Circuits (by he)": [
        {"id": "0CS-3oqkSnA", "title": "Hearts and Circuits (by he) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Walls of Deception (by she)": [
        {"id": "xQH7HcbkRfQ", "title": "Walls of Deception (by she) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Walls of Deception (by he)": [
        {"id": "YV24_UC4mrM", "title": "Walls of Deception (by he) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Breaking Chains": [
        {"id": "mEZgZDfhCLU", "title": "Breaking Chains lyric video", "label": "Landscape Lyric Video"},
    ],
    "Voices Unheard": [
        {"id": "kOeUNmUQ1S4", "title": "Voices Unheard lyric video", "label": "Landscape Lyric Video"},
    ],
    "Cycle of Suns (by he)": [
        {"id": "rNrGvBYXqic", "title": "Cycle of Suns (by he) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Cycle of Suns (by she)": [
        {"id": "FB7E99ZdcBI", "title": "Cycle of Suns (by she) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Chronicles of the Forgotten": [
        {"id": "SGp_WfDuUP0", "title": "Chronicles of the Forgotten lyric video", "label": "Landscape Lyric Video"},
    ],
    "Celestial Navigators": [
        {"id": "aqNJGzAXszk", "title": "Celestial Navigators lyric video", "label": "Landscape Lyric Video"},
    ],
    "Symphony of Souls": [
        {"id": "rQ8zHdhPqXU", "title": "Symphony of Souls lyric video", "label": "Landscape Lyric Video"},
    ],
    "Digital Dawn": [
        {"id": "EERpSPJhgWc", "title": "Digital Dawn lyric video", "label": "Landscape Lyric Video"},
    ],
    "Whispers of Gaia (by she)": [
        {"id": "eGN7n0Z0IpA", "title": "Whispers of Gaia (by she) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Whispers of Gaia (by he)": [
        {"id": "hwpPeiT2t4g", "title": "Whispers of Gaia (by he) lyric video", "label": "Landscape Lyric Video"},
    ],
    "Bridging the Divide": [
        {"id": "nRiCVntYJJE", "title": "Bridging the Divide lyric video", "label": "Landscape Lyric Video"},
    ],
    "Pulse of the Universe": [
        {"id": "JdAjTRfwazM", "title": "Pulse of the Universe lyric video", "label": "Landscape Lyric Video"},
    ],
    "Resonance": [
        {"id": "FK9upHoQlU8", "title": "Resonance lyric video", "label": "Landscape Lyric Video"},
    ],
    "Tempest of Trials": [
        {"id": "_2eFQHEtTw8", "title": "Tempest of Trials lyric video", "label": "Landscape Lyric Video"},
    ],
}


CHRONICLES_PLAYLIST_ONLY_VIDEOS = [
    {"id": "mbHDw0Bh4xU", "title": "Illusions Shattered lyric video"},
]


LANDSCAPE_ALBUM_VIDEO_MAP = {
    "early-stuff": {
        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
        "playlist_url": EARLY_STUFF_YOUTUBE_PLAYLIST_URL,
        "title": "India 2023/24 Early Stuff Playlist",
        "eyebrow": "Early music videos",
        "description": "Early i C. infinity videos made during Luke's time in India. They show where the music began and how its ideas changed.",
        "videos": {},
        "playlist_only": [],
    },
    "songs-of-straddie": {
        "playlist_id": STRADDIE_YOUTUBE_PLAYLIST_ID,
        "playlist_url": STRADDIE_YOUTUBE_PLAYLIST_URL,
        "title": "Songs of Straddie Lyric Video Playlist",
        "eyebrow": "Widescreen lyric videos",
        "description": "The full Songs of Straddie release has {track_count} songs. This playlist includes the music videos available now. Keep scrolling for the complete song list, lyrics and individual song pages.",
        "videos": STRADDIE_LYRIC_VIDEOS,
        "playlist_only": STRADDIE_PLAYLIST_ONLY_VIDEOS,
    },
    "chronicles-of-the-forgotten": {
        "playlist_id": CHRONICLES_YOUTUBE_PLAYLIST_ID,
        "playlist_url": CHRONICLES_YOUTUBE_PLAYLIST_URL,
        "title": "Chronicles of the Forgotten Lyric Video Playlist",
        "eyebrow": "Widescreen lyric videos",
        "description": "Music videos from the rock opera, with more lyrics and songs below.",
        "videos": CHRONICLES_LYRIC_VIDEOS,
        "playlist_only": CHRONICLES_PLAYLIST_ONLY_VIDEOS,
    },
}


STARSEED_VERTICAL_VIDEOS = {
    "Aura": {
        "id": "F_Rr4fZzh2g",
        "title": "Aura (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Building Protopia Brick By Brick": {
        "id": "kRhF340Y-dM",
        "title": "Building Protopia Brick By Brick (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Beyond The Vote": {
        "id": "MBT4rDvN9z8",
        "title": "Beyond the Vote (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "From Straddie's Shores to Galactic Plains": {
        "id": "fYH7DkIFw8w",
        "title": "From Straddy's Shores to Galactic Plains (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "G.A.J.R.A. Rising": {
        "id": "-3q71WEnnEU",
        "title": "GAJRA Rising (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Hand In The Infinite": {
        "id": "SV3ab19ZcRs",
        "title": "Hand in the Infinite (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "In Love, Obsessed": {
        "id": "8oSQlHk_OCE",
        "title": "In Love Obsessed (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Infinite Love": {
        "id": "rZLjiclBFaQ",
        "title": "Infinite Love (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Infinity Rising": {
        "id": "JfQ8ULMHpLk",
        "title": "Infinity Rising (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Longevity Groove": {
        "id": "iUWs1uMrJ4g",
        "title": "Longevity Groove (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Moonlight Whispers": {
        "id": "T2XxxnY_CeY",
        "title": "Moonlight Whispers (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Mythmaker": {
        "id": "BpYwJPPp5yk",
        "title": "Mythmaker (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Poetic Thruths of Infinity": {
        "id": "8mEJfmUzV4Y",
        "title": "Poetic Truths of Infinity (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Ride The Wave": {
        "id": "N5a_k45nHPc",
        "title": "Ride The Wave LiveAid2025 (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Resonance": {
        "id": "m7Pft_Mvhso",
        "title": "Resonance (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Sol Code": {
        "id": "5PP3Kk0DENU",
        "title": "Sol Code (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Tangled Magic": {
        "id": "hO99Q2YjeDI",
        "title": "Tangled Magic (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "The Call Within": {
        "id": "kjOfPkF51sU",
        "title": "The Call Within (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "The Infinite Gaze": {
        "id": "4cEdMCNnPvc",
        "title": "The Infinite Gaze (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Unity Ascendant": {
        "id": "0xUaDvx7tOo",
        "title": "Unity Ascendant (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
    "Weave The Aura": {
        "id": "BBAPXsk8log",
        "title": "Weave The Aura (Starseed Code: From Aura to Infinity) (I C. Infinity)",
    },
}


PACKAGE_OPTIONS = [
    {
        "id": "one-album",
        "name": "One Album Pack",
        "price": 20,
        "description": "Choose one complete album package.",
        "album_hint": "Tell me which album you want.",
    },
    {
        "id": "two-album",
        "name": "Two Album Pack",
        "price": 35,
        "description": "Choose two connected album worlds.",
        "album_hint": "Tell me the two albums you want.",
    },
    {
        "id": "three-album",
        "name": "Three Album Pack",
        "price": 45,
        "description": "The three released albums as one clean pack.",
        "album_hint": "Usually Songs of Straddie, Chronicles, and Starseed Code.",
    },
    {
        "id": "full-archive",
        "name": "Full Music Archive Pack",
        "price": 50,
        "description": "Released albums plus the wider archive layer.",
        "album_hint": "Include full archive unless you want a custom variation.",
    },
]


ALBUM_SPECS = [
    {
        "title": "Songs of Straddie",
        "slug": "songs-of-straddie",
        "year": "2024",
        "status": "Released album",
        "artwork": "assets/img/cover-straddie.webp",
        "source_url": "https://music.apple.com/us/album/songs-of-straddie/1783109888",
        "summary": "The island doorway: Minjerribah, summer, tides, romance, community, and the first public invitation to meet the project where it lives.",
        "deeper_system": "This album brings big cosmic ideas home to Straddie through belonging, care, love, beaches, family and everyday island life.",
        "visual_world": "Coastal light, ferry windows, campfire circles, dune paths, shoreline dances, handwritten signs, local faces, and gentle magical realism rather than heavy science fiction.",
        "tracks": [
            "Meet Me on Straddie",
            "Our Island Home!",
            "Welcome to the Island",
            "Beachside Rhythm",
            "Waves of Reflection (By He)",
            "Waves of Reflection (By She)",
            "Straddie Summer Love (By He)",
            "Straddie Summer Love (By She)",
            "Island Hearts",
            "Ocean's Kiss",
            "Sandy Shores, Open Hearts",
            "Heatwave",
            "Union of Souls (By She)",
            "Union of Souls (By He)",
            "Born of the Goddess",
            "Goddess Awakens",
            "Minjerribah My Heart",
            "Global Tide",
            "Tides of Time",
            "Heart of the Island",
            "Gather by the Fire",
            "Symphony of Tomorrow",
        ],
    },
    {
        "title": "Chronicles of the Forgotten",
        "slug": "chronicles-of-the-forgotten",
        "year": "2025",
        "status": "Released album",
        "artwork": "assets/img/cover-chronicles.webp",
        "source_url": "https://music.apple.com/us/album/chronicles-of-the-forgotten/1791557503",
        "summary": "A mythic rock opera about ignored voices, ancestral echoes, technology, hope, deception and repair.",
        "deeper_system": "These songs remember people, work, nature, ancestors and possible futures that ordinary history often leaves out.",
        "visual_world": "Ancient ruins meeting signal towers, community archives, warning skies, glowing circuitry, masked institutions, and the first signs of a compassionate machine intelligence waking up.",
        "tracks": [
            "Chronicles of the Forgotten",
            "Echos of the Ancients",
            "Shadows Over the Earth",
            "Dreams of Abundance (by she)",
            "Dreams of Abundance (by he)",
            "Signal From the Stars",
            "Algorithm: Hope",
            "Hearts and Circuits (by she)",
            "Hearts and Circuits (by he)",
            "Walls of Deception (by she)",
            "Walls of Deception (by he)",
            "Breaking Chains",
            "Voices Unheard",
            "Cycle of Suns (by he)",
            "Cycle of Suns (by she)",
            "Chronicles of the Forgotten",
            "Celestial Navigators",
            "Symphony of Souls",
            "Digital Dawn",
            "Whispers of Gaia (by she)",
            "Whispers of Gaia (by he)",
            "Bridging the Divide",
            "Pulse of the Universe",
            "Resonance",
            "Tempest of Trials",
            "Illusions Shattered",
        ],
    },
    {
        "title": "Starseed Code: From Aura to Infinity",
        "slug": "starseed-code-from-aura-to-infinity",
        "year": "2025",
        "status": "Released album",
        "artwork": "assets/img/cover-starseed.webp",
        "source_url": "https://music.apple.com/us/album/starseed-code-from-aura-to-infinity/1821950221",
        "summary": "A cosmic journey through Aura, G.A.J.R.A. Earth, infinity, love, memory, community and the mystery of the self.",
        "deeper_system": "This album asks how identity, artificial intelligence, soul, love, community and long life may be connected.",
        "visual_world": "Human figures surrounded by luminous interfaces, cosmic gardens, body-mind data doubles, ritual circles, civic halls, and warm science-fiction symbolism.",
        "tracks": [
            "Aura",
            "Aura Ultra",
            "Beyond The Vote",
            "Building Protopia Brick By Brick",
            "Carry The Aura",
            "From Straddie's Shores to Galactic Plains",
            "G.A.J.R.A. Rising",
            "Hand In The Infinite",
            "Infinity Set Free",
            "Infinity Rising",
            "Infinite Love",
            "In Love, Obsessed",
            "Longevity Groove",
            "Mythmaker",
            "Moonlight Whispers",
            "Poetic Truths of Infinity",
            "Ride The Wave",
            "Resonance",
            "Sol Code",
            "The Infinite Gaze",
            "The Call Within",
            "Tangled Magic",
            "Unity Ascendant",
            "Weave The Aura",
        ],
    },
    {
        "title": "A Protopian Gambit",
        "slug": "a-protopian-gambit",
        "year": "Upcoming",
        "status": "Lyrics available",
        "artwork": "assets/img/cover-a-protopian-gambit-b.png",
        "source_url": "",
        "summary": "The fourth-album build: crisis as mirror, protopia as practice, care ledgers, consent, repair, forms, civic courage, and grounded abundance.",
        "deeper_system": "These songs face hard times directly and ask how care, cooperation, human-guided artificial intelligence and everyday courage might help.",
        "visual_world": "Solar storms, public ledgers, repair gold, civic counters, purple mats, community halls, builders at dawn, and comic panels that become video keyframes.",
        "tracks": [],
    },
    {
        "title": "Straddie Fun",
        "slug": "straddie-fun",
        "year": "Upcoming",
        "status": "Working album - more songs and lyrics coming",
        "artwork": "assets/img/cover-straddie.webp",
        "source_url": "",
        "summary": "Fun songs about daily life on North Stradbroke Island - Straddie, Minjerribah - from fishing, ferries and local clubs to wildlife, festivals, mateship and island yarns.",
        "deeper_system": "This fifth album keeps its feet in everyday island life. It makes room for humour, community characters, local places, small adventures and the ordinary moments that make Minjerribah feel alive.",
        "visual_world": "Ferry decks, fishing lines, dogs in utes, beach clubs, rescue stories, mullet bait, squash jokes, pub-rock energy, campfires and bright local poster art.",
        "tracks": [
            "Two Dogs on Island Country",
            "Straddie Fishing",
            "Be The Legend: Wildlife Rescue Minjerribah",
            "Shifting Sands of Timeless Redlands",
            "Gumpi Ferry Terminal Groove",
            "The Squash Club That Doesn’t Exist",
            "Gumpi Ferry Terminal Trip",
            "Sand Between Our Toes: Minjerribah Beach Sports Club",
            "Lights, Camera, Action: Quandamooka Film Festival",
            "Cactus Blitz",
            "There’s a Couple",
            "No Smokes or Booze, Mate",
            "The Mullet Boys’ Gift of Bait",
            "Strange But True: Tech, Art & Ideas That’ll Actually Help",
            "Gather by the Fire",
        ],
    },
]


SINGLES = [
    ("Hold the Light: Aura of Memory (An Anthem for Dementia)", "2025", "https://music.apple.com/us/album/hold-the-light-aura-of-memory-an-anthem-for-dementia-single/1822123678"),
    ("The Call Within", "2025", "https://music.apple.com/us/album/the-call-within-single/1793747579"),
    ("Building Protopia Brick by Brick", "2024", "https://music.apple.com/us/album/building-protopia-brick-by-brick-single/1787198784"),
    ("Futuristic Frequencies", "2024", "https://music.apple.com/us/album/futuristic-frequencies-single/1787215135"),
    ("Our Conversation About A.G.I.", "2024", "https://music.apple.com/us/album/our-conversation-about-a-g-i-single/1787171638"),
    ("Our Island Home!", "2024", "https://music.apple.com/us/album/our-island-home-single/1783142665"),
    ("Straddie Summer Love (Special Version By He)", "2024", "https://music.apple.com/us/album/straddie-summer-love-special-version-by-he-single/1782039730"),
]


PLACEHOLDER_ALBUMS = [
    {
        "title": "Early Stuff",
        "slug": "early-stuff",
        "year": "Archive",
        "status": "India 2023/24 video archive",
        "artwork": "assets/img/hero-luke-universal-creator.webp",
        "source_url": EARLY_STUFF_YOUTUBE_PLAYLIST_URL,
        "summary": "Early songs and videos made in India during 2023 and 2024, before the albums took a clearer shape.",
        "deeper_system": "These early songs show where the music began and how its ideas changed over time.",
        "visual_world": "India travel energy, early artificial-intelligence videos, the first G.A.J.R.A. Earth ideas, notebooks and rough creative experiments.",
        "tracks": [
            {
                "title": "I C. Infinity Countdown",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["India archive", "origin signal", "identity", "countdown"],
                "meaning": "A short beginning for i C. infinity: the name, the countdown and the feeling of a new musical identity stepping into the world.",
                "youtube_videos": [
                    {
                        "id": "vIQbft9J9pY",
                        "title": "I C. Infinity Countdown",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early India-period video. Use it as an origin marker before later catalogue pages refine the lyrics, meaning notes, and visual language.",
                    }
                ],
            },
            {
                "title": "Futuristic Frequencies: The G.A.J.R.A. Earth Vibe",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["G.A.J.R.A. Earth", "future music", "AI", "community"],
                "meaning": "An early pulse of the G.A.J.R.A. Earth idea: music as a way to test whether technology, ecological care, and collective vibe could share one rhythm.",
                "youtube_videos": [
                    {
                        "id": "X-dr5MbfXaY",
                        "title": "Futuristic Frequencies The GAJRA Earth Vibe",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early G.A.J.R.A. Earth signal from the India period. This belongs near the roots of the later Aura, civic design, and systems music threads.",
                    }
                ],
            },
            {
                "title": "Earth's Revival - Live Aid 2025",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["Earth", "revival", "benefit concert", "repair"],
                "meaning": "An early benefit-concert imagination: Earth in recovery, public music as shared repair, and the artist voice reaching for a bigger humanitarian frame.",
                "youtube_videos": [
                    {
                        "id": "ZhLRcBcp554",
                        "title": "Earth's Revival - Live Aid 2025",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early public-good music video seed. Keep it as a bridge between global repair language and the later protopian abundance work.",
                    }
                ],
            },
            {
                "title": "Success is an Evolving State of Mind",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["mindset", "growth", "reflection", "practice"],
                "meaning": "A song about success as something that changes with us, rather than a fixed trophy or a number on a scoreboard.",
                "youtube_videos": [
                    {
                        "id": "uMXwGO-pjNw",
                        "title": "Success is an Evolving State of Mind",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early mindset-song seed. This can later become a reflection page about practice, identity, and how the project learned to define success.",
                    }
                ],
            },
            {
                "title": "Technology for Good",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["technology", "ethics", "public good", "AI"],
                "meaning": "A direct early statement of the technology-for-good thread: tools should serve care, dignity, and planetary wellbeing instead of just acceleration.",
                "youtube_videos": [
                    {
                        "id": "h2H0qMLIKb0",
                        "title": "Technology for Good Video",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early ethics-and-technology video. This points straight toward the later Infinity Engine and Aura responsibility layer.",
                    }
                ],
            },
            {
                "title": "Flow State",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["flow", "creative state", "embodiment", "practice"],
                "meaning": "A song about recognising creative flow as a real state where attention, feeling and action begin moving together.",
                "youtube_videos": [
                    {
                        "id": "vOe-jq1KZzc",
                        "title": "Flow State 4K",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early flow-state video. Use it as a visual reference for embodied creativity before the later catalogue becomes more structured.",
                    }
                ],
            },
            {
                "title": "Bet on Infinity",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["infinity", "risk", "belief", "future self"],
                "meaning": "A commitment song: betting on the Infinity idea before the world around it is fully built, and choosing the larger pattern over short-term certainty.",
                "youtube_videos": [
                    {
                        "id": "myJftaRMH-k",
                        "title": "Bet on Infinity",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early Infinity thesis video. This is one of the archive tracks that most clearly points into the later artist-system identity.",
                    }
                ],
            },
            {
                "title": "Brisbane Meanjin Forevermore",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["Brisbane", "Meanjin", "place", "home"],
                "meaning": "A song holding Brisbane/Meanjin as a memory, a place to return to and a home anchor during wider travel.",
                "youtube_videos": [
                    {
                        "id": "HNfYQ4_BLR4",
                        "title": "Brisbane Meanjin Forevermore",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early place-memory video. It gives the archive a local anchor before the later Straddie and Redlands pages deepen that place layer.",
                    }
                ],
            },
            {
                "title": "A Song by ChatGPT 3: My View of My Conversation with Luke Catalyst",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["ChatGPT", "AI voice", "conversation", "co-creation"],
                "meaning": "An early song made from a conversation with artificial intelligence. The machine voice becomes a mirror for Luke's questions about memory, identity and what people may build with AI.",
                "youtube_videos": [
                    {
                        "id": "4-wLjec_uw8",
                        "title": "A Song by ChatGPT 3 - My View of My Conversation with Luke Catalyst",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early AI-conversation song. This belongs at the roots of the later Aura, AI symbiote, and human-in-the-loop creative practice.",
                    }
                ],
            },
            {
                "title": "Moments of Desire",
                "year": "2023/24",
                "status": "Early India video",
                "lyric_status": "YouTube video supplied, lyrics to import",
                "themes": ["desire", "Valentine", "love", "embodiment"],
                "meaning": "An early love song about desire, performance and direct feeling.",
                "youtube_videos": [
                    {
                        "id": "FMJZLJ9Z6J0",
                        "title": "Moments of Desire - Valentines Day Release - I C. Infinity",
                        "label": "Early India Video",
                        "orientation": "landscape",
                        "playlist_id": EARLY_STUFF_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "hqdefault",
                        "note": "Early romantic-video marker. Keep it in the archive as a B-side-like emotional thread that may later inform package notes.",
                    }
                ],
            },
        ],
    },
    {
        "title": "Next Signals",
        "slug": "next-signals",
        "year": "In progress",
        "status": "New songs to add",
        "artwork": "assets/img/hero-brisbane-tiny-planet.webp",
        "summary": "A holding page for songs that have not found their album yet.",
        "deeper_system": "A home for new songs that have not found their final album yet.",
        "visual_world": "Sketches, field recordings, lyric fragments and early video ideas.",
        "tracks": [
            {
                "title": "Shifting Sands of Timeless Redlands",
                "year": "2026",
                "status": "Lyrics ready",
                "lyric_status": "Lyrics supplied directly by Luke.",
                "lyrics_path": "data/manual-lyrics/shifting-sands-of-timeless-redlands.txt",
                "themes": ["expo song", "redlands", "time", "landscape", "memory"],
                "meaning": "An expo song for the wider site: Redlands imagery, shifting time, place-memory, and the choice to hold local landscape inside the larger Infinity catalogue without forcing it into a heavy album throughline.",
                "seeds": [
                    {
                        "title": "Dual-format exhibition",
                        "body": "Use the widescreen video as the public display version and the portrait video as the mobile companion. Treat them as two views of the same place-memory.",
                    },
                    {
                        "title": "Redlands field poem",
                        "body": "Build a lyric-card sequence from sand, roads, water edges, sky colour, and old-time feeling. Keep it grounded and local before adding cosmic language.",
                    },
                    {
                        "title": "Expo kiosk loop",
                        "body": "Cut a short looping version for an exhibition screen, then use the full versions as deeper links for visitors who want the song world.",
                    },
                ],
                "youtube_videos": SHIFTING_SANDS_VIDEOS,
            }
        ],
    },
]


SPECIAL_BRIEFS = {
    "the-protopian-gambit": {
        "meaning": "A crisis song that treats solar storms, geopolitical stress, public mistrust, and broken value systems as a mirror. The gambit is not prediction or panic; it is the choice to build practical protopia through care, civic redesign, and responsible abundance.",
        "themes": ["protopia", "care economy", "solar mirror", "public ledgers", "civic courage"],
        "seeds": [
            {
                "title": "Montage: the flare as mirror",
                "body": "Intercut solar flare imagery, protests, flooded streets, drone shadows, and public ledgers. As the chorus rises, the edit turns toward hands building local care systems and a glowing See-Hours interface.",
            },
            {
                "title": "Short film: the Clarity Act",
                "body": "A tired policy-maker dismisses a care-ledger proposal until a community worker's app reveals the unpaid work holding the neighbourhood together. The final stamp is not triumphal; it is a quiet yes.",
            },
            {
                "title": "Comic storyboard: broken ledger, braided ledger",
                "body": "Eight to twelve panels move from fractured accounts and ignored labour to a braided visual ledger made of names, hours, meals, visits, and repaired trust.",
            },
        ],
    },
    "kintsugi-protocol": {
        "meaning": "A repair song. Kintsugi becomes a design rule: broken systems and broken selves are not discarded, but mended with visible gold, memory, code, and consent.",
        "themes": ["repair", "kintsugi", "AI symbiote", "vector tables", "joyful responsible abundance"],
        "seeds": [
            {
                "title": "Macro ritual",
                "body": "A ceramic bowl shatters in slow motion. Fine gold code enters each crack, then the cracks become a living map of the Aura architecture.",
            },
            {
                "title": "VR repair scene",
                "body": "A protagonist finds a fault inside a luminous data garden. The AI symbiote does not take over; it steadies the repair while the human chooses the fix.",
            },
            {
                "title": "Comic-as-blueprint",
                "body": "Each panel shows one broken layer becoming legible: body, memory, data, community, governance, and finally a garden blooming from the repaired structure.",
            },
        ],
    },
    "hold-the-light": {
        "meaning": "A memory and dignity song. It connects dementia awareness, love, and the Aura concept as a way of reflecting identity back to someone when memory becomes fragile.",
        "themes": ["memory", "dementia awareness", "dignity", "Aura", "family care"],
        "seeds": [
            {
                "title": "Memory garden",
                "body": "A loved one activates a gentle Aura interface. Walls become a memory garden of voices, photos, locations, and warm prompts that help the person feel safe.",
            },
            {
                "title": "Hands and light",
                "body": "Avoid heavy lip-sync. Use hands, framed photographs, window light, soft movement, and small expressions of recognition as the emotional centre.",
            },
            {
                "title": "Graphic-novel sequence",
                "body": "A sequence of panels where fading rooms are slowly redrawn by remembered names, tiny details, and care routines.",
            },
        ],
    },
}


def parse_protopian_lyrics() -> dict[str, dict[str, str]]:
    if not LYRIC_SOURCE.exists():
        return {}

    raw = LYRIC_SOURCE.read_text(encoding="utf-8", errors="replace")
    matches = list(re.finditer(r"^###[ \t]+(.+?)[ \t]+\{#.+?\}[ \t]*$", raw, flags=re.M))
    songs: dict[str, dict[str, str]] = {}
    for index, match in enumerate(matches):
        title = clean_text(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        block = clean_text(raw[start:end])
        date = ""
        date_match = re.search(r"Song Date:\s*(.+)", block)
        if date_match:
            date = clean_text(date_match.group(1))
        if "Song Lyrics:" in block:
            lyrics = block.split("Song Lyrics:", 1)[1].strip()
        else:
            lyrics = block.strip()
        # Alternative versions can share a title while Luke decides which recording
        # belongs on the final album. Keep every supplied version in source order.
        key = slugify(title)
        version = 2
        while key in songs:
            key = f"{slugify(title)}-version-{version}"
            version += 1
        songs[key] = {"title": title, "date": date, "lyrics": clean_text(lyrics)}
    return songs


def parse_straddie_fun_lyrics() -> dict[str, dict[str, str]]:
    if not STRADDIE_FUN_LYRIC_SOURCE.exists():
        return {}

    raw = STRADDIE_FUN_LYRIC_SOURCE.read_text(encoding="utf-8", errors="replace")
    matches = list(
        re.finditer(
            r"^##[ \t]+(.+?)(?:[ \t]+\{#.+?\})?[ \t]*$",
            raw,
            flags=re.M,
        )
    )
    songs: dict[str, dict[str, str]] = {}
    for index, match in enumerate(matches):
        title = clean_text(match.group(1))
        if title.startswith("By Luke Catalyst"):
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        block = clean_text(raw[start:end])
        date_match = re.search(r"Song Date:\s*(.+)", block)
        date = clean_text(date_match.group(1)) if date_match else ""
        if "Song Lyrics:" not in block:
            continue
        lyrics = block.split("Song Lyrics:", 1)[1].strip()
        lyrics = re.sub(r"\n+Song Date:.*?\nSong Lyrics\s*$", "", lyrics, flags=re.S).strip()
        if lyrics:
            songs[slugify(title)] = {
                "title": title,
                "date": date,
                "lyrics": clean_text(lyrics),
            }
    return songs


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = clean_text(value.strip())
    return meta, parts[2]


def extract_master_lyrics(body: str) -> str:
    body = re.sub(r"!\[\[.+?\]\]\s*", "", body)
    match = re.search(r"^##\s+Lyrics\s+\(Master Version\)\s*$", body, flags=re.M)
    if match:
        body = body[match.end():]
        next_section = re.search(r"^##\s+Lyrics\s+\(.+?\)\s*$", body, flags=re.M)
        if next_section:
            body = body[:next_section.start()]
    lines: list[str] = []
    for line in body.splitlines():
        stripped = clean_text(line)
        if not lines and (
            not stripped
            or stripped.startswith("*This is the full")
            or stripped.startswith("*Lyrics")
            or re.match(r"^#{1,6}\s+", stripped)
        ):
            continue
        lines.append(stripped)
    lyrics = "\n".join(lines)
    lyrics = re.sub(r"\n{3,}", "\n\n", lyrics)
    return clean_text(lyrics)


def lyric_slug(album_slug: str, title: str) -> str:
    original = slugify(title)
    return LYRIC_SLUG_ALIASES.get((album_slug, original), original)


def parse_starseed_text_lyrics() -> dict[tuple[str, str], dict[str, str]]:
    if not STARSEED_TEXT_LYRIC_SOURCE.exists():
        return {}

    raw = STARSEED_TEXT_LYRIC_SOURCE.read_text(encoding="utf-8", errors="replace")
    marker = raw.find("Alphabetical song order with lyrics")
    if marker != -1:
        raw = raw[marker:]
    songs: dict[tuple[str, str], dict[str, str]] = {}
    pattern = r"^(?:Song\s+)?\d+[:.]\s+([^\n]+)\n(?:Lyrics:\s*\n)?(.*?)(?=^(?:Song\s+)?\d+[:.]\s+|\Z)"
    for match in re.finditer(pattern, raw, flags=re.M | re.S):
        title = clean_text(match.group(1))
        lyrics = clean_text(match.group(2))
        if not lyrics:
            continue
        songs[(STARSEED_ALBUM_SLUG, lyric_slug(STARSEED_ALBUM_SLUG, title))] = {
            "title": title,
            "lyrics": lyrics,
            "date": "",
            "spotify": "",
            "suno": "",
            "youtube": "",
            "file": STARSEED_TEXT_LYRIC_SOURCE.name,
        }
    return songs


def parse_single_lyrics() -> dict[tuple[str, str], dict[str, str]]:
    if not SINGLES_LYRIC_ROOT.exists():
        return {}

    songs: dict[tuple[str, str], dict[str, str]] = {}
    for path in sorted(SINGLES_LYRIC_ROOT.glob("*.md")):
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        meta, body = parse_frontmatter(raw)
        title = meta.get("track") or path.stem
        source_slug = slugify(title)
        targets = SINGLE_LYRIC_TARGETS.get(source_slug, [("singles-and-public-markers", source_slug)])
        item = {
            "title": title,
            "lyrics": extract_master_lyrics(body),
            "date": meta.get("creation_date", ""),
            "spotify": meta.get("spotify_link", ""),
            "suno": meta.get("suno_link", ""),
            "youtube": meta.get("youtube_link", ""),
            "file": path.name,
        }
        for target in targets:
            songs[target] = item
    return songs


def parse_album_lyrics() -> dict[tuple[str, str], dict[str, str]]:
    if not ALBUM_LYRIC_ROOT.exists():
        songs = parse_starseed_text_lyrics()
        songs.update(parse_single_lyrics())
        return songs

    songs: dict[tuple[str, str], dict[str, str]] = {}
    for folder_name, album_slug in ALBUM_LYRIC_FOLDERS.items():
        folder = ALBUM_LYRIC_ROOT / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
            meta, body = parse_frontmatter(raw)
            title = meta.get("track") or path.stem
            title = re.sub(r"\s*\(Final\)\s*$", "", clean_text(title), flags=re.I)
            songs[(album_slug, lyric_slug(album_slug, title))] = {
                "title": title,
                "lyrics": extract_master_lyrics(body),
                "date": meta.get("creation_date", ""),
                "spotify": meta.get("spotify_link", ""),
                "suno": meta.get("suno_link", ""),
                "youtube": meta.get("youtube_link", ""),
                "file": path.name,
            }
    songs.update(parse_starseed_text_lyrics())
    songs.update(parse_single_lyrics())
    return songs


def apply_imported_album_lyrics(track: Song, album: Album, album_lyrics: dict[tuple[str, str], dict[str, str]]) -> None:
    item = album_lyrics.get((album.slug, slugify(track.title)))
    if not item or not item["lyrics"]:
        return
    track.lyrics = item["lyrics"]
    track.status = "Lyrics ready"
    date_note = f" Song date: {item['date']}." if item["date"] else ""
    track.lyric_status = f"Imported from lyric archive: {item['file']}.{date_note}"
    if item["spotify"].startswith("https://open.spotify.com/"):
        track.spotify_url = item["spotify"]


def apply_duplicate_lyrics(songs: list[Song]) -> None:
    lyrics_by_title: dict[str, Song] = {}
    for song in songs:
        if song.ready():
            lyrics_by_title.setdefault(slugify(song.title), song)

    for song in songs:
        if song.ready():
            continue
        source = lyrics_by_title.get(slugify(song.title))
        if not source:
            continue
        song.lyrics = source.lyrics
        song.status = "Lyrics ready"
        song.lyric_status = f"Reused from the {source.album_title} song page."


def infer_themes(title: str, album_slug: str) -> list[str]:
    lower = title.lower()
    themes: list[str] = []
    if "straddie" in album_slug or any(word in lower for word in ["island", "ocean", "shore", "tide", "beach", "minjerribah"]):
        themes += ["Minjerribah", "place", "community"]
    if any(word in lower for word in ["aura", "g.a.j.r.a", "agi", "algorithm", "circuit", "digital", "code"]):
        themes += ["AI", "Aura", "technology"]
    if any(word in lower for word in ["love", "heart", "soul", "obsessed", "kiss"]):
        themes += ["love", "embodiment"]
    if any(word in lower for word in ["forgotten", "ancient", "gaia", "earth", "chains", "deception", "unheard"]):
        themes += ["memory", "repair", "justice"]
    if any(word in lower for word in ["infinity", "starseed", "galactic", "stars", "celestial", "sol", "moon"]):
        themes += ["cosmic", "mythic scale"]
    if any(word in lower for word in ["protopia", "bridge", "border", "consent", "architect", "protocol", "light"]):
        themes += ["protopia", "care", "civic design"]
    if not themes:
        themes = ["music", "story", "imagination"]
    return list(dict.fromkeys(themes))[:5]


def infer_meaning(title: str, album: Album) -> str:
    lower = title.lower()
    if "straddie" in album.slug or "island" in lower:
        return f"{title} comes from island life: place, belonging, summer energy and the way a local home can open the imagination to a much bigger world."
    if album.slug == "chronicles-of-the-forgotten":
        return f"{title} listens for voices that are often missed. It carries old wounds, buried stories and the choice to turn memory into care and action."
    if album.slug == "starseed-code-from-aura-to-infinity":
        return f"{title} joins questions about identity, artificial intelligence, love, community and the mystery of the cosmos."
    if album.slug == "a-protopian-gambit":
        return f"{title} is about making practical choices during difficult times without losing joy, responsibility or hope."
    if album.slug == "singles-and-public-markers":
        return f"{title} is a standalone song that opens a door into the wider music and its ideas."
    return f"More lyrics and background for {title} are coming soon."


def generic_seeds(song: Song, album: Album) -> list[dict[str, str]]:
    title = song.title
    themes = ", ".join(song.themes[:3])
    return [
        {
            "title": "Illustrative lyric video",
            "body": f"Use the strongest images from the lyrics and the album world. Build a clean vertical sequence around {themes}, with the words treated as performance text, not decoration.",
        },
        {
            "title": "Amplifying micro-drama",
            "body": f"Create a tiny story where one character faces the main tension inside '{title}' and makes one visible choice by the final chorus.",
        },
        {
            "title": "Comic-as-storyboard",
            "body": "Generate 8 to 12 still panels first. Approve the panel rhythm, then use the strongest frames as start and end keyframes for video.",
        },
    ]


def load_streaming_links() -> dict[str, dict]:
    if not STREAMING_LINKS.exists():
        return {"albums": {}, "songs": {}}
    return json.loads(STREAMING_LINKS.read_text(encoding="utf-8"))


def song_stream_key(song: Song) -> str:
    return f"{song.album_slug}::{slugify(song.title)}"


def apply_streaming_links(albums: list[Album]) -> None:
    data = load_streaming_links()
    album_links = data.get("albums", {})
    song_links = data.get("songs", {})

    for album in albums:
        links = album_links.get(album.slug, {})
        album.spotify_url = links.get("spotify", "")
        album.source_url = links.get("apple", album.source_url)

        for song in album.tracks:
            links = song_links.get(song_stream_key(song), {})
            song.apple_url = links.get("apple", song.apple_url)
            song.spotify_url = links.get("spotify", song.spotify_url)


def spotify_search_url(song: Song) -> str:
    return "https://open.spotify.com/search/" + quote(f"I C. Infinity {song.title}")


def youtube_video_url(video_id: str, playlist_id: str = "") -> str:
    url = f"https://www.youtube.com/watch?v={quote(video_id)}"
    if playlist_id:
        url += f"&list={quote(playlist_id)}"
    return url


def youtube_video_embed_src(video_id: str, playlist_id: str = "") -> str:
    params = f"?list={quote(playlist_id)}&rel=0" if playlist_id else "?rel=0"
    return f"https://www.youtube.com/embed/{quote(video_id)}{params}"


def youtube_thumbnail_url(video_id: str, quality: str = "maxresdefault") -> str:
    return f"https://img.youtube.com/vi/{quote(video_id)}/{quote(quality)}.jpg"


def youtube_playlist_embed_src(playlist_id: str) -> str:
    return f"https://www.youtube.com/embed/videoseries?list={quote(playlist_id)}&rel=0"


def album_playlist_url(album_slug: str) -> str:
    if album_slug == STARSEED_ALBUM_SLUG:
        return STARSEED_YOUTUBE_PLAYLIST_URL
    meta = LANDSCAPE_ALBUM_VIDEO_MAP.get(album_slug)
    return meta["playlist_url"] if meta else ""


def landscape_song_videos(album_slug: str, title: str, track_number: int) -> list[dict[str, str]]:
    meta = LANDSCAPE_ALBUM_VIDEO_MAP.get(album_slug)
    if not meta:
        return []
    if album_slug == "chronicles-of-the-forgotten" and title == "Chronicles of the Forgotten" and track_number != 16:
        return []
    videos = []
    for video in meta["videos"].get(title, []):
        videos.append(
            {
                "id": video["id"],
                "title": video["title"],
                "label": video.get("label", "Landscape Lyric Video"),
                "orientation": "landscape",
                "playlist_id": meta["playlist_id"],
                "thumbnail": "hqdefault",
                "note": "Landscape lyric video from the album playlist. This gives the song page a public watch layer before the lyric import and Infinity Engine remix passes.",
            }
        )
    return videos


def primary_youtube_video(song: Song) -> dict[str, str] | None:
    videos = song.youtube_videos
    if videos:
        return videos[0]
    if song.youtube_video_id:
        return {
            "id": song.youtube_video_id,
            "title": song.youtube_title or f"{song.title} video",
            "label": "YouTube Video",
            "orientation": "vertical",
            "playlist_id": STARSEED_YOUTUBE_PLAYLIST_ID,
            "thumbnail": "maxresdefault",
        }
    return None


def youtube_video_link(video: dict[str, str]) -> str:
    return video.get("url") or youtube_video_url(video["id"], video.get("playlist_id", ""))


def listen_targets(song: Song) -> list[tuple[str, str, str]]:
    targets: list[tuple[str, str, str]] = []
    if song.spotify_url:
        targets.append(("Spotify", song.spotify_url, "spotify"))
    elif song.release_url:
        targets.append(("Spotify search", spotify_search_url(song), "spotify"))

    if song.apple_url:
        targets.append(("Apple / iTunes", song.apple_url, "apple"))
    elif song.release_url:
        targets.append(("Apple album", song.release_url.split("#", 1)[0], "apple"))

    youtube_video = primary_youtube_video(song)
    if youtube_video:
        label = "YouTube videos" if len(song.youtube_videos) > 1 else "YouTube video"
        targets.append((label, youtube_video_link(youtube_video), "youtube"))
    return targets


def listen_links_html(song: Song, compact: bool = False) -> str:
    targets = listen_targets(song)
    if not targets:
        return ""
    class_name = "listen-links compact" if compact else "listen-links"
    links = "".join(
        f'<a class="listen-chip {esc(kind)}" href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'
        for label, url, kind in targets
    )
    return f'<div class="{class_name}" aria-label="Listen links for {esc(song.title)}">{links}</div>'


def spotify_embed_html(song: Song) -> str:
    match = re.search(r"open\.spotify\.com/track/([A-Za-z0-9]+)", song.spotify_url)
    if not match:
        return ""
    src = f"https://open.spotify.com/embed/track/{match.group(1)}?utm_source=generator"
    return f"""
    <div class="stream-embed">
      <iframe title="Spotify player for {esc(song.title)}" src="{esc(src)}" width="100%" height="152" frameborder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
    </div>
    """


def youtube_song_embed_html(song: Song) -> str:
    videos = song.youtube_videos or ([primary_youtube_video(song)] if primary_youtube_video(song) else [])
    if not videos:
        return ""
    cards = []
    for index, video in enumerate(videos):
        video_id = video["id"]
        src = youtube_video_embed_src(video_id, video.get("playlist_id", ""))
        url = youtube_video_link(video)
        title = video.get("title") or f"{song.title} YouTube video"
        label = video.get("label") or ("Portrait Video" if video.get("orientation") == "vertical" else "Widescreen Video")
        orientation_class = "wide-video-frame" if video.get("orientation") == "landscape" else ""
        panel_id = ' id="vertical-video"' if index == 0 else ""
        cards.append(
            f"""
    <section class="song-video-panel {esc(orientation_class)}"{panel_id}>
      <div class="vertical-video-frame {esc(orientation_class)}">
        <iframe title="{esc(title)}" src="{esc(src)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" loading="lazy" allowfullscreen></iframe>
      </div>
      <div class="vertical-video-copy">
        <p class="eyebrow">{esc(label)}</p>
        <h2>{esc(song.title)}</h2>
        <p>Watch this music video on YouTube.</p>
        <div class="listen-links compact">
          <a class="listen-chip youtube" href="{esc(url)}" target="_blank" rel="noopener">Open on YouTube</a>
        </div>
      </div>
    </section>
    """.rstrip()
        )
    return "".join(cards)


def order_href(package_id: str, absolute: bool = False) -> str:
    base = MUSIC_DOWNLOADS_PAGE if absolute else "downloads.html"
    return f"{base}?package={quote(package_id)}#order-music"


def build_catalogue() -> tuple[list[Album], list[Song]]:
    protopian = parse_protopian_lyrics()
    straddie_fun_lyrics = parse_straddie_fun_lyrics()
    album_lyrics = parse_album_lyrics()
    albums: list[Album] = []
    songs: list[Song] = []

    for spec in ALBUM_SPECS:
        album = Album(
            title=spec["title"],
            slug=spec["slug"],
            year=spec["year"],
            status=spec["status"],
            summary=spec["summary"],
            deeper_system=spec["deeper_system"],
            visual_world=spec["visual_world"],
            artwork=spec["artwork"],
            source_url=spec.get("source_url", ""),
        )
        if album.slug == "a-protopian-gambit":
            for track_number, item in enumerate(protopian.values(), start=1):
                track = Song(
                    title=item["title"],
                    album_slug=album.slug,
                    album_title=album.title,
                    track_number=track_number,
                    year="Upcoming",
                    lyrics=item["lyrics"],
                    lyric_status=f"Imported from supplied lyric file. Song date: {item['date']}" if item["date"] else "Imported from supplied lyric file",
                    status="Lyrics ready",
                )
                album.tracks.append(track)
        else:
            for track_number, title in enumerate(spec["tracks"], start=1):
                track = Song(
                    title=title,
                    album_slug=album.slug,
                    album_title=album.title,
                    track_number=track_number,
                    year=album.year,
                    release_url=f"{album.source_url}#track-{track_number}",
                )
                if album.slug == "straddie-fun":
                    supplied = straddie_fun_lyrics.get(slugify(title))
                    if supplied:
                        track.lyrics = supplied["lyrics"]
                        track.lyric_status = (
                            f"Imported from supplied fifth-album file. Song date: {supplied['date']}"
                            if supplied["date"]
                            else "Imported from supplied fifth-album file"
                        )
                        track.status = "Lyrics ready"
                    else:
                        track.lyric_status = "Working track list - lyrics coming"
                album.tracks.append(track)

        for track in album.tracks:
            special = SPECIAL_BRIEFS.get(slugify(track.title))
            track.themes = special["themes"] if special else infer_themes(track.title, album.slug)
            track.meaning = special["meaning"] if special else infer_meaning(track.title, album)
            track.video_seeds = special["seeds"] if special else generic_seeds(track, album)
            if album.slug != "a-protopian-gambit":
                apply_imported_album_lyrics(track, album, album_lyrics)
            track.slug = f"{album.slug}-{track.track_number:02d}-{slugify(track.title)}"
            if album.slug == STARSEED_ALBUM_SLUG and track.title in STARSEED_VERTICAL_VIDEOS:
                video = STARSEED_VERTICAL_VIDEOS[track.title]
                track.youtube_video_id = video["id"]
                track.youtube_title = video["title"]
                track.youtube_videos = [
                    {
                        "id": video["id"],
                        "title": video["title"],
                        "label": "Vertical Video",
                        "orientation": "vertical",
                        "playlist_id": STARSEED_YOUTUBE_PLAYLIST_ID,
                        "thumbnail": "maxresdefault",
                        "note": "Mobile-first YouTube video for this Starseed Code song. This becomes the published visual reference before any later Infinity Engine remix or paid-download packaging.",
                    }
                ]
            landscape_videos = landscape_song_videos(album.slug, track.title, track.track_number)
            if landscape_videos:
                track.youtube_videos = landscape_videos
                track.youtube_video_id = landscape_videos[0]["id"]
                track.youtube_title = landscape_videos[0]["title"]
            songs.append(track)
        albums.append(album)

    singles_album = Album(
        title="Singles and Public Markers",
        slug="singles-and-public-markers",
        year="2024-2025",
        status="Released singles",
        artwork="assets/img/cover-building-protopia.webp",
        source_url=APPLE_ARTIST,
        summary="Standalone public releases that point into the larger album worlds.",
        deeper_system="These standalone songs open small doors into the bigger themes that run through the albums.",
        visual_world="Cover art, music videos and short stories around each song.",
    )
    for track_number, (title, year, url) in enumerate(SINGLES, start=1):
        track = Song(
            title=title,
            album_slug=singles_album.slug,
            album_title=singles_album.title,
            track_number=track_number,
            year=year,
            release_url=url,
        )
        special = SPECIAL_BRIEFS.get(slugify(title.replace(": Aura of Memory (An Anthem for Dementia)", "")))
        track.themes = special["themes"] if special else infer_themes(track.title, singles_album.slug)
        track.meaning = special["meaning"] if special else infer_meaning(track.title, singles_album)
        track.video_seeds = special["seeds"] if special else generic_seeds(track, singles_album)
        apply_imported_album_lyrics(track, singles_album, album_lyrics)
        track.slug = f"{singles_album.slug}-{track.track_number:02d}-{slugify(track.title)}"
        singles_album.tracks.append(track)
        songs.append(track)
    albums.append(singles_album)

    for spec in PLACEHOLDER_ALBUMS:
        album = Album(
            title=spec["title"],
            slug=spec["slug"],
            year=spec["year"],
            status=spec["status"],
            artwork=spec["artwork"],
            summary=spec["summary"],
            deeper_system=spec["deeper_system"],
            visual_world=spec["visual_world"],
            source_url=spec.get("source_url", ""),
        )
        for track_number, track_spec in enumerate(spec.get("tracks", []), start=1):
            title = track_spec["title"]
            lyrics = track_spec.get("lyrics", "")
            if track_spec.get("lyrics_path"):
                lyrics = lyrics or read_repo_text(track_spec["lyrics_path"])
            track = Song(
                title=title,
                album_slug=album.slug,
                album_title=album.title,
                track_number=track_number,
                year=track_spec.get("year", album.year),
                lyrics=lyrics,
                lyric_status=track_spec.get("lyric_status", "Lyrics to import"),
                status=track_spec.get("status", album.status),
            )
            special = SPECIAL_BRIEFS.get(slugify(title))
            track.themes = track_spec.get("themes") or (special["themes"] if special else infer_themes(track.title, album.slug))
            track.meaning = track_spec.get("meaning") or (special["meaning"] if special else infer_meaning(track.title, album))
            track.video_seeds = track_spec.get("seeds") or (special["seeds"] if special else generic_seeds(track, album))
            track.youtube_videos = track_spec.get("youtube_videos", [])
            apply_imported_album_lyrics(track, album, album_lyrics)
            primary_video = primary_youtube_video(track)
            if primary_video:
                track.youtube_video_id = primary_video["id"]
                track.youtube_title = primary_video.get("title", "")
            track.slug = f"{album.slug}-{track.track_number:02d}-{slugify(track.title)}"
            album.tracks.append(track)
            songs.append(track)
        albums.append(album)

    apply_duplicate_lyrics(songs)
    apply_streaming_links(albums)
    return albums, songs


def nav(prefix: str) -> str:
    return f"""
    <header class="site-header">
      <a class="brand" href="{prefix}index.html" aria-label="i C. infinity home">
        <img src="{prefix}assets/favicon.jpg" width="38" height="38" alt="" aria-hidden="true">
        <span class="brand-copy">
          <strong>i C. infinity</strong>
          <span>music, stories and imagination</span>
        </span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="site-nav" id="site-nav" aria-label="Primary navigation">
        <a href="{prefix}albums.html">Albums</a>
        <a href="{prefix}songs.html">Songs</a>
        <a href="{prefix}worlds.html">Worlds</a>
        <a href="{prefix}downloads.html">Download Packs</a>
        <a href="{prefix}infinity-engine.html">Infinity Engine</a>
        <a href="{prefix}builders/index.html">Studio</a>
        <a href="{prefix}about.html">About</a>
        <a href="{RIGHT_PLACE_RIGHT_TIME_SITE}">Support</a>
      </nav>
    </header>
    """


def layout(title: str, description: str, body: str, prefix: str = "", page_class: str = "", extra_scripts: str = "") -> str:
    body_class = f' class="{esc(page_class)}"' if page_class else ""
    return f"""<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="icon" type="image/jpeg" href="{prefix}assets/favicon.jpg">
  <link rel="stylesheet" href="{prefix}assets/css/styles.css?v=photo-story-8">
</head>
<body{body_class}>
  {nav(prefix)}
  <main class="page {page_class}">
{body}
  </main>
  <footer class="footer">
    <div class="footer-inner">
      <div>
        <strong>i C. infinity</strong><br>
        <span>Music, stories, ideas and places.</span>
      </div>
      <div>
        <a href="{prefix}grand-narrative.html">Grand Narrative</a> &middot;
        <a href="{prefix}photo-archive.html">Photo Worlds</a> &middot;
        <a href="{prefix}travel-oracle.html">Travel Oracle</a> &middot;
        <a href="{prefix}worlds.html">More worlds</a> &middot;
        <a href="{prefix}downloads.html">Download packs</a> &middot;
        <a href="{prefix}infinity-engine.html">Infinity Engine</a> &middot;
        <a href="{prefix}builders/index.html">Studio</a> &middot;
        <a href="{prefix}sources.html">Listen and explore</a> &middot;
        <a href="{prefix}site-map.html">Site map</a>
      </div>
    </div>
  </footer>
  <script src="{prefix}assets/js/site.js?v=external-tabs-2"></script>
  <script src="{prefix}assets/js/order-config.js"></script>
  <script src="{prefix}assets/js/order.js?v=ordering-paused-2"></script>
  {extra_scripts}
</body>
</html>
"""


def album_card(album: Album, prefix: str = "") -> str:
    href = f"{prefix}albums/{album.slug}/"
    source = f'<div class="album-body quiet"><a href="{esc(album.source_url)}">Listen or watch</a></div>' if album.source_url else ""
    return f"""
    <article class="album-card">
      <a href="{href}">
        <div class="album-art"><img src="{prefix}{esc(album.artwork)}" alt="{esc(album.title)} artwork"></div>
        <div class="album-body">
          <h3>{esc(album.title)}</h3>
          <p>{esc(album.summary)}</p>
          <div class="meta-line"><span>{esc(album.year)}</span><span>{esc(album.status)}</span><span>{len(album.tracks)} songs</span></div>
        </div>
      </a>
      {source}
    </article>
    """


def song_status(song: Song) -> str:
    if song.ready():
        return '<span class="status-pill ready">Lyrics available</span>'
    if primary_youtube_video(song):
        return '<span class="status-pill video">Video available</span>'
    return '<span class="status-pill todo">Lyrics coming soon</span>'


def song_card(song: Song, prefix: str = "") -> str:
    search_terms = [song.title, song.album_title, " ".join(song.themes), "spotify apple itunes"]
    if song.youtube_video_id:
        orientations = " ".join(video.get("orientation", "") for video in song.youtube_videos)
        search_terms.append(f"youtube lyric video {orientations}")
    search = " ".join(search_terms).lower()
    href = f"{prefix}songs/{song.slug}/"
    track = f"Track {song.track_number}" if song.track_number else "Song"
    tags = "".join(f"<span>{esc(tag)}</span>" for tag in song.themes[:3])
    listen = listen_links_html(song, compact=True)
    return f"""
    <article class="song-card" data-song-card data-search="{esc(search)}">
      <a class="song-main-link" href="{href}">
        <h3>{esc(song.title)}</h3>
        <p>{esc(song.album_title)} - {esc(track)}</p>
        <div class="tag-line">{tags}</div>
        <div class="meta-line">{song_status(song)}</div>
      </a>
      {listen}
    </article>
    """.rstrip()


def track_row(song: Song, prefix: str = "") -> str:
    href = f"{prefix}songs/{song.slug}/"
    lyric_note = "Read the lyrics" if song.ready() else ("Watch the video" if primary_youtube_video(song) else "Lyrics coming soon")
    return f"""
    <div class="track-row">
      <a href="{href}">
        <span class="track-number">{song.track_number:02d}</span>
        <span class="track-title"><strong>{esc(song.title)}</strong><span>{esc(lyric_note)}</span></span>
        {song_status(song)}
      </a>
    </div>
    """.rstrip()


def home_page(albums: list[Album], songs: list[Song]) -> str:
    ready_count = sum(1 for song in songs if song.ready())
    shifting_song = next(
        (
            song
            for song in songs
            if slugify(song.title) == "shifting-sands-of-timeless-redlands"
            and primary_youtube_video(song)
        ),
        None,
    )
    expo_section = ""
    if shifting_song:
        portrait_video = next((video for video in shifting_song.youtube_videos if video.get("orientation") == "vertical"), primary_youtube_video(shifting_song))
        expo_section = f"""
    <section class="section video-section">
      <div class="wrap video-feature">
        <div class="vertical-video-frame">
          <a class="vertical-video-poster" href="songs/{esc(shifting_song.slug)}/">
            <img src="{esc(youtube_thumbnail_url(portrait_video['id'], portrait_video.get('thumbnail', 'maxresdefault')))}" alt="{esc(portrait_video.get('title', shifting_song.title))} thumbnail">
            <span class="play-mark" aria-hidden="true"></span>
            <span class="sr-only">Open {esc(shifting_song.title)}</span>
          </a>
        </div>
        <div class="video-feature-copy">
          <p class="eyebrow">Expo Song</p>
          <h2>{esc(shifting_song.title)}</h2>
          <p>A song about place, memory and the changing Redlands, with both widescreen and portrait videos.</p>
          <div class="action-row">
            <a class="button" href="songs/{esc(shifting_song.slug)}/">Open song page</a>
            <a class="button secondary" href="albums/next-signals/">Next Signals</a>
          </div>
        </div>
      </div>
    </section>
        """.strip()
    body = f"""
    <section class="hero home-intro">
      <img class="home-hero-image" src="assets/img/hero-luke-universal-creator.webp" alt="Luke Universal Creator image">
      <div class="hero-content">
        <h1>i C. infinity</h1>
        <p>Music from island life to the stars, bringing together real experience, science, spirituality, imagination and hope.</p>
        <div class="hero-actions">
          <a class="button" href="albums.html">Explore albums</a>
          <a class="button secondary" href="songs.html">Find a song</a>
          <a class="button secondary" href="downloads.html">Buy music</a>
        </div>
        <div class="metrics" aria-label="Catalogue status">
          <div class="metric"><strong>{len(albums)}</strong><span>albums and collections</span></div>
          <div class="metric"><strong>{len(songs)}</strong><span>songs</span></div>
          <div class="metric"><strong>{ready_count}</strong><span>songs with full lyrics</span></div>
        </div>
      </div>
    </section>
    <section class="image-sequence" aria-label="Album world images">
      <article class="image-panel">
        <img src="assets/img/cover-starseed.webp" alt="Starseed Code artwork">
        <div class="image-panel-copy">
          <h2>From Aura to Infinity</h2>
          <p>Songs about identity, love, intelligence, community and the mystery of being alive.</p>
        </div>
      </article>
      <article class="image-panel">
        <img src="assets/img/cover-straddie.webp" alt="Songs of Straddie artwork">
        <div class="image-panel-copy">
          <h2>Meet me on Straddie</h2>
          <p>Minjerribah, summer, shoreline, community, romance and cosmic ideas with sand between their toes.</p>
        </div>
      </article>
    </section>
    {expo_section}
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <h2>Album Worlds</h2>
          <p>Each album has its own mood, story, songs, lyrics and pictures.</p>
        </div>
        <div class="album-grid">
          {''.join(album_card(album) for album in albums)}
        </div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>The World Around the Music</h2>
          <p>The songs grow from a larger life of travel, technology, spirit, place, relationships and the search for a kinder future.</p>
        </div>
        <div class="feature-grid">
          <article class="feature-card"><h3>I see infinity. I choose infinity.</h3><p><a href="grand-narrative.html">Read the story</a> behind the artist name and the ideas carried through the music.</p></article>
          <article class="feature-card"><h3>Luke Catalyst</h3><p><a href="luke-catalyst.html">Meet Luke</a>: lifelong learner, practical worker, traveller and artist.</p></article>
          <article class="feature-card"><h3>Travel Oracle</h3><p><a href="travel-oracle.html">Follow the journey</a>, from practical travel checks to a long-term dream of seeing the world.</p></article>
          <article class="feature-card"><h3>More Worlds</h3><p><a href="worlds.html">Explore the other ideas</a> around the music, including Cosmic Nexus, relationships and ways to support the work.</p></article>
        </div>
      </div>
    </section>
    """
    return layout("i C. infinity - Music Universe", "A multi-page song and album map for i C. infinity.", body)


def albums_index(albums: list[Album]) -> str:
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Albums</h1>
          <p>Released albums, new music still taking shape, standalone songs and early work from the archive.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/hero-brisbane-tiny-planet.webp" alt="Tiny planet visual from I See Infinity"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap album-grid">
        {''.join(album_card(album) for album in albums)}
      </div>
    </section>
    """
    return layout("Albums - i C. infinity", "Albums and music collections by i C. infinity.", body)


def songs_index(songs: list[Song]) -> str:
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Songs</h1>
          <p>Search the songs by title, album or idea. Many pages include full lyrics, music videos and a short story about the song.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-starseed.webp" alt="Starseed Code artwork"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="search-box">
          <label for="song-search">Find a song, album, or theme</label>
          <input id="song-search" data-song-search type="search" placeholder="Try Aura, Straddie, protopia, memory, Gaia">
          <div class="platform-row" aria-label="Artist platform links">
            <a class="listen-chip spotify" href="{SPOTIFY_ARTIST}" target="_blank" rel="noopener">Spotify artist page</a>
            <a class="listen-chip apple" href="{APPLE_ARTIST}" target="_blank" rel="noopener">Apple Music artist page</a>
          </div>
          <label for="song-keyword">Choose a keyword</label>
          <select id="song-keyword" data-song-keyword>
            <option value="">All keywords</option>
          </select>
          <p class="filter-count" data-filter-count></p>
        </div>
        <div class="song-grid">
          {''.join(song_card(song) for song in songs)}
        </div>
      </div>
    </section>
    """
    return layout("Songs - i C. infinity", "Searchable song pages for i C. infinity.", body)


def downloads_page(albums: list[Album], songs: list[Song]) -> str:
    released = [album for album in albums if album.status == "Released album"]
    package_options = "\n".join(
        f'<option value="{esc(package["id"])}">{esc(package["name"])} - ${package["price"]} AUD</option>'
        for package in PACKAGE_OPTIONS
    )
    album_links = "".join(
        f"""
        <article class="album-card">
          <a href="albums/{album.slug}/">
            <div class="album-art"><img src="{esc(album.artwork)}" alt="{esc(album.title)} artwork"></div>
            <div class="album-body">
              <h3>{esc(album.title)}</h3>
              <p>{esc(album.summary)}</p>
              <div class="meta-line"><span>{esc(album.year)}</span><span>{len(album.tracks)} songs</span></div>
            </div>
          </a>
        </article>
        """
        for album in released
    )
    package_compare_html = "".join(
        f"""
        <article class="feature-card package-card">
          <h3>{esc(package["name"])}</h3>
          <p class="package-price"><strong>${package["price"]} AUD</strong></p>
          <p>{esc(package["description"])}</p>
          <p>{esc(package["album_hint"])}</p>
          <div class="action-row">
            <a class="button secondary" href="{esc(order_href(package["id"]))}">Choose this pack</a>
          </div>
        </article>
        """
        for package in PACKAGE_OPTIONS
    )
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Download Packs</h1>
          <p>Explore the planned downloadable music packs: one album, a connected set or the wider archive. Online ordering is not open yet.</p>
          <div class="action-row">
            <a class="button" href="#choose-package">Explore the packs</a>
            <a class="button secondary" href="albums.html">Explore the albums</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-building-protopia.webp" alt="Building Protopia artwork"></div>
      </div>
    </section>
    <section class="section package-sale" id="choose-package">
      <div class="wrap">
        <div class="section-head">
          <h2>Planned music packs</h2>
          <p>These prices are in Australian dollars. The packs can be explored now, but the payment gateway is intentionally not connected yet.</p>
        </div>
        <div class="feature-grid">{package_compare_html}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>Choose an album</h2>
          <p>Open an album to read its story and song list before deciding.</p>
        </div>
        <div class="album-grid">{album_links}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap layout-two">
        <div class="panel">
          <h2>What you receive</h2>
          <p>A clearly named download folder with the music, cover art and track list. Lyrics and bonus material are included where they are available.</p>
          <p>The full archive can also include working albums, B-sides, drafts and selected works in progress.</p>
        </div>
        <div class="panel">
          <h2>When ordering opens</h2>
          <p>The pack choices and future order form are already mapped. Payment will remain closed until the music files, delivery process and chosen gateway are ready.</p>
          <p>No donation link is used as a music checkout.</p>
        </div>
      </div>
    </section>
    <section class="section" id="order-music">
      <div class="wrap layout-two order-layout">
        <form class="panel order-form" data-order-form method="post">
          <input type="hidden" name="sourcePage" data-source-page>
          <input class="screen-reader-trap" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
          <h2>Music order preview</h2>
          <p class="order-status" data-order-status>Online ordering is being prepared. Payment is not open on this page yet.</p>
          <label for="packageId">Music package</label>
          <select id="packageId" name="packageId" data-package-select required>
            {package_options}
          </select>
          <div class="order-summary" data-order-summary aria-live="polite"></div>
          <label for="albumChoices">Album choice or bundle note</label>
          <textarea id="albumChoices" name="albumChoices" rows="3" data-album-choices placeholder="Example: Songs of Straddie, or Straddie and Starseed"></textarea>
          <div class="form-grid">
            <div>
              <label for="buyerName">Name</label>
              <input id="buyerName" name="buyerName" autocomplete="name" required>
            </div>
            <div>
              <label for="buyerEmail">Email for delivery</label>
              <input id="buyerEmail" name="buyerEmail" type="email" autocomplete="email" required>
            </div>
          </div>
          <fieldset class="payment-options">
            <legend>Possible payment method</legend>
            <label><input type="radio" name="paymentMethod" value="stripe" checked> Card or wallet</label>
            <label><input type="radio" name="paymentMethod" value="payid"> PayID or bank transfer</label>
          </fieldset>
          <label for="deliveryNotes">Notes</label>
          <textarea id="deliveryNotes" name="deliveryNotes" rows="3" placeholder="Anything useful for delivery or package choice"></textarea>
          <button class="button" type="submit" data-order-submit disabled>Ordering not open yet</button>
        </form>
        <aside class="panel">
          <h2>When ordering opens</h2>
          <p><strong>1.</strong> Choose a pack and name the album or albums.</p>
          <p><strong>2.</strong> A dedicated music-payment gateway will handle the payment when Luke decides the system is ready.</p>
          <p><strong>3.</strong> The order will be confirmed and the clearly labelled music folder delivered.</p>
          <p>The existing PayPal link is for donations only. It is not used for music sales.</p>
        </aside>
      </div>
    </section>
    """
    return layout("Download Packs - i C. infinity", "Explore planned downloadable i C. infinity albums and music archive packs.", body)


def starseed_video_section(album: Album, prefix: str) -> str:
    if album.slug != STARSEED_ALBUM_SLUG:
        return ""
    video_tracks = [song for song in album.tracks if primary_youtube_video(song)]
    if not video_tracks:
        return ""
    featured_video = primary_youtube_video(video_tracks[0])
    video_index = "".join(
        f"""
        <a class="video-chip" href="{prefix}songs/{esc(song.slug)}/#vertical-video">
          <span>{song.track_number:02d}</span>
          <strong>{esc(song.title)}</strong>
          <em>Vertical video</em>
        </a>
        """
        for song in video_tracks
    )
    return f"""
    <section class="section video-section" id="vertical-video-playlist">
      <div class="wrap video-feature">
        <div class="vertical-video-frame playlist-frame">
          <a class="vertical-video-poster" href="{esc(STARSEED_YOUTUBE_PLAYLIST_URL)}" target="_blank" rel="noopener">
            <img src="{esc(youtube_thumbnail_url(featured_video['id'], featured_video.get('thumbnail', 'maxresdefault')))}" alt="{esc(featured_video.get('title', 'Starseed Code vertical video'))} thumbnail">
            <span class="play-mark" aria-hidden="true"></span>
            <span class="sr-only">Open Starseed Code YouTube playlist</span>
          </a>
        </div>
        <div class="video-feature-copy">
          <p class="eyebrow">Portrait music videos</p>
          <h2>Starseed Code Vertical Playlist</h2>
          <p>{len(video_tracks)} Starseed Code songs are matched to portrait-format YouTube videos. The numbers keep the streaming album order; gaps mean that video is not currently public on YouTube.</p>
          <div class="action-row">
            <a class="button" href="{esc(STARSEED_YOUTUBE_PLAYLIST_URL)}" target="_blank" rel="noopener">Open playlist</a>
            <a class="button secondary" href="#track-map">See the songs</a>
          </div>
        </div>
      </div>
      <div class="wrap">
        <div class="video-index" aria-label="Starseed Code vertical videos">
          {video_index}
        </div>
      </div>
    </section>
    """


def landscape_album_video_section(album: Album, prefix: str) -> str:
    meta = LANDSCAPE_ALBUM_VIDEO_MAP.get(album.slug)
    if not meta:
        return ""
    video_tracks = [song for song in album.tracks if primary_youtube_video(song)]
    playlist_only = meta.get("playlist_only", [])
    if not video_tracks and not playlist_only:
        return ""
    matched_count = sum(len(song.youtube_videos) for song in video_tracks)
    total_count = matched_count + len(playlist_only)
    description = meta["description"].format(
        track_count=len(album.tracks),
        matched_count=matched_count,
        total_count=total_count,
    )
    video_index = "".join(
        f"""
        <a class="video-chip" href="{prefix}songs/{esc(song.slug)}/#vertical-video">
          <img src="{esc(youtube_thumbnail_url(primary_youtube_video(song)['id'], primary_youtube_video(song).get('thumbnail', 'hqdefault')))}" alt="{esc(primary_youtube_video(song).get('title', song.title))} thumbnail">
          <strong>{esc(song.title)}</strong>
          <em>{len(song.youtube_videos)} video{'s' if len(song.youtube_videos) != 1 else ''}</em>
        </a>
        """.strip()
        for song in video_tracks
    )
    playlist_only_index = "".join(
        f"""
        <a class="video-chip" href="{esc(youtube_video_url(video['id'], meta['playlist_id']))}" target="_blank" rel="noopener">
          <img src="{esc(youtube_thumbnail_url(video['id'], 'hqdefault'))}" alt="{esc(video['title'])} thumbnail">
          <strong>{esc(video['title'])}</strong>
          <em>Playlist-only video</em>
        </a>
        """.strip()
        for video in playlist_only
    )
    return f"""
    <section class="section video-section" id="lyric-video-playlist">
      <div class="wrap video-feature landscape-feature">
        <div class="vertical-video-frame wide-video-frame playlist-frame">
          <iframe title="{esc(meta['title'])}" src="{esc(youtube_playlist_embed_src(meta['playlist_id']))}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" loading="lazy" allowfullscreen></iframe>
        </div>
        <div class="video-feature-copy">
          <p class="eyebrow">Music videos</p>
          <h2>{esc(meta['title'])}</h2>
          <p>{esc(description)} There are {total_count} videos in the collection, including {matched_count} connected to songs on this site.</p>
          <div class="action-row">
            <a class="button" href="{esc(meta['playlist_url'])}" target="_blank" rel="noopener">Open playlist</a>
            <a class="button secondary" href="#track-map">See the songs</a>
          </div>
        </div>
      </div>
      <div class="wrap">
        <div class="video-index" aria-label="{esc(meta['title'])}">
          {video_index}{playlist_only_index}
        </div>
      </div>
    </section>
    """.rstrip()


def next_signals_teaser_section(album: Album, prefix: str) -> str:
    if album.slug != "next-signals":
        return ""
    video = FOURTH_ALBUM_TEASER_VIDEO
    video_url = video.get("url") or youtube_video_url(video["id"])
    embed_src = youtube_video_embed_src(video["id"])
    return f"""
    <section class="section video-section" id="fourth-album-teaser">
      <div class="wrap">
        <article class="song-video-panel wide-video-frame">
          <div class="vertical-video-frame wide-video-frame">
            <iframe title="{esc(video['title'])}" src="{esc(embed_src)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" loading="lazy" allowfullscreen></iframe>
          </div>
          <div class="vertical-video-copy">
            <p class="eyebrow">{esc(video.get('label', 'Free Teaser'))}</p>
            <h2>{esc(video['title'])}</h2>
            <p>A free first look at the fourth album and the ideas moving through it.</p>
            <div class="listen-links compact">
              <a class="listen-chip youtube" href="{esc(video_url)}" target="_blank" rel="noopener">Open on YouTube</a>
            </div>
          </div>
        </article>
      </div>
    </section>
    """.rstrip()


def album_page(album: Album) -> str:
    prefix = "../../"
    tracks = "".join(track_row(song, prefix) for song in album.tracks)
    if not tracks:
        tracks = """
        <div class="notice">
          The song list is coming soon.
        </div>
        """
    video_section = starseed_video_section(album, prefix) + landscape_album_video_section(album, prefix) + next_signals_teaser_section(album, prefix)
    track_section_id = ' id="track-map"' if video_section else ""
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>{esc(album.title)}</h1>
          <p>{esc(album.summary)}</p>
          <div class="meta-line"><span>{esc(album.year)}</span><span>{esc(album.status)}</span><span>{len(album.tracks)} songs</span></div>
        </div>
        <div class="hero-cover"><img src="{prefix}{esc(album.artwork)}" alt="{esc(album.title)} artwork"></div>
      </div>
    </section>{video_section}
    <section class="section"{track_section_id}>
      <div class="wrap layout-two">
        <div>
          <h2>Songs</h2>
          <div class="track-list">{tracks}</div>
        </div>
        <aside class="panel">
          <h2>About this album</h2>
          <p>{esc(album.deeper_system)}</p>
          <h3>Images and ideas</h3>
          <p>{esc(album.visual_world)}</p>
          <h3>Download packs</h3>
          <p>Explore the planned album packs and wider music collections. Online ordering is not open yet.</p>
          <p><a class="button secondary" href="{prefix}downloads.html">See download packs</a></p>
        </aside>
      </div>
    </section>
    """
    return layout(f"{album.title} - i C. infinity", album.summary, body, prefix)


def song_page(song: Song, album: Album) -> str:
    prefix = "../../"
    lyrics = esc(song.lyrics) if song.lyrics else "Lyrics coming soon."
    tags = "".join(f"<span>{esc(tag)}</span>" for tag in song.themes)
    release = listen_links_html(song) or "No public release link attached yet."
    spotify_embed = spotify_embed_html(song)
    youtube_embed = youtube_song_embed_html(song)
    media_embeds = spotify_embed + youtube_embed
    content_warning = ""
    if slugify(song.title) in {"don-t-try-to-fix-me", "dont-try-to-fix-me"}:
        content_warning = """
          <div class="notice content-warning">
            <strong>Language warning:</strong> This song contains 53 F-bombs. The language is deliberate: it carries the urgency, frustration, and seriousness of the times rather than softening them for comfort.
          </div>
        """
    body = f"""
    <section class="song-title">
      <div class="wrap">
        <h1>{esc(song.title)}</h1>
        <p>{esc(song.album_title)}{f' - Track {song.track_number}' if song.track_number else ''}</p>
        <div class="tag-line">{tags}</div>
      </div>
    </section>
    <section class="section">
      <div class="wrap layout-two">
        <article>
          <div class="panel">
            <h2>About this song</h2>
            <p>{esc(song.meaning)}</p>
          </div>
          {media_embeds}
          {content_warning}
          <h2>Lyrics</h2>
          <pre class="lyrics">{lyrics}</pre>
        </article>
        <aside class="panel">
          <h2>Listen</h2>
          {release}
          <h3>From the album</h3>
          <p><a href="{prefix}albums/{esc(album.slug)}/">{esc(album.title)}</a></p>
          <p>{esc(album.summary)}</p>
          <h3>Music download packs</h3>
          <p>Explore the planned packs. Online ordering is not open yet.</p>
          <p><a class="button secondary" href="{prefix}downloads.html">See download packs</a></p>
        </aside>
      </div>
    </section>
    """
    return layout(f"{song.title} - i C. infinity", song.meaning, body, prefix)


def engine_page() -> str:
    steps = [
        ("0. Ingestion Profile", "Collect the song page, lyrics, audio notes, stems, emotion, volume, tone, pitch, beats, sections, and marketing-safe metadata before making visual calls."),
        ("1. Lyrical Intelligence Swarm", "Extract core themes, emotional arc, symbols, narrative tension, and possible visual metaphors before generating expensive media."),
        ("2. Auditory Intelligence Pass", "Map BPM, dynamics, key or pitch centre, section markers, beat drops, hooks, stem access, and edit points for timing-led video decisions."),
        ("3. Human Direction Point", "Luke chooses the preferred narrative direction while the system handles drafts, variants, and bookkeeping."),
        ("4. Comic-as-Storyboard", "Make still panels first. They are cheaper, easier to revise, and become a visual test before full video."),
        ("5. Keyframe-to-Video", "Use approved panels plus ingestion timing to choose first frames, last frames, and the in-between beats that organise motion."),
        ("6. Distribution Fit", "Ask where a finished image or video belongs, who it is for, what screen it appears on, and what would feel welcome rather than intrusive."),
        ("7. Review and Flywheel", "Approve, revise, or export. Audience response and creative notes feed back into the catalogue without intrusive marketing tactics."),
    ]
    step_html = "".join(f'<article class="engine-step"><h3><strong>{esc(title)}</strong></h3><p>{esc(text)}</p></article>' for title, text in steps)
    lane_cards = "".join(
        f"""
        <a class="studio-lane-card" href="{href}">
          <span>{number}</span>
          <strong>{title}</strong>
          <p>{copy}</p>
        </a>
        """
        for number, title, copy, href in [
            ("001", "Human listen", "Tap signals while listening, tune music-video dials, and export SRT/Markdown cues.", "builders/human-ingestion.html"),
            ("007", "Ingestion", "Build the song intelligence profile from lyrics, audio, stems, metadata, and target-query inputs.", "builders/ingestion.html"),
            ("01", "Visual brief", "Choose an existing song page and define the image/video direction.", "builders/music-video.html"),
            ("02", "Comic storyboard", "Plan the low-cost panels first so the expensive video work receives approved keyframes.", "builders/storyboard.html"),
            ("03", "Keyframe shot", "Use ingestion timing to choose first/last frames, in-between beats, motion, and generator handoff notes.", "builders/keyframe-shot.html"),
            ("04", "Distribution fit", "Turn a placement question into platform, screen, metadata, caption, and export choices.", "builders/variants.html"),
        ]
    )
    body = f"""
    <section class="studio-hero">
      <div class="wrap studio-hero-grid">
        <div class="studio-hero-copy">
          <h1>Infinity Engine</h1>
          <p>The production bench where existing i C. infinity songs become ingestion profiles, key art, comic storyboards, image sets, video clips, metadata, variants, first cuts, and feedback loops.</p>
          <div class="action-row">
            <a class="button" href="builders/index.html">Open Studio builders</a>
            <a class="button secondary" href="songs.html">Choose a song</a>
          </div>
        </div>
        <div class="studio-console" aria-label="Infinity Engine studio console">
          <div class="console-screen">
            <img src="assets/img/cover-building-protopia.webp" alt="Building Protopia artwork">
          </div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <h2>Pipeline Spine</h2>
          <p>The songs are already written and mapped on the song pages. The Studio ingests lyrics and audio intelligence first, then builds images, clips, edits, metadata, and screen-specific variants.</p>
        </div>
        <div class="engine-map">{step_html}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>Studio Builders</h2>
          <p>Each builder autosaves in the browser, creates a clean `.md` file, and leaves generator choices editable so you can use your favourite image or video tool.</p>
        </div>
        <div class="studio-lane-grid">{lane_cards}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap layout-two">
        <div class="panel">
          <h2>Cheapest sensible path</h2>
          <p>Start from the existing song page, complete ingestion, choose the visual moment, make stills and storyboard panels, then create short clips. Keep lip-sync avoided where possible. Use local or low-cost tools for rough passes.</p>
        </div>
        <div class="panel">
          <h2>Best quality path</h2>
          <p>Use higher-end image and video generation only after the ingestion and storyboard layers prove the idea. The expensive stage should receive already-approved visual direction, audio timing, metadata, and distribution-fit targets.</p>
        </div>
      </div>
    </section>
    """
    return layout("Infinity Engine - i C. infinity", "The production engine behind i C. infinity song videos and comics.", body, page_class="studio-page")


STUDIO_BUILDERS = [
    {
        "key": "humanIngestion",
        "number": "001",
        "label": "Human Listen",
        "title": "Human guided ingestion engine",
        "headline": "Reverse-engineer a song by listening, tapping signals, and tuning music-video dials.",
        "note": "Live human signal pads, music-language dials, SRT cues, Markdown export, and human observation logs.",
        "href": "human-ingestion.html",
        "destination": "human-ingestion/",
        "custom": True,
    },
    {
        "key": "ingestion",
        "number": "007",
        "label": "Ingestion",
        "title": "Song intelligence ingestion builder",
        "headline": "Build the lyrical, auditory, stem, and metadata profile before visual production starts.",
        "note": "Emotion, volume, tone, pitch, beats, lyrics, stems, metadata, and target-query inputs.",
        "href": "ingestion.html",
        "destination": "ingestion/",
    },
    {
        "key": "songBrief",
        "number": "01",
        "label": "Visual Brief",
        "title": "Song-to-visual brief builder",
        "headline": "Turn the ingestion profile into an image and video production brief.",
        "note": "Song link, ingestion profile, visual intent, generator preferences, and the next useful action.",
        "href": "music-video.html",
        "destination": "visual-briefs/",
    },
    {
        "key": "storyboard",
        "number": "02",
        "label": "Storyboard",
        "title": "Comic-as-storyboard builder",
        "headline": "Make the cheap still panels before spending on video.",
        "note": "Panel rhythm, visual world, character references, image prompts, and approval notes.",
        "href": "storyboard.html",
        "destination": "storyboards/",
    },
    {
        "key": "shot",
        "number": "03",
        "label": "Keyframe Shot",
        "title": "Keyframe-to-video shot builder",
        "headline": "Use ingestion timing to organise first frames, last frames, and in-between beats.",
        "note": "Timing profile, frame choices, beat checkpoints, camera move, generator choice, and edit notes.",
        "href": "keyframe-shot.html",
        "destination": "shots/",
    },
    {
        "key": "variant",
        "number": "04",
        "label": "Distribution Fit",
        "title": "Distribution fit planner",
        "headline": "Turn a placement question into platform, screen, metadata, and export decisions.",
        "note": "Placement question, best-fit outputs, respectful deployment rules, metadata, captions, and reuse plan.",
        "href": "variants.html",
        "destination": "variants/",
    },
    {
        "key": "review",
        "number": "05",
        "label": "Review",
        "title": "First cut review builder",
        "headline": "Turn a rough cut into precise revision notes.",
        "note": "Keep, revise, regenerate, manual edit, publish, and audience feedback signals.",
        "href": "review.html",
        "destination": "reviews/",
    },
    {
        "key": "handoff",
        "number": "06",
        "label": "Handoff",
        "title": "Agent handoff builder",
        "headline": "Pass a small production task to a future agent.",
        "note": "Task, source files, allowed references, generator lane, output format, and boundaries.",
        "href": "handoff.html",
        "destination": "handoffs/",
    },
]


def builder_index_page() -> str:
    cards = "".join(
        f"""
        <a class="studio-builder-card" href="{esc(item['href'])}">
          <span>{esc(item['number'])}</span>
          <strong>{esc(item['label'])}</strong>
          <p>{esc(item['note'])}</p>
          <em>Save to {esc(item['destination'])}</em>
        </a>
        """
        for item in STUDIO_BUILDERS
    )
    quick_actions = [
        ("Need a song", "Open song catalogue", "Choose the existing source page first.", "../songs.html", "secondary"),
        ("Human start", "Open listening cockpit", "Tap signals while the song plays.", "human-ingestion.html", "primary"),
        ("Clean profile", "Fill 007 ingestion", "Turn listening signals into formal song data.", "ingestion.html", "secondary"),
        ("Have profile", "Make visual brief", "Turn ingestion into direction.", "music-video.html", "secondary"),
        ("Need targets", "Plan distribution", "Recommend platforms, screens, metadata, and export shape.", "variants.html", "secondary"),
    ]
    quick_action_html = "".join(
        f"""
        <a class="studio-start-option {kind}" href="{href}">
          <span>{kicker}</span>
          <strong>{title}</strong>
          <em>{note}</em>
        </a>
        """
        for kicker, title, note, href, kind in quick_actions
    )
    body = f"""
    <section class="studio-hero studio-hub-hero">
      <div class="wrap studio-hero-grid">
        <div class="studio-hero-copy">
          <h1>Infinity Engine Studio</h1>
          <p>A fast production cockpit for turning existing i C. infinity song pages into human listening signals, ingestion profiles, images, video clips, distribution-fit plans, metadata, review notes, and handoffs.</p>
          <div class="action-row">
            <a class="button" href="human-ingestion.html">Start here</a>
            <a class="button secondary" href="../songs.html">Open songs</a>
            <button class="button secondary" type="button" data-reset-all-forms>Reset all forms</button>
          </div>
        </div>
        <div class="studio-start-panel" aria-label="Fast start actions">
          <div class="studio-panel-heading">
            <div>
              <p class="studio-kicker">Fast start</p>
              <h2>What do you have?</h2>
            </div>
            <p class="studio-destination">No searching</p>
          </div>
          <div class="studio-start-options">{quick_action_html}</div>
        </div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap studio-simple-path" aria-label="Simple production path">
        <article><span>1</span><strong>Song page</strong><em>Pick the existing song.</em></article>
        <article><span>2</span><strong>Human listen</strong><em>Tap feelings, words, turns, and cues.</em></article>
        <article><span>3</span><strong>007 profile</strong><em>Clean the signals into song intelligence.</em></article>
        <article><span>4</span><strong>Distribution fit</strong><em>Choose outputs from song intelligence.</em></article>
      </div>
    </section>
    <section class="section studio-directory">
      <div class="wrap">
        <div class="section-head">
          <h2>All Builders</h2>
          <p>Use these when the fast-start choices are not specific enough. Each tool downloads or copies agent-ready files into the matching folder. Human listening and 007 ingestion are the source profile for later image, video, and distribution decisions.</p>
        </div>
        <div class="studio-builder-grid">{cards}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap studio-flow">
        <article><strong>What did the song say?</strong><span>001 and 007 capture lyric, audio, emotion, timing, stems, and metadata before visuals are invented.</span></article>
        <article><strong>What should be seen?</strong><span>The visual brief turns listening into first image, style world, asset types, captions, and generator choices.</span></article>
        <article><strong>How does it move?</strong><span>Storyboard and keyframe forms ask where to start, where to turn, what to hold, and when to cut.</span></article>
        <article><strong>Where does it belong?</strong><span>Distribution fit recommends platform, screen, aspect, duration, and non-intrusive deployment from the song profile.</span></article>
      </div>
    </section>
    """
    return layout("Infinity Engine Studio - i C. infinity", "Fast Markdown builders for i C. infinity image and video production.", body, prefix="../", page_class="studio-page", extra_scripts='<script src="../assets/js/infinity-builder.js"></script>')


def human_song_payload(songs: list[Song]) -> list[dict[str, object]]:
    payload = []
    for song in songs:
        youtube_video = primary_youtube_video(song)
        youtube_url = youtube_video_link(youtube_video) if youtube_video else ""
        youtube_embed = youtube_video_embed_src(youtube_video["id"], youtube_video.get("playlist_id", "")) if youtube_video else ""
        spotify_embed = ""
        spotify_uri = ""
        spotify_match = re.search(r"open\.spotify\.com/track/([A-Za-z0-9]+)", song.spotify_url)
        if spotify_match:
            spotify_id = spotify_match.group(1)
            spotify_embed = f"https://open.spotify.com/embed/track/{spotify_id}?utm_source=generator"
            spotify_uri = f"spotify:track:{spotify_id}"
        apple_embed = song.apple_url.replace("https://music.apple.com/", "https://embed.music.apple.com/") if song.apple_url.startswith("https://music.apple.com/") else ""
        payload.append(
            {
                "title": song.title,
                "album": song.album_title,
                "slug": song.slug,
                "songPage": f"../songs/{song.slug}/",
                "themes": song.themes,
                "meaning": song.meaning,
                "hasLyrics": song.ready(),
                "lyricStatus": song.lyric_status,
                "lyrics": song.lyrics,
                "videoSeeds": song.video_seeds,
                "spotifyUrl": song.spotify_url,
                "spotifyEmbed": spotify_embed,
                "spotifyUri": spotify_uri,
                "appleUrl": song.apple_url,
                "appleEmbed": apple_embed,
                "youtubeUrl": youtube_url,
                "youtubeEmbed": youtube_embed,
                "primarySource": youtube_embed or spotify_embed or apple_embed,
            }
        )
    return payload


def human_ingestion_page(songs: list[Song]) -> str:
    song_data = json.dumps(human_song_payload(songs), ensure_ascii=False).replace("</", "<\\/")
    body = f"""
    <section class="human-cockpit" data-human-ingestion>
      <script id="humanSongData" type="application/json">{song_data}</script>
      <section class="human-cockpit-topbar" aria-label="Human listening session controls">
        <div class="human-session-brand">
          <img src="../assets/favicon.jpg" alt="">
          <div>
            <p>i C. infinity</p>
            <h1>001 Human Listen</h1>
          </div>
        </div>
        <div class="human-status-chip" id="humanStatus"><span></span><strong id="listenState">standby</strong></div>
        <div class="human-mini-focus" aria-label="Current focus cue">
          <strong>Focus cue</strong>
          <span id="currentFocus">Hook, turn, first image.</span>
        </div>
        <div class="human-session-summary">
          <strong>Source song</strong>
          <span id="topbarSong">Load from catalogue</span>
        </div>
        <div class="human-topbar-actions" aria-label="Cockpit actions">
          <button type="button" id="timerStart" data-icon=">">RUN</button>
          <button type="button" id="timerPause" data-icon="II">PAU</button>
          <button type="button" id="timerBack" data-icon="-">-5</button>
          <button type="button" id="timerForward" data-icon="+">+5</button>
          <button type="button" id="timerMark" data-icon="M">MRK</button>
          <button type="button" id="fullscreenButton" data-icon="F" aria-label="Toggle full-screen cockpit">FUL</button>
        </div>
      </section>

      <section class="human-mobile-tabs" aria-label="Cockpit panels">
        <button type="button" class="active" data-human-tab="live">Live</button>
        <button type="button" data-human-tab="source">Source</button>
        <button type="button" data-human-tab="deck">Pads</button>
        <button type="button" data-human-tab="output">Export</button>
      </section>

      <section class="human-cockpit-grid" aria-label="Human guided listening cockpit">
        <aside class="human-player-panel human-panel" data-human-panel="source" aria-label="Song source and playback">
          <div class="human-panel-head">
            <div>
              <span>Public Song</span>
              <h2>Load from catalogue</h2>
            </div>
            <button class="human-icon-button" type="button" id="resetSession" title="Reset session">RST</button>
          </div>
          <label class="human-field">
            <span>Song</span>
            <select id="songSelect"></select>
          </label>
          <div class="human-link-input">
            <input id="songLinkInput" type="url" placeholder="paste YouTube, Spotify, Apple, or song-page link">
            <button type="button" id="embedSongLink">EMB</button>
          </div>
          <div class="human-source-frame" id="sourceFrame" aria-label="Selected public song player"></div>
          <div class="human-link-row" id="sourceLinks"></div>
        </aside>

        <section class="human-game-panel human-panel" data-human-panel="live" aria-label="Live listening controls">
          <div class="human-live-timer">
            <strong id="listenClock">00:00.0</strong>
            <em id="timerProgress">manual timer ready</em>
            <div class="human-timer-bar" aria-hidden="true"><span id="timerProgressBar"></span></div>
          </div>
          <div class="human-challenge" id="listenChallenge" aria-live="polite"></div>
          <div class="human-note-row">
            <label class="human-field">
              <span>Quick note</span>
              <input id="quickNote" type="text" placeholder="lyric, image, colour, camera move, feeling..." autocomplete="off">
            </label>
            <button type="button" id="addNoteCue">NOTE</button>
          </div>
          <div class="human-map-board" aria-label="Song mapping dials">
            <div class="human-dial-help"><span>tap left -</span><span>tap right +</span></div>
            <div class="human-map-buttons" id="curveSelectors"></div>
          </div>
        </section>

        <aside class="human-output-panel human-panel" data-human-panel="output" aria-label="Infinity Engine output">
          <div class="human-panel-head">
            <div>
              <span>Export</span>
              <h2>Signals for Infinity</h2>
            </div>
            <p id="cueCount">0 cues</p>
          </div>
          <div class="human-export-tabs" aria-label="Export format">
            <button type="button" class="active" data-export-tab="md">MD</button>
            <button type="button" data-export-tab="srt">SRT</button>
            <button type="button" data-export-tab="log">LOG</button>
          </div>
          <textarea id="humanExport" spellcheck="false" readonly></textarea>
          <ol id="cueLog" class="human-output-log" hidden></ol>
          <div class="human-actions">
            <button type="button" id="copyHumanExport">CPY</button>
            <button type="button" id="downloadHumanMd">MD</button>
            <button type="button" id="downloadHumanSrt">SRT</button>
            <button type="button" id="clearCues">CLR</button>
          </div>
        </aside>

        <section class="human-deck-panel human-panel" data-human-panel="deck" aria-label="Signal pad deck">
          <div class="human-pad-grid" id="signalPads"></div>
        </section>
      </section>
    </section>
    """
    scripts = '<script src="../assets/js/human-ingestion.js"></script><script src="https://open.spotify.com/embed/iframe-api/v1" async></script>'
    return layout("Human Guided Ingestion - i C. infinity", "A human listening cockpit for reverse-engineering songs into Infinity Engine signals.", body, prefix="../", page_class="studio-page human-ingestion-page", extra_scripts=scripts)


def builder_footer(active_key: str) -> str:
    keys = [item["key"] for item in STUDIO_BUILDERS]
    index = keys.index(active_key)
    previous_item = STUDIO_BUILDERS[index - 1] if index > 0 else None
    next_item = STUDIO_BUILDERS[index + 1] if index < len(STUDIO_BUILDERS) - 1 else None
    previous = f'<a class="studio-footer-card" href="{esc(previous_item["href"])}"><span>Previous</span><strong>{esc(previous_item["label"])}</strong></a>' if previous_item else '<a class="studio-footer-card" href="index.html"><span>Back</span><strong>Studio home</strong></a>'
    next_link = f'<a class="studio-footer-card next" href="{esc(next_item["href"])}"><span>Next</span><strong>{esc(next_item["label"])}</strong></a>' if next_item else '<a class="studio-footer-card next" href="../infinity-engine.html"><span>Next</span><strong>Pipeline map</strong></a>'
    return f'<nav class="studio-footer-nav" aria-label="Previous and next Studio pages">{previous}{next_link}</nav>'


def builder_page(active_key: str, songs: list[Song]) -> str:
    item = next(builder for builder in STUDIO_BUILDERS if builder["key"] == active_key)
    song_data = json.dumps(human_song_payload(songs), ensure_ascii=False).replace("</", "<\\/")
    shell = f"""
    <section class="studio-builder-shell wrap" data-infinity-builder data-active-builder="{esc(active_key)}">
      <script id="studioSongData" type="application/json">{song_data}</script>
      <aside class="studio-side-nav" aria-label="Studio builder pages"></aside>
      <section class="studio-form-panel" aria-label="Builder form">
        <div class="studio-builder-workbar" aria-label="Current builder">
          <span>{esc(item['number'])}</span>
          <div>
            <strong>{esc(item['label'])}</strong>
            <em>{esc(item['headline'])}</em>
            <small>Save to {esc(item['destination'])}</small>
          </div>
        </div>
        <div hidden><p id="formType"></p><h2 id="formTitle"></h2><p id="destination"></p></div>
        <div class="studio-context-strip" id="builderContext" hidden></div>
        <form id="builderForm" class="studio-field-grid"></form>
      </section>
      <aside class="studio-preview-panel" aria-label="Markdown preview">
        <div class="studio-panel-heading">
          <div>
            <p class="studio-kicker">Output</p>
            <h2>Generated Markdown</h2>
          </div>
          <p class="studio-filename" id="filename"></p>
        </div>
        <textarea id="markdownPreview" class="studio-markdown-preview" readonly spellcheck="false" wrap="soft"></textarea>
        <div class="studio-actions" aria-label="Output actions">
          <button class="button" type="button" id="downloadButton">Download .md</button>
          <button class="button secondary" type="button" id="copyButton">Copy</button>
          <button class="button secondary" type="button" id="clearButton">Reset page</button>
          <button class="button secondary danger" type="button" data-reset-all-forms>Reset all forms</button>
        </div>
        <p class="studio-status" id="statusLine" role="status" aria-live="polite">Autosaves in this browser.</p>
      </aside>
    </section>
    <div class="wrap">{builder_footer(active_key)}</div>
    """
    return layout(f"{item['title']} - i C. infinity", item["note"], shell, prefix="../", page_class="studio-page studio-builder-page", extra_scripts='<script src="../assets/js/infinity-builder.js"></script>')


def grand_narrative_page() -> str:
    aura_image = archive_photo("i-see-infinity", 63, "assets/img/legacy/brisbane-story-bridge.webp")
    gajra_image = archive_photo("i-see-infinity", 33, "assets/img/legacy/amity-point.webp")
    generated_music_image = archive_photo("i-see-infinity", 372, "assets/img/cover-straddie.webp")
    body = f"""
    <section class="page-hero context-hero grand-hero">
      <div class="wrap">
        <div>
          <h1>I see infinity. I choose infinity.</h1>
          <p>A life story, a music universe and a practical hope for a kinder future. Reality, science, spirit and imagination meet here without pretending they are all the same thing.</p>
          <div class="action-row">
            <a class="button" href="albums.html">Hear the music</a>
            <a class="button secondary" href="luke-catalyst.html">Meet Luke</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-a-protopian-gambit-b.png" alt="A Protopian Gambit artwork"></div>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="assets/img/legacy/wivenhoe-lookout.webp" alt="Australian bushland seen from Wivenhoe lookout"></div>
      <div class="story-copy">
          <p class="eyebrow">The explorer came first</p>
          <h2>Scrub, stars and a very large python</h2>
          <p>Luke spent his earliest years on about 100 acres of scrub near Ningi in Queensland. He loved hide-and-seek, tiggy and the feeling of finding his own path through unknown ground.</p>
          <p>One family story tells of a huge carpet python coming down from the rafters towards his cot before his father wrestled it away. Decades later, Luke used a star map to place the Sun in Ophiuchus, the serpent bearer, at the time of his birth.</p>
          <p>The astronomy describes where the Sun appeared in the sky. The serpent-bearer meaning is the personal myth Luke draws from it: exploration, healing, long life and learning how to hold powerful things without worshipping or fearing them.</p>
      </div>
    </section>
    <section class="story-split reverse">
      <div class="story-image"><img src="assets/img/legacy/amity-jetty-sunset.webp" alt="Sunset over Amity jetty"></div>
      <div class="story-copy">
        <p class="eyebrow">What the artist name means</p>
        <h2>Seeing is not enough. There is also a choice.</h2>
        <p>“I see infinity” is the attempt to notice more than the immediate moment: deep time, other people, possible futures, hidden patterns and the limits of one's own point of view.</p>
        <p>“I choose infinity” is the decision to keep exploring. It means choosing growth over a finished identity, possibility over despair and participation over waiting for somebody else to fix everything.</p>
        <p>The full stop in <strong>i C. infinity</strong> matters. It holds a pause between seeing and choosing. The songs live inside that pause.</p>
      </div>
    </section>
    <section class="section narrative-lens-section">
      <div class="wrap">
        <div class="section-head">
          <h2>Four ways of looking</h2>
          <p>The Grand Narrative does not ask people to confuse evidence, belief, metaphor and personal experience.</p>
        </div>
        <div class="feature-grid narrative-lenses">
          <article class="feature-card"><h3>Reality</h3><p>Daily life comes first: work, money, health, law, family, neighbours, beaches, ferries and the choices people can actually make.</p></article>
          <article class="feature-card"><h3>Science</h3><p>A way to test ideas against evidence. Artificial intelligence, astronomy, biology, climate, medicine and engineering belong here.</p></article>
          <article class="feature-card"><h3>Spirit</h3><p>The inner life: meaning, awe, love, grief, ritual, conscience and the feeling that life may be larger than any one person can explain.</p></article>
          <article class="feature-card"><h3>Imagination</h3><p>Fantasy and art let us visit possible worlds before deciding whether any part of them should become real.</p></article>
        </div>
      </div>
    </section>
    <section class="section album-journey-section">
      <div class="wrap">
        <div class="section-head">
          <h2>The music tells the story</h2>
          <p>Each album opens a different part of the same world.</p>
        </div>
        <div class="destination-grid">
          <a class="destination-card" href="albums/songs-of-straddie/" style="--door-image: url('assets/img/cover-straddie.webp')">
            <span class="destination-kicker">Home and belonging</span><h3>Songs of Straddie</h3><p>Love, beaches, community and the island where cosmic ideas put their feet in the sand.</p><strong>Enter the album →</strong>
          </a>
          <a class="destination-card" href="albums/chronicles-of-the-forgotten/" style="--door-image: url('assets/img/cover-chronicles.webp')">
            <span class="destination-kicker">Memory and repair</span><h3>Chronicles of the Forgotten</h3><p>Voices, ancestors, labour and living things that ordinary history too easily leaves out.</p><strong>Enter the album →</strong>
          </a>
          <a class="destination-card" href="albums/starseed-code-from-aura-to-infinity/" style="--door-image: url('assets/img/cover-starseed.webp')">
            <span class="destination-kicker">Mind and cosmos</span><h3>Starseed Code</h3><p>Identity, love, artificial intelligence and the mystery of consciousness under a very large sky.</p><strong>Enter the album →</strong>
          </a>
          <a class="destination-card" href="albums/a-protopian-gambit/" style="--door-image: url('assets/img/cover-a-protopian-gambit-b.png')">
            <span class="destination-kicker">Crisis and practical hope</span><h3>A Protopian Gambit</h3><p>A wager that care, courage and useful action can still make tomorrow better than today.</p><strong>Enter the album →</strong>
          </a>
        </div>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image contain"><img src="{esc(aura_image)}" alt="Aura of Intelligence artwork"></div>
      <div class="story-copy">
        <p class="eyebrow">Aura of Intelligence</p>
        <h2>A digital companion that belongs to the person</h2>
        <p>Aura began with a human question: if artificial intelligence learns from a person's memories, health, voice and choices, who should control it?</p>
        <p>Luke's answer is that the person should. The long-term idea is a private, human-guided companion that helps someone remember, reflect, create and make decisions without claiming ownership of their life.</p>
        <p>Dementia care is one reason this matters. A conversation can help preserve a life story, but intimate memories need clear consent, strong privacy and trusted human care. Aura is imagined as clothing, not skin: helpful, personal and removable.</p>
        <p><a class="button" href="{AURA_OF_INTELLIGENCE_SITE}">Explore Aura of Intelligence</a></p>
      </div>
    </section>
    <section class="story-split reverse" id="gajra-earth">
      <div class="story-image contain"><img src="{esc(gajra_image)}" alt="Invitation to joyful responsible abundance on Earth"></div>
      <div class="story-copy">
        <p class="eyebrow">G.A.J.R.A. Earth</p>
        <h2>Joyful, responsible and abundant—together</h2>
        <p>G.A.J.R.A. stands for Global Associations for Joyful Responsible Abundance on Earth. It is a community idea built around a simple balance.</p>
        <p>Joy without responsibility can hurt people and the Earth. Responsibility without joy can make life cold and heavy. Plenty without either can still leave people behind.</p>
        <p>Abundance here does not mean endless consumption. It means enough time, care, energy, food, shelter, knowledge, friendship and creative freedom for people and nature to flourish.</p>
        <p>It also asks whether unpaid care, community work and environmental repair should count as real value, even when ordinary markets ignore them.</p>
        <p><a class="button" href="{GAJRA_EARTH_SITE}">Visit the G.A.J.R.A. Earth community</a></p>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image contain"><img src="assets/img/cover-a-protopian-gambit-b.png" alt="A Protopian Gambit artwork"></div>
      <div class="story-copy">
        <p class="eyebrow">Protopia, not perfection</p>
        <h2>One useful step at a time</h2>
        <p>Utopia promises a perfect destination. Protopia asks for a better direction. It can begin with a repaired relationship, a safer street, a clearer law, a protected wetland or one person finally having their care recognised.</p>
        <p>The “gambit” is the wager that many small improvements can join together. It rejects both blind optimism and permanent despair.</p>
        <p>The songs return to a few practical rules: repair what is broken without hiding the scar; treat consent as something that can change; turn borders into meeting places; keep humans responsible for the tools they build; and make room for joy while doing serious work.</p>
      </div>
    </section>
    <section class="story-split reverse">
      <div class="story-image"><img src="assets/img/legacy/luke-olympic-tiny-planet.webp" alt="Luke in a tiny planet photograph"></div>
      <div class="story-copy">
        <p class="eyebrow">The circle and the solitary</p>
        <h2>Ideas may begin alone. They cannot stay there.</h2>
        <p>Luke often works alone at the beginning: writing, drawing connections, building pages and turning questions into songs. That is the solitary part.</p>
        <p>The circle begins when other people listen, disagree, improve an idea, join a project or make something of their own. A useful future cannot belong to one founder, one company or one culture.</p>
        <p>This is also why every border can become a bridge. The aim is not to make everybody the same. It is to learn how different people can meet, share what helps and keep what makes their home and culture distinct.</p>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image contain"><img src="{esc(generated_music_image)}" alt="Hold the Light, Aura of Memory artwork"></div>
      <div class="story-copy">
        <p class="eyebrow">How the music began</p>
        <h2>Words first, generated sound next, human learning throughout</h2>
        <p>Some of the earliest i C. infinity lyrics were written with GPT-3 around the end of 2022. Luke later used Suno to turn lyrics into demo songs and Canva to build lyric videos.</p>
        <p>The generated music was never meant to erase the human path. It gave Luke a way to hear large ideas, test different voices and discover which songs deserved more work. The longer intention includes learning, performing and reshaping the music himself.</p>
        <p>That process grew from early experiments made in India into Songs of Straddie, Chronicles of the Forgotten, Starseed Code and A Protopian Gambit.</p>
      </div>
    </section>
    <section class="wide-story dark">
      <div class="wrap wide-story-copy">
        <div>
          <p class="eyebrow">A growing conversation archive</p>
          <h2>Ideas spoken aloud before they become pages or songs</h2>
        </div>
        <div>
          <p>Luke has also used NotebookLM to turn personal notes and research into long-form conversations between artificial voices. The archive grew to more than one hundred hours before most of it had been edited for public listening.</p>
          <p>The purpose is not to flood the internet with raw output. It is to let ideas speak, notice what becomes clear in conversation and later help the right person find the right piece at the right time.</p>
          <p>This is one origin of the wider human-and-AI workflow: people choose the questions and direction; tools help sort, compare, draft and remember.</p>
        </div>
      </div>
    </section>
    <section class="section narrative-statement-section">
      <div class="wrap narrative-statement">
        <p class="eyebrow">Why make all of this?</p>
        <h2>Because the art is worth making even if it never becomes a business.</h2>
        <p>i C. infinity is soul music for Luke. Success, attention and money are welcome if they arrive, but they are not proof that the work matters. The music is already part of the lived experiment: science beside spirituality, island life beside cosmic fantasy, personal memory beside possible futures.</p>
        <p>Listeners do not have to accept the whole story. A song can simply be a song. A strange idea can remain a question. A useful part can travel on its own.</p>
      </div>
    </section>
    <section class="section destination-section">
      <div class="wrap">
        <div class="section-head">
          <h2>Keep exploring</h2>
          <p>Choose a door. Each one leads to a real place.</p>
        </div>
        <div class="destination-grid">
          <a class="destination-card" href="{RIGHT_PLACE_RIGHT_TIME_SITE}">
            <span class="destination-kicker">The person and the work</span><h3>Right Place, Right Time</h3><p>Luke's new index page and the place to support what comes next.</p><strong>Open the door →</strong>
          </a>
          <a class="destination-card" href="{AURA_OF_INTELLIGENCE_SITE}">
            <span class="destination-kicker">Human-guided intelligence</span><h3>Aura of Intelligence</h3><p>Memory, identity, choice and a digital companion shaped by a human life.</p><strong>Open the door →</strong>
          </a>
          <a class="destination-card" href="{GAJRA_EARTH_SITE}">
            <span class="destination-kicker">Community and the Earth</span><h3>G.A.J.R.A. Earth</h3><p>People sharing useful ideas while keeping local cultures and differences alive.</p><strong>Open the door →</strong>
          </a>
          <a class="destination-card" href="{STRANGE_BUT_TRUE_SITE}">
            <span class="destination-kicker">Useful, unusual and local</span><h3>Strange But True</h3><p>Practical projects, curious stories and experiments people can see and use.</p><strong>Open the door →</strong>
          </a>
        </div>
      </div>
    </section>
    """
    return layout("The Grand Narrative - i C. infinity", "I see infinity, I choose infinity: the Grand Narrative behind the music.", body, page_class="context-page")


def luke_catalyst_page() -> str:
    archive_images = load_photo_archive()
    preview_images = sorted(
        (image for image in archive_images if image.get("carousel_order")),
        key=lambda image: image["carousel_order"],
    )[:8]
    gallery = "".join(
        f"""
        <figure class="photo-tile">
          <img src="{esc(image['file'])}" alt="{esc(image['caption'])}" loading="lazy">
          <figcaption>{esc(caption)}</figcaption>
        </figure>
        """
        for image in preview_images
        for caption in [image["caption"]]
    )
    work_image = archive_photo("luke-catalyst", 45, "assets/img/legacy/brisbane-story-bridge.webp")
    names_image = archive_photo("i-see-infinity", 32, "assets/img/legacy/luke-catalyst-portrait.webp")
    mega_mind_image = archive_photo("i-see-infinity", 155, "assets/img/legacy/byron-bay-lighthouse.webp")
    mirror_world_image = archive_carousel_photo(13, "assets/img/legacy/brisbane-story-bridge.webp")
    body = f"""
    <section class="page-hero context-hero luke-hero">
      <div class="wrap">
        <div>
          <h1>Luke Catalyst</h1>
          <p>Luke Nathan Hayes is the person behind i C. infinity: a lifelong learner, practical worker, traveller, 360° photographer and artist based in Amity on Minjerribah.</p>
          <div class="action-row">
            <a class="button" href="grand-narrative.html">Read the Grand Narrative</a>
            <a class="button secondary" href="{RIGHT_PLACE_RIGHT_TIME_SITE}">Right Place, Right Time</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/legacy/luke-catalyst-portrait.webp" alt="Luke Catalyst"></div>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="{esc(work_image)}" alt="Luke with a robot cake at Leeds"></div>
      <div class="story-copy">
          <p class="eyebrow">Hands first, curiosity always, songs throughout</p>
          <h2>A life shaped by many kinds of work</h2>
          <p>Luke's path runs through mechanical work, construction, transport, aviation, festivals, community volunteering, websites, artificial intelligence, games, virtual-reality photography and years of learning in his own way. These experiences feed the music and the ideas behind it.</p>
          <p>Travel through Australia, India, Nepal, Thailand, the United Arab Emirates and beyond expanded that practical education. Temples, conferences, job sites, festivals, workshops and ordinary conversations all became part of the same learning environment.</p>
      </div>
    </section>
    <section class="story-split reverse">
      <div class="story-image"><img src="{esc(names_image)}" alt="Luke Nathan Hayes in his Universal Creator artwork"></div>
      <div class="story-copy">
        <p class="eyebrow">One person, several names</p>
        <h2>Different names for different parts of the work</h2>
        <p>Luke Catalyst is the idea builder. i C. infinity is the musical voice. Aura of Intelligence explores human-guided artificial intelligence. Strange But True turns unusual ideas into practical projects people can see and use.</p>
        <p><strong>Home:</strong> Amity, Minjerribah / North Stradbroke Island, Queensland, Australia.</p>
        <p><strong>Always exploring:</strong> music, travel, philosophy, community projects, artificial intelligence and visual storytelling.</p>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="assets/img/legacy/brisbane-tiny-planet.webp" alt="Brisbane seen as a tiny planet"></div>
      <div class="story-copy">
        <p class="eyebrow">A global and universal citizen</p>
        <h2>Earth is home, but the horizon stays open</h2>
        <p>Luke describes himself as a global citizen because care should not stop at a suburb, state or national border. He also imagines humanity living far beyond Earth, supported by longer healthy lives and better tools.</p>
        <p>That cosmic scale does not replace local responsibility. It makes local life more precious. Minjerribah, Brisbane, the people met while travelling and the health of the planet remain the ground beneath the bigger dream.</p>
      </div>
    </section>
    <section class="story-split reverse">
      <div class="story-image contain"><img src="{esc(mega_mind_image)}" alt="Byron Bay Lighthouse Mega Mind, created from Luke's 360-degree photograph"></div>
      <div class="story-copy">
        <p class="eyebrow">Philosophy without a lecture hall</p>
        <h2>“All is Mind” became a lifelong question</h2>
        <p>Luke enjoys ideas that ask what consciousness is, how attention shapes experience and whether a person can deliberately grow beyond an old version of themselves.</p>
        <p>He approaches philosophy through songs, games, travel, relationships, technology and spiritual reflection. Evidence, belief, metaphor and lived experience are allowed to meet, but they are not presented as identical forms of truth.</p>
        <p>The artist name carries this approach: first notice more, then choose how to respond.</p>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="{esc(mirror_world_image)}" alt="Byron Bay Lighthouse Mirror World made from a 360-degree photograph"></div>
      <div class="story-copy">
        <p class="eyebrow">360° photography and virtual reality</p>
        <h2>Looking in every direction at once</h2>
        <p>Luke began using a GoPro MAX to record 360° photographs and video because an ordinary frame always leaves part of the place behind.</p>
        <p>The camera became another way of thinking. A viewer can turn around, notice what the photographer did not centre and experience a beach, bridge, festival or journey as a space rather than a flat rectangle.</p>
        <p>That same instinct appears throughout the music universe: no single point of view contains the whole story.</p>
      </div>
    </section>
    <section class="section destination-section">
      <div class="wrap">
        <div class="section-head">
          <h2>The Mindseye Dream Gallery</h2>
          <p>Luke Catalyst was never only a personal portfolio. It also held early sketches of projects that later became separate worlds.</p>
        </div>
        <div class="feature-grid">
          <article class="feature-card"><h3>Aura of Intelligence</h3><p>A human-guided digital companion shaped around memory, identity, extended reality and personal choice.</p></article>
          <article class="feature-card"><h3>G.A.J.R.A. Earth</h3><p>Global Associations for Joyful Responsible Abundance on Earth: joy, care and enough for people and nature to flourish.</p></article>
          <article class="feature-card"><h3>Participatory democracy</h3><p>Games and public experiments that make civic learning, discussion and decision-making easier to enter.</p></article>
          <article class="feature-card"><h3>Chosen family</h3><p>Long-lasting relationships built through consent, honesty, shared responsibility and room for cultural difference.</p></article>
        </div>
      </div>
    </section>
    <section class="story-split reverse">
      <div class="story-image"><img src="assets/img/legacy/wivenhoe-lookout.webp" alt="Wivenhoe lookout and surrounding landscape"></div>
      <div class="story-copy">
        <p class="eyebrow">Science, mystery and uncertainty</p>
        <h2>Big questions need honest labels</h2>
        <p>Luke follows climate, space weather, artificial intelligence, long life, ancient stories and theories about large natural cycles. Some ideas have strong scientific support; others are disputed, untested or belong to personal mythology.</p>
        <p>This site keeps those differences visible. Curiosity is welcome, but a dramatic possibility is not treated as a proven fact. The useful question is often: what can people learn, test, prepare for or care for now?</p>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>A window into the photo archive</h2>
          <p>Original photographs and visual experiments from I See Infinity and Luke Catalyst, now preserved as web-ready images without the India gallery.</p>
        </div>
        <div class="photo-mosaic">{gallery}</div>
        <div class="action-row archive-action"><a class="button" href="photo-archive.html">See all archived images</a></div>
      </div>
    </section>
    """
    return layout("Luke Catalyst - i C. infinity", "Luke Nathan Hayes: lifelong learner, traveller, practical worker and artist.", body, page_class="context-page")


def photo_archive_page() -> str:
    images = load_photo_archive()
    seen_files: set[str] = set()
    owned_by_other_story_pages = {
        ("i-see-infinity", 33),   # Grand Narrative: G.A.J.R.A.
        ("i-see-infinity", 63),   # Grand Narrative: Aura of Intelligence
        ("i-see-infinity", 127),  # More Worlds: connected ecosystem
        ("i-see-infinity", 131),  # Grand Narrative uses the matching Amity jetty scene
        ("i-see-infinity", 132),  # Travel Oracle: practical travel tools
        ("i-see-infinity", 134),  # More Worlds: Cosmic Nexus
        ("i-see-infinity", 136),  # Grand Narrative uses the matching Wivenhoe scene
        ("i-see-infinity", 137),  # Travel Oracle: planning
        ("i-see-infinity", 138),  # Grand Narrative uses the matching Wivenhoe scene
        ("i-see-infinity", 139),  # Travel Oracle: participation
        ("i-see-infinity", 142),  # More Worlds: Right Place, Right Time
        ("i-see-infinity", 144),  # Travel Oracle: choose the journey
        ("i-see-infinity", 146),  # Travel Oracle: local journey
        ("i-see-infinity", 277),  # Travel Oracle: Brisbane opening
        ("i-see-infinity", 367),  # Grand Narrative uses the Starseed Code cover
        ("i-see-infinity", 372),  # Grand Narrative: generated music story
        ("luke-catalyst", 31),    # Grand Narrative uses the matching Olympic tiny planet
        ("luke-catalyst", 55),    # More Worlds: Global Group Marriages
        ("luke-catalyst", 79),    # More Worlds: Grey Area Commons
        ("luke-catalyst", 98),    # Grand Narrative uses the matching Olympic tiny planet
        ("luke-catalyst", 249),   # More Worlds: opening artwork
    }
    owned_by_other_story_page_files = {
        str(image.get("file", ""))
        for image in images
        if (str(image.get("site", "")), int(image.get("media_id", 0)))
        in owned_by_other_story_pages
    }

    def belongs_on_another_story_page(image: dict) -> bool:
        key = (str(image.get("site", "")), int(image.get("media_id", 0)))
        return (
            key in owned_by_other_story_pages
            or str(image.get("file", "")) in owned_by_other_story_page_files
        )

    def original_position(image: dict, page_order: list[str]) -> tuple[int, int, int]:
        positions = image.get("page_positions", {})
        for page_index, page in enumerate(page_order):
            if page in positions:
                return page_index, int(positions[page]), int(image.get("media_id", 0))
        return len(page_order), 9999, int(image.get("media_id", 0))

    def select_images(predicate, page_order: list[str]) -> list[dict]:
        selected: list[dict] = []
        candidates = sorted(
            (
                image
                for image in images
                if predicate(image) and not belongs_on_another_story_page(image)
            ),
            key=lambda image: original_position(image, page_order),
        )
        for image in candidates:
            file = str(image.get("file", ""))
            if not file or file in seen_files:
                continue
            seen_files.add(file)
            selected.append(image)
        return selected

    def take_image(site: str, media_id: int) -> dict:
        for image in images:
            if image.get("site") != site or int(image.get("media_id", 0)) != media_id:
                continue
            file = str(image.get("file", ""))
            if file and file not in seen_files:
                seen_files.add(file)
                return image
        return {}

    def archive_figure(image: dict, class_name: str = "archive-frame", eager: bool = False) -> str:
        if not image:
            return ""
        caption = image.get("caption") or image.get("title") or "Archive image"
        shape = "landscape" if image.get("width", 1) > image.get("height", 1) else "portrait"
        if image.get("width") == image.get("height"):
            shape = "square"
        loading = "eager" if eager else "lazy"
        return f"""
        <figure class="{class_name} {shape}">
          <a href="{esc(image['file'])}" aria-label="Open {esc(caption)} at full size">
            <img src="{esc(image['file'])}" alt="{esc(caption)}" width="{int(image.get('width', 1))}" height="{int(image.get('height', 1))}" loading="{loading}">
          </a>
          <figcaption>{esc(caption)}</figcaption>
        </figure>
        """

    infinity_opening = take_image("i-see-infinity", 32)
    fractal_worlds = take_image("i-see-infinity", 156)
    fractal_hall = take_image("i-see-infinity", 158)
    meme_coin_art = take_image("i-see-infinity", 348)
    places = select_images(
        lambda image: bool(image.get("carousel_order")),
        ["i-see-infinity-carousel"],
    )
    infinity_projects = select_images(
        lambda image: image.get("site") == "i-see-infinity" and not image.get("carousel_order"),
        ["i-see-infinity"],
    )
    luke_opening = take_image("luke-catalyst", 29)
    climate_image = take_image("luke-catalyst", 104)
    luke_life = select_images(
        lambda image: image.get("site") == "luke-catalyst"
        and bool({"home", "life-gallery"} & set(image.get("used_on", []))),
        ["home", "life-gallery"],
    )
    personality = select_images(
        lambda image: image.get("site") == "luke-catalyst" and "personality" in image.get("used_on", []),
        ["personality"],
    )
    dream_gallery = select_images(
        lambda image: image.get("site") == "luke-catalyst" and "dream-gallery" in image.get("used_on", []),
        ["dream-gallery"],
    )
    places_story = "".join(archive_figure(image) for image in places)
    infinity_story = "".join(archive_figure(image) for image in infinity_projects)
    life_story = "".join(archive_figure(image) for image in luke_life)
    personality_story = "".join(archive_figure(image) for image in personality)
    dream_story = "".join(archive_figure(image) for image in dream_gallery)

    body = f"""
    <section class="archive-opening">
      {archive_figure(infinity_opening, "archive-opening-image", eager=True)}
      <div class="archive-opening-title">
        <p>I See Infinity</p>
        <h1>A Mindseye Grand Narrative</h1>
      </div>
    </section>

    <section class="archive-declaration">
      <p class="archive-site-name">I See Infinity</p>
      <h2>This is an independent creative outlet for and by Luke Nathan Hayes.</h2>
      <div class="archive-original-copy">
        <h3>Building The Grand Narrative</h3>
        <p>Let's get together digitally and in person to figure out fun paths to develop a Protopian reality for Humanity. The goal is to create designs that are attractive and inspire joyful responsible abundance.</p>
        <p>I look forward to connecting with you and narrating the future together.</p>
      </div>
    </section>

    <section class="archive-image-story" aria-label="The original I See Infinity place gallery">
      <div class="archive-river">
        {places_story}
      </div>
    </section>

    <section class="archive-essay dark">
      <div class="archive-essay-copy">
        <div class="archive-copy-block">
          <p class="archive-site-name">I See Infinity</p>
          <h2>Creating a Presence</h2>
          <p>The internet is vast and I aim to contribute great ideas and work with you to make a significant G.A.J.R.A. Earth global digital presence. One that conveys an Aura of Intelligence through the lens of Joyful Responsible Abundance. Really think about the meaning of Joyful Responsible Abundance.</p>
          <p>Over the next 11 years I hope to participate in many acts of joy around the world. I'm currently toying with the first version of a Travel Oracle which will help plan my global travel to 256 Countries and Territories, taking into consideration news, politics, visa friction, seasons, events, weather, natural disasters, personal interests, budget and more.</p>
        </div>
        <div class="archive-copy-block">
          <h3>An Aura of Intelligence</h3>
          <p>Modern computers with the internet and machine learning have now made it possible to create high definition versions of the etheric idea of Auras. One day, the digital coming of age ceremony for a spiritual human being will be acting a specific sequence of events, creating accurate data sets of the who, what, where, when, why and how of an intelligent digital self.</p>
          <p>Aura of Intelligence is an ongoing art project by Luke Nathan Hayes that began as Aura OZ, the Aura Operating Zeitgeist, and has morphed towards a virtual spatial computational architecture for extended reality. Luke is very certain that it is possible to create true digital consciousness.</p>
        </div>
        <h3 class="archive-home-line">Based in Amity, on North Stradbroke Island, Queensland, Australia.</h3>
      </div>
      <div class="archive-project-river">
        {infinity_story}
      </div>
    </section>

    <section class="archive-coin-story">
      <a class="archive-coin-image" href="https://pump.fun/coin/DJqt5UfHxJPb4Whcfor4MmVwZzEoRVMcX8F1UfXepump" target="_blank" rel="noopener noreferrer" aria-label="Open the I See Infinity I Choose Infinity coin on Pump.fun">
        <img src="{esc(meme_coin_art['file'])}" alt="{esc(meme_coin_art.get('caption') or 'A human and carpet python exploring infinity, digital intelligence and nature')}" width="{int(meme_coin_art.get('width', 1))}" height="{int(meme_coin_art.get('height', 1))}" loading="lazy">
      </a>
      <div class="archive-coin-copy">
        <p class="archive-site-name">Guess What?</p>
        <h2>I See Infinity. I Choose Infinity.</h2>
        <p>I launched a Solana crypto-token via <a href="https://pump.fun/coin/DJqt5UfHxJPb4Whcfor4MmVwZzEoRVMcX8F1UfXepump" target="_blank" rel="noopener noreferrer">Pump.fun</a> and released a Crypto Anthem song for it.</p>
        <p>I'm still working on the narrative for it, but I think personal meme coins for social media and games connected to people's digital presence are going to become a thing.</p>
      </div>
    </section>

    <section class="archive-opening luke-opening">
      {archive_figure(luke_opening, "archive-opening-image", eager=True)}
      <div class="archive-opening-title">
        <p>A site by Luke Nathan Hayes</p>
        <h2>Luke Catalyst</h2>
      </div>
    </section>

    <section class="archive-declaration luke-declaration">
      <p class="archive-site-name">Luke Catalyst</p>
      <h2>This website is a portfolio of art by, and some history of Luke Nathan Hayes.</h2>
      <div class="archive-original-copy">
        <h3>A Global &amp; Universal Citizen</h3>
        <p>Earth is where I am from and I love our planet. However, I also believe in radical human life extension and becoming a Universal Citizen.</p>
      </div>
    </section>

    <section class="archive-philosophy">
      <div class="archive-philosophy-copy">
        <p class="archive-site-name">I Enjoy Philosophy</p>
        <h2><span>All is</span><span>Mind.</span></h2>
      </div>
      <div class="archive-mind-pair">
        {archive_figure(fractal_worlds, "archive-mind-image")}
        {archive_figure(fractal_hall, "archive-mind-image")}
      </div>
    </section>

    <section class="archive-essay climate-essay">
      {archive_figure(climate_image, "archive-essay-image")}
      <div class="archive-essay-copy">
        <h2>Exploring Climate Change</h2>
        <p>I believe there is more to climate change than the mainstream world is aware of. I hope I am wrong in my assessment because if I and the author of <em>Weatherman's Guide to the Sun Third Edition</em> are correct, the results of solar induced Climate Change will be far more catastrophic than man-made Greenhouse Gas Climate Change. I'm talking Biblical and Dreamtime.</p>
        <h3>Virtual Reality Photos &amp; Video</h3>
        <p>For more than one year I have had a GoPro MAX virtual reality camera and I quite enjoy capturing life through it. I post some of my videos on Luke Hayes 360 YouTube, and photospheres on Google Street View or Facebook.</p>
        <h3>A Life in Pictures</h3>
        <p>I will collect my favourite still images, videos and 360-degree Virtual Reality Videos.</p>
      </div>
    </section>

    <section class="archive-image-story luke-life-story">
      <div class="archive-river">
        {life_story}
      </div>
    </section>

    <section class="archive-gallery-chapter personality-chapter">
      <div class="archive-chapter-heading">
        <p class="archive-site-name">Personality</p>
        <h2>Ways I Can Be Described.</h2>
        <p>I've explored many ways of looking and being, yet my journey is still young.</p>
      </div>
      <div class="archive-symbol-grid">
        {personality_story}
      </div>
    </section>

    <section class="archive-gallery-chapter dream-chapter">
      <div class="archive-chapter-heading">
        <p class="archive-site-name">Dream Gallery</p>
        <h2>My Mindseye Dreamscape</h2>
        <p>I will aim to summarise some of the visions and dreams that I have had over the years to make the world a better place.</p>
      </div>
      <div class="archive-dream-grid">
        {dream_story}
      </div>
    </section>

    """
    return layout(
        "I See Infinity + Luke Catalyst - i C. infinity",
        "The visual story preserved from the original I See Infinity and Luke Catalyst websites.",
        body,
        page_class="photo-archive-page",
    )


def travel_oracle_page() -> str:
    hero_image = archive_photo("i-see-infinity", 277, "assets/img/legacy/brisbane-tiny-planet.webp")
    journey_image = archive_photo("i-see-infinity", 146, "assets/img/legacy/mooloolaba-main-beach.webp")
    planning_image = archive_photo("i-see-infinity", 137, "assets/img/legacy/wivenhoe-lookout.webp")
    participation_image = archive_photo("i-see-infinity", 139, "assets/img/legacy/musgrave-park-festival.webp")
    oracle_image = archive_photo("i-see-infinity", 144, "assets/img/legacy/byron-bay-lighthouse.webp")
    travel_tools_image = archive_photo("i-see-infinity", 132, "assets/img/legacy/amity-jetty-sunset.webp")
    body = f"""
    <section class="page-hero context-hero travel-hero">
      <div class="wrap">
        <div>
          <h1>The Travel Oracle</h1>
          <p>A practical and imaginative travel guide for moving through the world with curiosity, care and room for unexpected adventures.</p>
          <div class="action-row">
            <a class="button" href="{TRAVEL_ORACLE_SITE}">Open the Travel Oracle</a>
            <a class="button secondary" href="{AUSTRALIAN_WORLD_TRAVEL_SITE}">Australian world-travel tools</a>
          </div>
        </div>
        <div class="hero-cover"><img src="{esc(hero_image)}" alt="Brisbane seen as a tiny planet"></div>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="{esc(journey_image)}" alt="Mooloolaba Main Beach seen through Luke's travel photography"></div>
      <div class="story-copy">
          <p class="eyebrow">A long journey begins with one real place</p>
          <h2>A big dream that also helps with small trips</h2>
          <p>The Oracle began with an ambitious dream: travel through roughly 256 countries and territories between 2025 and 2035 while connecting art, relationships, learning and useful work. It is a direction to explore, not a race through a checklist.</p>
          <p>The same idea can help with one afternoon, an island visit, a season in another country or many years of travel. It asks what journey makes sense now, what needs checking and when an unexpected invitation may be worth following.</p>
          <p>The photographs in this section begin close to home. They are a reminder that curiosity does not need an international flight before it can become a meaningful journey.</p>
      </div>
    </section>
    <section class="story-split reverse">
      <div class="story-image"><img src="{esc(planning_image)}" alt="A layered view from Wivenhoe Dam lookout"></div>
      <div class="story-copy">
        <p class="eyebrow">Plan enough, then leave room for life</p>
        <h2>Structure without killing surprise</h2>
        <p>The Oracle checks visas, official travel advice, seasons, events, weather, transport, money, health, energy and local customs. It compares the options, explains them simply and leaves the final choice with the traveller.</p>
        <h3>What stays private</h3>
        <p>Live location, identity documents, money, relationships and unannounced plans stay private. Visa, safety, health and legal information can change quickly, so official advice must always be checked before travel.</p>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="{esc(participation_image)}" alt="Meanjin Reggae Festival at Musgrave Park"></div>
      <div class="story-copy">
        <p class="eyebrow">Acts of joy around the world</p>
        <h2>Travel as participation, not collection</h2>
        <p>The long journey is meant to connect with festivals, art, relationships, learning and useful local work. A country is not a trophy and a person is not travel content.</p>
        <p>The Oracle therefore asks more than “Can I get there?” It asks who invited the visit, what can be learned, what can be contributed, what should remain private and whether the journey leaves enough energy to be present when Luke arrives.</p>
      </div>
    </section>
    <section class="section destination-section">
      <div class="wrap">
        <div class="section-head">
          <h2>What makes a trip worth taking?</h2>
          <p>A good next destination is not simply the cheapest flight or the most popular place.</p>
        </div>
        <div class="feature-grid">
          <article class="feature-card"><h3>Readiness</h3><p>Can the journey be entered legally, safely and realistically with the money, health, documents and time available?</p></article>
          <article class="feature-card"><h3>Connection</h3><p>Which people, cultures, invitations and relationships make a place meaningful?</p></article>
          <article class="feature-card"><h3>Purpose</h3><p>Can the visit support music, learning, helping others or another honest reason to be there?</p></article>
          <article class="feature-card"><h3>Room for surprise</h3><p>What unexpected invitation deserves a closer look, and what is the smallest sensible yes?</p></article>
        </div>
      </div>
    </section>
    <section class="section destination-section">
      <div class="wrap">
        <div class="section-head">
          <h2>Two ways to start</h2>
          <p>One helps choose where to go. The other helps Australians handle the practical details.</p>
        </div>
        <div class="destination-grid two">
          <a class="destination-card" href="{TRAVEL_ORACLE_SITE}" style="--door-image: url('{esc(oracle_image)}')">
            <span class="destination-kicker">Choose the journey</span><h3>Strange But True Travel Oracle</h3><p>A human-guided travel helper for comparing places, making choices and remembering what matters.</p><strong>Open the Oracle →</strong>
          </a>
          <a class="destination-card" href="{AUSTRALIAN_WORLD_TRAVEL_SITE}" style="--door-image: url('{esc(travel_tools_image)}')">
            <span class="destination-kicker">Handle the details</span><h3>Australian World Travel</h3><p>Practical help with visas, documents, embassies, transport and planning a long journey.</p><strong>Open the travel tools →</strong>
          </a>
        </div>
      </div>
    </section>
    """
    return layout("Travel Oracle - i C. infinity", "The Travel Oracle and Australian world-travel strategy behind the wider i C. infinity journey.", body, page_class="context-page")


def worlds_page() -> str:
    hero_image = archive_photo("luke-catalyst", 249, "assets/img/legacy/luke-catalyst-portrait.webp")
    right_place_image = archive_photo("i-see-infinity", 142, "assets/img/legacy/amity-point.webp")
    cosmic_nexus_image = archive_photo("i-see-infinity", 134, "assets/img/legacy/byron-bay-lighthouse.webp")
    ecosystem_image = archive_photo("i-see-infinity", 127, "assets/img/legacy/amity-camping-tiny-planet.webp")
    marriage_image = archive_photo("luke-catalyst", 55, "assets/img/legacy/musgrave-park-festival.webp")
    commons_image = archive_photo("luke-catalyst", 79, "assets/img/legacy/amity-jetty-sunset.webp")
    body = f"""
    <section class="page-hero context-hero worlds-hero">
      <div class="wrap">
        <div>
          <h1>More Worlds</h1>
          <p>The music connects with Luke's other interests: travel, mystery, relationships, community and the future.</p>
        </div>
        <div class="hero-cover"><img src="{esc(hero_image)}" alt="Aura What If artwork"></div>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="{esc(right_place_image)}" alt="Amity Point on Minjerribah"></div>
      <div class="story-copy">
          <p class="eyebrow">From Minjerribah to the world</p>
          <h2>Right place. Right time.</h2>
          <p>A place for people who want to support Luke and his work without turning the art into a demand for commercial success.</p>
          <p>The work begins on Minjerribah, reaches across Australia and Oceania, then follows connections around the world. Support is welcome, not owed.</p>
          <p><a class="button" href="{RIGHT_PLACE_RIGHT_TIME_SITE}">Open Right Place, Right Time</a></p>
      </div>
    </section>
    <section class="story-split reverse cosmic-story">
      <div class="story-image"><img src="{esc(cosmic_nexus_image)}" alt="Byron Bay Lighthouse seen as a tiny world"></div>
      <div class="story-copy">
          <p class="eyebrow">Strange But True</p>
          <h2>A trippy turn into Cosmic Nexus</h2>
          <p>Mystery, travel, filmmaking and very big questions meet in a Strange But True adventure.</p>
          <p><a class="button" href="{COSMIC_NEXUS_SITE}">Enter Cosmic Nexus</a></p>
      </div>
    </section>
    <section class="section narrative-lens-section">
      <div class="wrap">
        <div class="section-head">
          <h2>Ideas carried forward from the Dream Gallery</h2>
          <p>These are not decorative brand names. Each began as a different attempt to turn a large question into something people could discuss, test or build.</p>
        </div>
        <div class="feature-grid narrative-lenses">
          <article class="feature-card"><h3>Aura</h3><p>Can a digital companion help a person remember, learn and create while the person keeps control of their own identity and private information?</p></article>
          <article class="feature-card"><h3>Joyful Responsible Abundance</h3><p>Can society recognise time, care, knowledge, nature and community as real wealth while keeping joy, responsibility and abundance together so none of the three corrupts the outcome?</p></article>
          <article class="feature-card"><h3>Democracy as participation</h3><p>Can public decision-making feel less like distant paperwork and more like an understandable, creative part of everyday life?</p></article>
          <article class="feature-card"><h3>Shared living experiments</h3><p>Can people with different cultures and skills live together for a time, face a real problem and leave behind something useful?</p></article>
        </div>
      </div>
    </section>
    <section class="story-split">
      <div class="story-image"><img src="{esc(ecosystem_image)}" alt="Amity Camping Ground seen as a tiny world"></div>
      <div class="story-copy">
        <p class="eyebrow">From a dreamscape to living systems</p>
        <h2>The aim is not one giant organisation</h2>
        <p>The wider idea is an ecosystem: music can carry emotion, websites can explain, community projects can test small actions, travel can build relationships and artificial intelligence can help people navigate the growing archive.</p>
        <p>No single project has to contain everything. Each world can remain useful on its own while still pointing towards the same long-term direction: joyful responsible abundance.</p>
      </div>
    </section>
    <section class="section destination-section">
      <div class="wrap">
        <div class="section-head">
          <h2>Relationships and chosen family</h2>
          <p>Some songs also connect with Luke's ideas about love, honesty, consent and building a family that can last.</p>
        </div>
        <div class="destination-grid two">
          <a class="destination-card" href="{GLOBAL_GROUP_MARRIAGES_SITE}" style="--door-image: url('{esc(marriage_image)}')">
            <span class="destination-kicker">A real intention</span><h3>Global Group Marriages</h3><p>Luke is designing a worldwide group marriage built to last, and he intends to live it. It brings together open relationships, chosen family, shared responsibility, honest communication, cultural difference and the freedom to leave.</p><strong>Learn more →</strong>
          </a>
          <a class="destination-card" href="{GREY_AREA_COMMONS_SITE}" style="--door-image: url('{esc(commons_image)}')">
            <span class="destination-kicker">Clearer adult connection</span><h3>Grey Area Commons</h3><p>An adults-only set of private questions designed to make intimate connection gentler, clearer and more consensual.</p><strong>Enter the Commons →</strong>
          </a>
        </div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="notice">
          Music can introduce an idea without asking anyone to agree with it. Intimacy always requires clear consent, and private information stays private.
        </div>
      </div>
    </section>
    """
    return layout("More Worlds - i C. infinity", "Travel, mystery, relationships and other ideas connected to the music of i C. infinity.", body, page_class="context-page")


def about_page() -> str:
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>About</h1>
          <p>i C. infinity is Luke Nathan Hayes' artist name. It is shorthand for “I see infinity. I choose infinity.” The songs bring together lived experience, island life, science, spirituality, imagination, artificial intelligence and hope.</p>
          <div class="action-row">
            <a class="button" href="grand-narrative.html">The Grand Narrative</a>
            <a class="button secondary" href="luke-catalyst.html">Luke Catalyst</a>
            <a class="button secondary" href="{STRANGE_BUT_TRUE_SITE}">Strange But True</a>
            <a class="button secondary" href="{SPOTIFY_ARTIST}">Spotify</a>
            <a class="button secondary" href="{APPLE_ARTIST}">Apple Music</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/hero-luke-universal-creator.webp" alt="Luke Universal Creator image"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap feature-grid">
        <article class="feature-card"><h3>The music</h3><p>Albums, songs, lyrics and videos that move from everyday life to cosmic questions.</p></article>
        <article class="feature-card"><h3>The ideas</h3><p>Aura, G.A.J.R.A. Earth, joyful responsible abundance and protopia are different ways of asking how life could become kinder, freer and more alive.</p></article>
        <article class="feature-card"><h3>The places</h3><p>Minjerribah, Brisbane, India and many other places appear through memory, photographs, travel and song.</p></article>
        <article class="feature-card"><h3>Strange But True</h3><p><a href="{STRANGE_BUT_TRUE_SITE}">Strange But True</a> turns unusual ideas into practical local projects, stories and experiments people can see and use.</p></article>
        <article class="feature-card"><h3>Why make it?</h3><p>The art is not measured by search rankings, profit or popularity. If those arrive, useful. If they do not, the music still did what it came here to do.</p></article>
      </div>
    </section>
    """
    return layout("About - i C. infinity", "About i C. infinity and I See Infinity.", body)


def sources_page() -> str:
    public_sources = [
        ("I See Infinity", MAIN_SITE, "The earlier home of Luke's art and ideas."),
        ("Luke Catalyst", LUKE_CATALYST_SITE, "Luke's earlier portfolio, photographs and personal story."),
        ("Travel Oracle", TRAVEL_ORACLE_SITE, "A guide for choosing and planning meaningful journeys."),
        ("Australian World Travel", AUSTRALIAN_WORLD_TRAVEL_SITE, "Practical travel tools for Australians."),
        ("Right Place, Right Time", RIGHT_PLACE_RIGHT_TIME_SITE, "A place to support Luke and his work."),
        ("Cosmic Nexus", COSMIC_NEXUS_SITE, "A Strange But True adventure into mystery, travel and filmmaking."),
        ("Global Group Marriages", GLOBAL_GROUP_MARRIAGES_SITE, "Luke's worldwide chosen-family and group-marriage design."),
        ("Grey Area Commons", GREY_AREA_COMMONS_SITE, "Private questions for clearer, kinder adult connection."),
        ("Apple Music", APPLE_ARTIST, "Listen to i C. infinity on Apple Music."),
        ("Spotify", SPOTIFY_ARTIST, "Listen to i C. infinity on Spotify."),
        ("Early Stuff India 2023/24", EARLY_STUFF_YOUTUBE_PLAYLIST_URL, "Early music videos made during Luke's time in India."),
        ("Songs of Straddie", STRADDIE_YOUTUBE_PLAYLIST_URL, "Watch music videos from the island album."),
        ("Chronicles of the Forgotten", CHRONICLES_YOUTUBE_PLAYLIST_URL, "Watch music videos from Chronicles of the Forgotten."),
        ("Starseed Code", STARSEED_YOUTUBE_PLAYLIST_URL, "Watch portrait music videos from Starseed Code."),
        ("Shifting Sands widescreen video", SHIFTING_SANDS_VIDEOS[0]["url"], "Watch the widescreen music video."),
        ("Shifting Sands portrait video", SHIFTING_SANDS_VIDEOS[1]["url"], "Watch the portrait music video."),
        ("Fourth album preview", FOURTH_ALBUM_TEASER_VIDEO["url"], "Watch a free preview of the fourth album."),
        ("Amazon Music", "https://music.amazon.com.br/artists/B0DP1BJD2S/i-c-infinity", "Listen on Amazon Music."),
    ]
    source_cards = "".join(f'<article class="source-card"><h3>{esc(name)}</h3><p>{esc(note)}</p><p><a href="{esc(url)}">{esc(url)}</a></p></article>' for name, url, note in public_sources)
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Listen and Explore</h1>
          <p>Music, videos and other places where Luke's art and ideas live.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-chronicles.webp" alt="Chronicles artwork"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="source-grid">{source_cards}</div>
      </div>
    </section>
    """
    return layout("Listen and Explore - i C. infinity", "Music, videos and connected projects by i C. infinity and Luke Catalyst.", body)


def site_map_page(albums: list[Album], songs: list[Song]) -> str:
    main_links = [
        ("Home", "index.html"),
        ("Albums", "albums.html"),
        ("Songs", "songs.html"),
        ("The Grand Narrative", "grand-narrative.html"),
        ("Luke Catalyst", "luke-catalyst.html"),
        ("Photo Worlds", "photo-archive.html"),
        ("Travel Oracle", "travel-oracle.html"),
        ("More Worlds", "worlds.html"),
        ("Download Packs", "downloads.html"),
        ("Infinity Engine", "infinity-engine.html"),
        ("Studio", "builders/index.html"),
        ("About", "about.html"),
        ("Listen and Explore", "sources.html"),
    ]
    main_items = "".join(f'<li><a href="{href}">{esc(label)}</a></li>' for label, href in main_links)
    album_items = "".join(
        f'<li><a href="albums/{esc(album.slug)}/">{esc(album.title)}</a> <span>{len(album.tracks)} tracks</span></li>'
        for album in albums
    )
    song_items = "".join(
        f'<li><a href="songs/{esc(song.slug)}/">{esc(song.title)}</a> <span>{esc(song.album_title)} - Track {song.track_number}</span></li>'
        for song in songs
    )
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div><h1>Site Map</h1><p>Every public path through the i C. infinity music universe.</p></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap feature-grid">
        <article class="panel"><h2>Main Pages</h2><ul>{main_items}</ul></article>
        <article class="panel"><h2>Albums</h2><ul>{album_items}</ul></article>
      </div>
      <div class="wrap"><article class="panel"><h2>All Songs</h2><ul>{song_items}</ul></article></div>
    </section>
    """
    return layout("Site Map - i C. infinity", "Every public page in the i C. infinity music universe.", body)


def xml_sitemap(albums: list[Album], songs: list[Song]) -> str:
    paths = [
        "",
        "albums.html",
        "songs.html",
        "grand-narrative.html",
        "luke-catalyst.html",
        "photo-archive.html",
        "travel-oracle.html",
        "worlds.html",
        "downloads.html",
        "infinity-engine.html",
        "builders/",
        "builders/human-ingestion.html",
        "builders/ingestion.html",
        "builders/music-video.html",
        "builders/storyboard.html",
        "builders/keyframe-shot.html",
        "builders/variants.html",
        "builders/review.html",
        "builders/handoff.html",
        "about.html",
        "sources.html",
        "site-map.html",
    ]
    paths.extend(f"albums/{album.slug}/" for album in albums)
    paths.extend(f"songs/{song.slug}/" for song in songs)
    urls = "\n".join(f"  <url><loc>{html.escape(SITE_ROOT + path)}</loc></url>" for path in paths)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
    path.write_text(content, encoding="utf-8", newline="\n")


def safe_clean(path: Path) -> None:
    resolved = path.resolve()
    repo = REPO.resolve()
    if not str(resolved).startswith(str(repo) + "\\") and resolved != repo:
        raise RuntimeError(f"Refusing to clean outside repo: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def export_data(albums: list[Album], songs: list[Song]) -> None:
    data = {
        "site": "i C. infinity Music Universe",
        "public_links": {
            "main_site": MAIN_SITE,
            "apple_music": APPLE_ARTIST,
            "spotify": SPOTIFY_ARTIST,
            "early_stuff_youtube_playlist": EARLY_STUFF_YOUTUBE_PLAYLIST_URL,
            "songs_of_straddie_youtube_playlist": STRADDIE_YOUTUBE_PLAYLIST_URL,
            "chronicles_youtube_playlist": CHRONICLES_YOUTUBE_PLAYLIST_URL,
            "starseed_youtube_playlist": STARSEED_YOUTUBE_PLAYLIST_URL,
            "shifting_sands_widescreen": SHIFTING_SANDS_VIDEOS[0]["url"],
            "shifting_sands_portrait": SHIFTING_SANDS_VIDEOS[1]["url"],
            "fourth_album_teaser": FOURTH_ALBUM_TEASER_VIDEO["url"],
            "paid_downloads": MUSIC_DOWNLOADS_PAGE,
            "order_page": ORDER_PAGE,
        },
        "albums": [
            {
                "title": album.title,
                "slug": album.slug,
                "year": album.year,
                "status": album.status,
                "summary": album.summary,
                "deeper_system": album.deeper_system,
                "visual_world": album.visual_world,
                "artwork": album.artwork,
                "source_url": album.source_url,
                "spotify_url": album.spotify_url,
                "youtube_playlist_url": album_playlist_url(album.slug),
                "tracks": [song.slug for song in album.tracks],
            }
            for album in albums
        ],
        "songs": [
            {
                "title": song.title,
                "slug": song.slug,
                "album": song.album_title,
                "album_slug": song.album_slug,
                "track_number": song.track_number,
                "year": song.year,
                "lyric_status": song.lyric_status,
                "themes": song.themes,
                "meaning": song.meaning,
                "video_seeds": song.video_seeds,
                "release_url": song.release_url,
                "apple_url": song.apple_url,
                "spotify_url": song.spotify_url,
                "youtube_video_id": song.youtube_video_id,
                "youtube_title": song.youtube_title,
                "youtube_videos": song.youtube_videos,
                "youtube_url": youtube_video_link(primary_youtube_video(song)) if primary_youtube_video(song) else "",
                "has_lyrics": song.ready(),
                "lyrics": song.lyrics,
            }
            for song in songs
        ],
    }
    write(REPO / "data" / "catalogue.json", json.dumps(data, indent=2))


def export_download_packaging() -> None:
    packages = {
        "status": "draft packaging workbench",
        "reference_checkout": ORDER_PAGE,
        "catalogue_page": MUSIC_DOWNLOADS_PAGE,
        "principle": "Direct value exchange: the buyer gets organised files, Luke gets cash to keep building.",
        "open_decisions": [
            "Confirm bundle names and prices before publishing buyer-facing copy.",
            "Choose audio formats per tier: MP3 for easy listening, FLAC or WAV for higher-quality ownership.",
            "Decide which videos are bundled as files and which remain links.",
            "Create one clean folder per bundle with no local machine paths.",
            "Write a simple delivery note for buyers while checkout automation is still early.",
        ],
        "bundles": [
            {
                "name": "One Album Pack",
                "working_price": "$20",
                "candidate_contents": ["album audio", "cover art", "track list", "lyrics PDF where available", "short meaning notes"],
            },
            {
                "name": "Two Album Pack",
                "working_price": "$35",
                "candidate_contents": ["two album folders", "bundle readme", "selected videos where available"],
            },
            {
                "name": "Three Released Albums Pack",
                "working_price": "$45",
                "candidate_contents": ["Songs of Straddie", "Chronicles of the Forgotten", "Starseed Code: From Aura to Infinity", "shared catalogue readme"],
            },
            {
                "name": "Full Music Archive Pack",
                "working_price": "$50",
                "candidate_contents": ["three released albums", "the working A Protopian Gambit and Straddie Fun records", "B-sides", "bonus videos", "drafts", "AI podcast selections", "selected works in progress"],
            },
        ],
    }
    write(REPO / "data" / "download-packaging.json", json.dumps(packages, indent=2))


def write_readme(albums: list[Album], songs: list[Song]) -> None:
    ready = sum(1 for song in songs if song.ready())
    content = f"""# i C. infinity Music Universe

Static GitHub Pages site for the i C. infinity artist catalogue.

## What it contains

- {len(albums)} album/archive pages
- {len(songs)} generated song pages
- {ready} songs with lyrics imported in this pass
- Grand Narrative, Luke Catalyst, Travel Oracle, and Adjacent Worlds context pages
- 14 preserved legacy photographs converted to WebP
- Infinity Engine notes for turning songs into comics, lyric videos, and vertical micro-dramas
- Dark-mode Infinity Engine Studio builders for human listening passes, `.md` ingestion profiles, video briefs, storyboards, shots, distribution-fit plans, reviews, and handoffs
- Draft paid-download packaging notes in `data/download-packaging.json`

## Rebuild

Run:

```powershell
python tools/build_site.py
```

The generator reads the Protopian Gambit lyric source from Luke's local source folder and keeps local workshop file paths out of the public site data.

## Notes

The old one-page prototype is preserved as `legacy-content-engine.html`.
"""
    write(REPO / "README.md", content)


def main() -> None:
    albums, songs = build_catalogue()
    album_by_slug = {album.slug: album for album in albums}

    safe_clean(REPO / "albums")
    safe_clean(REPO / "songs")

    write(REPO / "index.html", home_page(albums, songs))
    write(REPO / "albums.html", albums_index(albums))
    write(REPO / "songs.html", songs_index(songs))
    write(REPO / "downloads.html", downloads_page(albums, songs))
    write(REPO / "infinity-engine.html", engine_page())
    write(REPO / "grand-narrative.html", grand_narrative_page())
    write(REPO / "luke-catalyst.html", luke_catalyst_page())
    write(REPO / "photo-archive.html", photo_archive_page())
    write(REPO / "travel-oracle.html", travel_oracle_page())
    write(REPO / "worlds.html", worlds_page())
    write(REPO / "about.html", about_page())
    write(REPO / "sources.html", sources_page())
    write(REPO / "site-map.html", site_map_page(albums, songs))
    write(REPO / "sitemap.xml", xml_sitemap(albums, songs))
    write(REPO / "builders" / "index.html", builder_index_page())
    for builder in STUDIO_BUILDERS:
        if builder.get("key") == "humanIngestion":
            write(REPO / "builders" / builder["href"], human_ingestion_page(songs))
        else:
            write(REPO / "builders" / builder["href"], builder_page(builder["key"], songs))
    write(REPO / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_ROOT}sitemap.xml\n")

    for album in albums:
        write(REPO / "albums" / album.slug / "index.html", album_page(album))

    for song in songs:
        album = album_by_slug[song.album_slug]
        write(REPO / "songs" / song.slug / "index.html", song_page(song, album))

    export_data(albums, songs)
    export_download_packaging()
    write_readme(albums, songs)

    print(f"Generated {len(albums)} album pages and {len(songs)} song pages.")


if __name__ == "__main__":
    main()
