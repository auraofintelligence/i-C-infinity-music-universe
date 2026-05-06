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
LYRIC_SOURCE = Path(r"C:\Users\lukec\Downloads\4th i C. infinity album A Protopian Gambit (lyrics).md")


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
STRANGE_DOWNLOADS = "https://auraofintelligence.github.io/strange-but-true/downloads.html"
STREAMING_LINKS = REPO / "data" / "streaming-links.json"
ORDER_PAGE = "https://auraofintelligence.github.io/i-C-infinity-music-universe/order.html"
STARSEED_ALBUM_SLUG = "starseed-code-from-aura-to-infinity"
STARSEED_YOUTUBE_PLAYLIST_ID = "PLsN0U9hPJHBZyRTYmAwLCuVSpY9q_-tCd"
STARSEED_YOUTUBE_PLAYLIST_URL = f"https://www.youtube.com/playlist?list={STARSEED_YOUTUBE_PLAYLIST_ID}"


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
        "artwork": "assets/img/cover-straddie.jpg",
        "source_url": "https://music.apple.com/us/album/songs-of-straddie/1783109888",
        "summary": "The island doorway: Minjerribah, summer, tides, romance, community, and the first public invitation to meet the project where it lives.",
        "deeper_system": "This album grounds the cosmic language in place. It turns the abstract Infinity world back toward local belonging, care, love, beaches, family energy, and the everyday social fabric of Straddie.",
        "visual_world": "Coastal light, ferry windows, campfire circles, dune paths, shoreline dances, handwritten signs, local faces, and gentle magical realism rather than heavy science fiction.",
        "tracks": [
            "Songs of Straddie",
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
        ],
    },
    {
        "title": "Chronicles of the Forgotten",
        "slug": "chronicles-of-the-forgotten",
        "year": "2025",
        "status": "Released album",
        "artwork": "assets/img/cover-chronicles.jpg",
        "source_url": "https://music.apple.com/us/album/chronicles-of-the-forgotten/1791557503",
        "summary": "A larger mythic and social arc: ignored voices, broken systems, ancestral echoes, technology, hope, deception, and repair.",
        "deeper_system": "This is the bridge from personal song into world-system thinking. The forgotten are not just characters; they are memory, labour, ecosystems, ancestors, and futures that old ledgers failed to count.",
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
        ],
    },
    {
        "title": "Starseed Code: From Aura to Infinity",
        "slug": "starseed-code-from-aura-to-infinity",
        "year": "2025",
        "status": "Released album",
        "artwork": "assets/img/cover-starseed.jpg",
        "source_url": "https://music.apple.com/us/album/starseed-code-from-aura-to-infinity/1821950221",
        "summary": "The metaphysical tech chapter: Aura, G.A.J.R.A., infinity, democratic redesign, love, memory, myth, and the self as a living interface.",
        "deeper_system": "This album moves from island and archive into cognitive architecture. It treats identity, AI, soul, governance, love, and longevity as linked design problems.",
        "visual_world": "Human figures surrounded by luminous interfaces, cosmic gardens, body-mind data doubles, ritual circles, civic halls, and warm science-fiction symbolism.",
        "tracks": [
            "Starseed Code: From Aura to Infinity",
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
            "Poetic Thruths of Infinity",
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
        "status": "Lyrics imported",
        "artwork": "assets/img/cover-building-protopia.jpg",
        "source_url": "",
        "summary": "The fourth-album build: crisis as mirror, protopia as practice, care ledgers, consent, repair, forms, civic courage, and grounded abundance.",
        "deeper_system": "This is where the songs start acting like design briefs. They point directly at systems for care work, public coordination, human-AI collaboration, civic process, and creative restraint inside crisis.",
        "visual_world": "Solar storms, public ledgers, repair gold, civic counters, purple mats, community halls, builders at dawn, and comic panels that become video keyframes.",
        "tracks": [],
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
        "status": "Track list to import",
        "artwork": "assets/img/hero-luke-universal-creator.jpg",
        "summary": "The early sketches, experiments, first frameworks, and raw attempts before the albums took a clearer shape.",
        "deeper_system": "This page is the intake tray for the earliest material. It should eventually show what ideas survived, what mutated, and which concepts became part of the later Infinity system.",
        "visual_world": "Desktop screenshots, old notebooks, early videos, first AI experiments, and archive-room energy.",
    },
    {
        "title": "Next Signals",
        "slug": "next-signals",
        "year": "In progress",
        "status": "New songs to add",
        "artwork": "assets/img/hero-brisbane-tiny-planet.png",
        "summary": "A holding page for the next cycle of songs after A Protopian Gambit.",
        "deeper_system": "This is the forward-looking lab. It can capture new songs as soon as they appear, before the album title or narrative order is locked.",
        "visual_world": "Sketches, test renders, field recordings, lyric fragments, seed prompts, and prototype clips.",
    },
    {
        "title": "Local B-Sides and Fun Songs",
        "slug": "local-b-sides-and-fun-songs",
        "year": "Ongoing",
        "status": "Loose song tray",
        "artwork": "assets/img/hero-brisbane-tiny-planet.png",
        "summary": "The joyful local songs that do not need a heavy throughline to be worth keeping.",
        "deeper_system": "This page protects the fun layer. Not every song has to carry the whole cosmology. Some songs simply keep the world human, local, and alive.",
        "visual_world": "Community noticeboards, road-trip clips, kitchen-table jokes, beaches, local characters, and lightweight lyric videos.",
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
    matches = list(re.finditer(r"^###\s+(.+?)\s+\{#.+?\}\s*$", raw, flags=re.M))
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
        songs[slugify(title)] = {"title": title, "date": date, "lyrics": clean_text(lyrics)}
    return songs


def infer_themes(title: str, album_slug: str) -> list[str]:
    lower = title.lower()
    themes: list[str] = []
    if "straddie" in album_slug or any(word in lower for word in ["island", "ocean", "shore", "tide", "beach", "minjerribah"]):
        themes += ["Minjerribah", "place", "community"]
    if any(word in lower for word in ["aura", "g.a.j.r.a", "agi", "algorithm", "circuit", "digital", "code"]):
        themes += ["AI", "Aura", "systems"]
    if any(word in lower for word in ["love", "heart", "soul", "obsessed", "kiss"]):
        themes += ["love", "embodiment"]
    if any(word in lower for word in ["forgotten", "ancient", "gaia", "earth", "chains", "deception", "unheard"]):
        themes += ["memory", "repair", "justice"]
    if any(word in lower for word in ["infinity", "starseed", "galactic", "stars", "celestial", "sol", "moon"]):
        themes += ["cosmic", "mythic scale"]
    if any(word in lower for word in ["protopia", "bridge", "border", "consent", "architect", "protocol", "light"]):
        themes += ["protopia", "care", "civic design"]
    if not themes:
        themes = ["song seed", "visual brief", "catalogue"]
    return list(dict.fromkeys(themes))[:5]


def infer_meaning(title: str, album: Album) -> str:
    lower = title.lower()
    if "straddie" in album.slug or "island" in lower:
        return f"{title} sits in the island layer of the project: place, belonging, summer energy, and the way a local home can hold a much larger cosmology without becoming abstract."
    if album.slug == "chronicles-of-the-forgotten":
        return f"{title} belongs to the recovery layer: unheard voices, buried systems, old wounds, and the choice to turn memory into action rather than spectacle."
    if album.slug == "starseed-code-from-aura-to-infinity":
        return f"{title} is part of the Aura-to-Infinity layer, where identity, AI, love, civic redesign, and cosmic imagination are treated as connected pieces of one living architecture."
    if album.slug == "a-protopian-gambit":
        return f"{title} is one of the Protopian Gambit briefs: a song about making practical choices inside crisis, keeping joy, responsibility, and abundance in the same frame."
    if album.slug == "singles-and-public-markers":
        return f"{title} is a public marker song. It points listeners toward one of the larger threads before they enter the full album maps."
    return f"{title} is waiting for a deeper annotation pass. This page is ready for lyrics, meaning notes, and Infinity Engine video seeds."


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
            song.apple_url = links.get("apple", "")
            song.spotify_url = links.get("spotify", "")


def spotify_search_url(song: Song) -> str:
    return "https://open.spotify.com/search/" + quote(f"I C. Infinity {song.title}")


def youtube_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={quote(video_id)}&list={STARSEED_YOUTUBE_PLAYLIST_ID}"


def youtube_video_embed_src(video_id: str) -> str:
    return f"https://www.youtube.com/embed/{quote(video_id)}?list={STARSEED_YOUTUBE_PLAYLIST_ID}&rel=0"


def youtube_thumbnail_url(video_id: str) -> str:
    return f"https://img.youtube.com/vi/{quote(video_id)}/maxresdefault.jpg"


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

    if song.youtube_video_id:
        targets.append(("YouTube video", youtube_video_url(song.youtube_video_id), "youtube"))
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
    if not song.youtube_video_id:
        return ""
    src = youtube_video_embed_src(song.youtube_video_id)
    url = youtube_video_url(song.youtube_video_id)
    title = song.youtube_title or f"{song.title} vertical video"
    return f"""
    <section class="song-video-panel" id="vertical-video">
      <div class="vertical-video-frame">
        <iframe title="{esc(title)}" src="{esc(src)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" loading="lazy" allowfullscreen></iframe>
      </div>
      <div class="vertical-video-copy">
        <p class="eyebrow">Vertical Video</p>
        <h2>{esc(song.title)}</h2>
        <p>Mobile-first YouTube video for this Starseed Code song. This becomes the published visual reference before any later Infinity Engine remix or paid-download packaging.</p>
        <div class="listen-links compact">
          <a class="listen-chip youtube" href="{esc(url)}" target="_blank" rel="noopener">Open on YouTube</a>
          <a class="listen-chip" href="{esc(STARSEED_YOUTUBE_PLAYLIST_URL)}" target="_blank" rel="noopener">Full playlist</a>
        </div>
      </div>
    </section>
    """


def order_href(package_id: str, absolute: bool = False) -> str:
    base = ORDER_PAGE if absolute else "order.html"
    return f"{base}?package={quote(package_id)}"


def build_catalogue() -> tuple[list[Album], list[Song]]:
    protopian = parse_protopian_lyrics()
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
                album.tracks.append(track)

        for track in album.tracks:
            special = SPECIAL_BRIEFS.get(slugify(track.title))
            track.themes = special["themes"] if special else infer_themes(track.title, album.slug)
            track.meaning = special["meaning"] if special else infer_meaning(track.title, album)
            track.video_seeds = special["seeds"] if special else generic_seeds(track, album)
            track.slug = f"{album.slug}-{track.track_number:02d}-{slugify(track.title)}"
            if album.slug == STARSEED_ALBUM_SLUG and track.title in STARSEED_VERTICAL_VIDEOS:
                video = STARSEED_VERTICAL_VIDEOS[track.title]
                track.youtube_video_id = video["id"]
                track.youtube_title = video["title"]
            songs.append(track)
        albums.append(album)

    singles_album = Album(
        title="Singles and Public Markers",
        slug="singles-and-public-markers",
        year="2024-2025",
        status="Released singles",
        artwork="assets/img/cover-building-protopia.jpg",
        source_url=APPLE_ARTIST,
        summary="Standalone public releases that point into the larger album worlds.",
        deeper_system="These singles are public signposts. Some later become album tracks, some are bridges, and some are proof-of-life markers for a bigger system still being mapped.",
        visual_world="Cover art, lyric-video fragments, platform embeds, and short public-facing story seeds.",
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
        track.slug = f"{singles_album.slug}-{track.track_number:02d}-{slugify(track.title)}"
        singles_album.tracks.append(track)
        songs.append(track)
    albums.append(singles_album)

    for spec in PLACEHOLDER_ALBUMS:
        albums.append(
            Album(
                title=spec["title"],
                slug=spec["slug"],
                year=spec["year"],
                status=spec["status"],
                artwork=spec["artwork"],
                summary=spec["summary"],
                deeper_system=spec["deeper_system"],
                visual_world=spec["visual_world"],
            )
        )

    apply_streaming_links(albums)
    return albums, songs


def nav(prefix: str) -> str:
    return f"""
    <header class="site-header">
      <a class="brand" href="{prefix}index.html" aria-label="i C. infinity home">
        <strong>i C. infinity</strong>
        <span>songs as systems</span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="site-nav" id="site-nav" aria-label="Primary navigation">
        <a href="{prefix}albums.html">Albums</a>
        <a href="{prefix}songs.html">Songs</a>
        <a href="{prefix}downloads.html">Packaging Lab</a>
        <a href="{prefix}order.html">Order</a>
        <a href="{prefix}infinity-engine.html">Infinity Engine</a>
        <a href="{prefix}about.html">About</a>
        <a href="{prefix}sources.html">Sources</a>
      </nav>
    </header>
    """


def layout(title: str, description: str, body: str, prefix: str = "", page_class: str = "") -> str:
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
  <link rel="stylesheet" href="{prefix}assets/css/styles.css">
</head>
<body>
  {nav(prefix)}
  <main class="page {page_class}">
{body}
  </main>
  <footer class="footer">
    <div class="footer-inner">
      <div>
        <strong>i C. infinity</strong><br>
        <span>Music, lyrics, systems, and video seeds.</span>
      </div>
      <div>
        <a href="{prefix}sources.html">Sources and notes</a>
      </div>
    </div>
  </footer>
  <script src="{prefix}assets/js/site.js"></script>
  <script src="{prefix}assets/js/order-config.js"></script>
  <script src="{prefix}assets/js/order.js"></script>
</body>
</html>
"""


def album_card(album: Album, prefix: str = "") -> str:
    href = f"{prefix}albums/{album.slug}/"
    source = f'<a href="{esc(album.source_url)}">Public listing</a>' if album.source_url else "Local archive"
    return f"""
    <article class="album-card">
      <a href="{href}">
        <div class="album-art"><img src="{prefix}{esc(album.artwork)}" alt="{esc(album.title)} artwork"></div>
        <div class="album-body">
          <h3>{esc(album.title)}</h3>
          <p>{esc(album.summary)}</p>
          <div class="meta-line"><span>{esc(album.year)}</span><span>{esc(album.status)}</span><span>{len(album.tracks)} songs mapped</span></div>
        </div>
      </a>
      <div class="album-body quiet">{source}</div>
    </article>
    """


def song_status(song: Song) -> str:
    if song.ready():
        return '<span class="status-pill ready">Lyrics ready</span>'
    return '<span class="status-pill todo">Lyrics to import</span>'


def song_card(song: Song, prefix: str = "") -> str:
    search_terms = [song.title, song.album_title, " ".join(song.themes), "spotify apple itunes"]
    if song.youtube_video_id:
        search_terms.append("youtube vertical video mobile")
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
    """


def track_row(song: Song, prefix: str = "") -> str:
    href = f"{prefix}songs/{song.slug}/"
    lyric_note = "Full lyrics imported" if song.ready() else "Lyric slot ready"
    return f"""
    <div class="track-row">
      <a href="{href}">
        <span class="track-number">{song.track_number:02d}</span>
        <span class="track-title"><strong>{esc(song.title)}</strong><span>{esc(lyric_note)}</span></span>
        {song_status(song)}
      </a>
    </div>
    """


def home_page(albums: list[Album], songs: list[Song]) -> str:
    ready_count = sum(1 for song in songs if song.ready())
    body = f"""
    <section class="hero home-intro">
      <img class="home-hero-image" src="assets/img/hero-luke-universal-creator.jpg" alt="Luke Universal Creator image">
      <div class="hero-content">
        <h1>i C. infinity</h1>
        <p>A living music catalogue for the songs, albums, lyrics, deeper meanings, and Infinity Engine video seeds behind the I See Infinity universe.</p>
        <div class="hero-actions">
          <a class="button" href="albums.html">Explore albums</a>
          <a class="button secondary" href="songs.html">Open song map</a>
          <a class="button secondary" href="downloads.html">Packaging lab</a>
        </div>
        <div class="metrics" aria-label="Catalogue status">
          <div class="metric"><strong>{len(albums)}</strong><span>album and archive pages</span></div>
          <div class="metric"><strong>{len(songs)}</strong><span>song pages generated</span></div>
          <div class="metric"><strong>{ready_count}</strong><span>songs with imported lyrics</span></div>
        </div>
      </div>
    </section>
    <section class="image-sequence" aria-label="Album world images">
      <article class="image-panel">
        <img src="assets/img/cover-starseed.jpg" alt="Starseed Code artwork">
        <div class="image-panel-copy">
          <h2>From Aura to Infinity</h2>
          <p>The metaphysical technology layer: identity, love, intelligence, governance, and the self as a living interface.</p>
        </div>
      </article>
      <article class="image-panel">
        <img src="assets/img/cover-straddie.jpg" alt="Songs of Straddie artwork">
        <div class="image-panel-copy">
          <h2>Meet me on Straddie</h2>
          <p>The local doorway: Minjerribah, summer, shoreline, community, romance, and the place where the cosmic work touches sand.</p>
        </div>
      </article>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <h2>Album Worlds</h2>
          <p>Each album page keeps the track list, the bigger system layer, and the visual world for future lyric videos, comics, and vertical micro-dramas.</p>
        </div>
        <div class="album-grid">
          {''.join(album_card(album) for album in albums)}
        </div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>Packaging Lab</h2>
          <p>This site also helps work out the paid download products before the checkout layer is final: what files go in each bundle, what formats to offer, and what bonus material belongs where.</p>
        </div>
        <div class="feature-grid">
          <article class="feature-card"><h3>Package contents</h3><p>Decide which audio, videos, lyrics, covers, notes, and bonus files belong in each pack.</p></article>
          <article class="feature-card"><h3>Format choices</h3><p>Compare MP3, WAV, FLAC, MP4, lyric PDFs, and future physical or USB options.</p></article>
          <article class="feature-card"><h3>Shop reference</h3><p><a href="{STRANGE_DOWNLOADS}">Use the current Strange But True downloads page</a> as the checkout reference, not the final product structure.</p></article>
        </div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>Deep Seeds</h2>
          <p>The site is built to become an intake layer for the Infinity Engine: lyrics in, meaning maps out, comic panels first, video keyframes next.</p>
        </div>
        <div class="feature-grid">
          <article class="feature-card"><h3>Lyrics</h3><p>Full Protopian lyrics are imported now. Other albums have clean slots ready for the next content pass.</p></article>
          <article class="feature-card"><h3>Meaning</h3><p>Every song page starts with a plain-language meaning layer so listeners can see how the song fits the bigger system.</p></article>
          <article class="feature-card"><h3>Video Seeds</h3><p>Each song has three first-pass seed directions: lyric video, micro-drama, and comic-as-storyboard.</p></article>
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
          <p>The public albums, upcoming Protopian material, early archive tray, next signals, and local B-side layer.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/hero-brisbane-tiny-planet.png" alt="Tiny planet visual from I See Infinity"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap album-grid">
        {''.join(album_card(album) for album in albums)}
      </div>
    </section>
    """
    return layout("Albums - i C. infinity", "Album pages and archive trays for i C. infinity.", body)


def songs_index(songs: list[Song]) -> str:
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Songs</h1>
          <p>Search the generated song pages. Protopian lyrics are populated; released album lyrics are ready for the next import pass.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-starseed.jpg" alt="Starseed Code artwork"></div>
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
    bundle_cards = [
        ("One Album Pack", "Decision to make: final audio formats, cover art, lyrics PDF, video links, and whether each album gets a short guide to the deeper meaning."),
        ("Two Album Pack", "Decision to make: whether this is simply a discount bundle or a curated pathway, for example Straddie plus Starseed, or Chronicles plus Protopian material."),
        ("Three Released Albums Pack", "Decision to make: how to package Songs of Straddie, Chronicles of the Forgotten, and Starseed Code as one clean folder with track lists and context notes."),
        ("Full Music Archive Pack", "Decision to make: where to draw the line around B-sides, fourth-album drafts, bonus videos, podcasts, working notes, and selected works in progress."),
    ]
    bundle_html = "".join(
        f'<article class="feature-card"><h3>{esc(title)}</h3><p>{esc(text)}</p></article>'
        for title, text in bundle_cards
    )
    package_compare = [
        ("One Album Pack", "$20", "Choose only the album you most want.", order_href("one-album")),
        ("Two Album Pack", "$35", "Pick a pair of connected album worlds.", order_href("two-album")),
        ("Three Album Pack", "$45", "Keep the released-album set clean.", order_href("three-album")),
        ("Full Archive Pack", "$50", "Stay with the whole catalogue and bonus archive layer.", order_href("full-archive")),
    ]
    package_compare_html = "".join(
        f"""
        <article class="feature-card">
          <h3>{esc(title)}</h3>
          <p><strong>{esc(price)}</strong></p>
          <p>{esc(text)}</p>
          <p><a class="button secondary" href="{esc(href)}">Open option</a></p>
        </article>
        """
        for title, price, text, href in package_compare
    )
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Paid Download Packaging Lab</h1>
          <p>A draft workspace for working out what the I C. Infinity paid downloads should contain before the checkout layer is final.</p>
          <div class="action-row">
            <a class="button" href="#choose-package">Choose full archive pack</a>
            <a class="button secondary" href="albums.html">Review album worlds</a>
            <a class="button secondary" href="https://auraofintelligence.github.io/strange-but-true/downloads.html#music-album-bundles">Compare all packs</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-building-protopia.jpg" alt="Building Protopia artwork"></div>
      </div>
    </section>
    <section class="section package-sale" id="choose-package">
      <div class="wrap layout-two">
        <div class="panel">
          <h2>Choose The Full Archive Pack</h2>
          <p><strong>Full Music Archive Pack $50</strong></p>
          <p>The bigger catalogue option: released albums, most of A Protopian Gambit, B-sides, bonus videos, drafts, selected podcasts, and works in progress.</p>
          <div class="action-row">
            <a class="button" href="{order_href("full-archive")}">Start this $50 order</a>
            <a class="button secondary" href="https://auraofintelligence.github.io/strange-but-true/downloads.html#music-album-bundles">Compare all packs</a>
          </div>
        </div>
        <div class="panel">
          <h2>Changed Your Mind?</h2>
          <p>If the full archive feels too big, move down to a one, two, or three album pack before starting the order.</p>
          <div class="action-row">
            <a class="button secondary" href="https://auraofintelligence.github.io/i-C-infinity-one-album-pack/">One album</a>
            <a class="button secondary" href="https://auraofintelligence.github.io/i-C-infinity-three-album-pack/">Three albums</a>
          </div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <h2>Bundle Questions</h2>
          <p>These are not final buyer promises. They are the working decisions that need to be settled before the paid files are packaged.</p>
        </div>
        <div class="feature-grid">{bundle_html}</div>
      </div>
    </section>
    <section class="section tight" id="upgrade-options">
      <div class="wrap">
        <div class="section-head">
          <h2>Compare Before You Buy</h2>
          <p>You can still change your mind. Pick a smaller pack if that is cleaner, or stay with the whole archive if the bigger creative cache is what you want.</p>
        </div>
        <div class="feature-grid">{package_compare_html}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>Album Inputs</h2>
          <p>Each released album needs a clean package folder, public description, track list, cover art, and a decision about bonus material.</p>
        </div>
        <div class="album-grid">{album_links}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap layout-two">
        <div class="panel">
          <h2>Packaging Principle</h2>
          <p>A paid download should be a direct value exchange, not charity language and not a vague tip jar. The buyer gets useful files. Luke gets cash to keep building.</p>
          <p>Free streaming can stay as discovery. Paid downloads should feel like owning a clean, well-labelled slice of the project.</p>
        </div>
        <div class="panel">
          <h2>Packaging Checklist</h2>
          <p>1. Choose the bundle names and prices.</p>
          <p>2. Decide file formats: MP3, WAV, FLAC, MP4, lyrics PDF, cover art, and notes.</p>
          <p>3. Build one folder per bundle with simple names and no local machine paths.</p>
          <p>4. Write buyer-facing copy only after the actual contents are clear.</p>
        </div>
      </div>
    </section>
    """
    return layout("Paid Download Packaging Lab - i C. infinity", "Draft packaging workspace for I C. Infinity paid music downloads.", body)


def order_page() -> str:
    package_options = "\n".join(
        f'<option value="{esc(package["id"])}">{esc(package["name"])} - ${package["price"]} AUD</option>'
        for package in PACKAGE_OPTIONS
    )
    package_cards = "".join(
        f"""
        <article class="feature-card">
          <h3>{esc(package["name"])}</h3>
          <p><strong>${package["price"]} AUD</strong></p>
          <p>{esc(package["description"])}</p>
          <p><a class="button secondary" href="{order_href(package["id"])}">Choose this pack</a></p>
        </article>
        """
        for package in PACKAGE_OPTIONS
    )
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Order Music Downloads</h1>
          <p>Choose a music bundle, leave the delivery details, then pay by Stripe Checkout, PayPal, or PayID / bank transfer once the Apps Script endpoint is connected.</p>
          <div class="action-row">
            <a class="button" href="#order-form-title">Start order</a>
            <a class="button secondary" href="downloads.html#upgrade-options">Compare packs</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-building-protopia.jpg" alt="I C. Infinity package artwork"></div>
      </div>
    </section>
    <section class="section" id="order-form-title">
      <div class="wrap layout-two order-layout">
        <form class="panel order-form" data-order-form method="post">
          <input type="hidden" name="sourcePage" data-source-page>
          <input class="screen-reader-trap" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
          <h2>Start Order</h2>
          <p class="order-status" data-order-status>Choose a pack and payment method. Card payments use Stripe Checkout, not a card form on this site.</p>
          <label for="packageId">Music package</label>
          <select id="packageId" name="packageId" data-package-select required>
            {package_options}
          </select>
          <div class="order-summary" data-order-summary aria-live="polite"></div>
          <label for="albumChoices">Album choice or bundle note</label>
          <textarea id="albumChoices" name="albumChoices" rows="3" data-album-choices placeholder="Example: Songs of Straddie, or Straddie + Starseed"></textarea>
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
            <legend>Payment method</legend>
            <label><input type="radio" name="paymentMethod" value="stripe" checked> Stripe card / wallet</label>
            <label><input type="radio" name="paymentMethod" value="paypal"> PayPal</label>
            <label><input type="radio" name="paymentMethod" value="payid"> PayID / bank transfer</label>
          </fieldset>
          <label for="deliveryNotes">Notes</label>
          <textarea id="deliveryNotes" name="deliveryNotes" rows="3" placeholder="Anything useful for delivery or package choice"></textarea>
          <button class="button" type="submit" data-order-submit>Continue to payment</button>
          <p class="microcopy">Orders are logged to a private Google Sheet. Payment secrets live in Google Apps Script properties, not in this public repo.</p>
        </form>
        <aside class="panel">
          <h2>How The Payment Flow Works</h2>
          <p><strong>1. Sheet record</strong><br>The Apps Script writes the order to Google Sheets first, so there is a trace even if payment is manual.</p>
          <p><strong>2. Stripe Checkout</strong><br>For card or wallet payments, Apps Script creates the Stripe Checkout Session and redirects the buyer there.</p>
          <p><strong>3. Manual options</strong><br>PayPal and PayID / bank transfer can be recorded in the same sheet and confirmed manually before delivery.</p>
          <p><strong>4. Delivery</strong><br>Downloads can be delivered after payment confirmation by email, Drive link, or a later automated file link.</p>
        </aside>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="section-head">
          <h2>Package Options</h2>
          <p>You can still change your mind before payment. This keeps the buying path flexible while you work out the final bundle packaging.</p>
        </div>
        <div class="feature-grid">{package_cards}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="notice">
          Setup note: this page needs the deployed Google Apps Script web app URL added to <strong>assets/js/order-config.js</strong> before live orders can be accepted.
        </div>
      </div>
    </section>
    """
    return layout("Order Music Downloads - i C. infinity", "Order page for I C. Infinity music download bundles.", body)


def starseed_video_section(album: Album, prefix: str) -> str:
    if album.slug != STARSEED_ALBUM_SLUG:
        return ""
    video_tracks = [song for song in album.tracks if song.youtube_video_id]
    if not video_tracks:
        return ""
    featured_video = video_tracks[0]
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
            <img src="{esc(youtube_thumbnail_url(featured_video.youtube_video_id))}" alt="{esc(featured_video.title)} vertical video thumbnail">
            <span class="play-mark" aria-hidden="true"></span>
            <span class="sr-only">Open Starseed Code YouTube playlist</span>
          </a>
        </div>
        <div class="video-feature-copy">
          <p class="eyebrow">Mobile Video Layer</p>
          <h2>Starseed Code Vertical Playlist</h2>
          <p>{len(video_tracks)} Starseed Code songs are matched to portrait-format YouTube videos. This turns the album page into a phone-first watch path, not just a static track list.</p>
          <div class="action-row">
            <a class="button" href="{esc(STARSEED_YOUTUBE_PLAYLIST_URL)}" target="_blank" rel="noopener">Open playlist</a>
            <a class="button secondary" href="#track-map">Use track map</a>
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


def album_page(album: Album) -> str:
    prefix = "../../"
    tracks = "".join(track_row(song, prefix) for song in album.tracks)
    if not tracks:
        tracks = """
        <div class="notice">
          Track titles are not imported yet. This page is ready for a future pass that adds the exact songs, lyrics, and video seeds.
        </div>
        """
    source = f'<a href="{esc(album.source_url)}">Open public listing</a>' if album.source_url else "Local source material and upcoming release notes."
    video_section = starseed_video_section(album, prefix)
    track_section_id = ' id="track-map"' if video_section else ""
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>{esc(album.title)}</h1>
          <p>{esc(album.summary)}</p>
          <div class="meta-line"><span>{esc(album.year)}</span><span>{esc(album.status)}</span><span>{len(album.tracks)} songs mapped</span></div>
        </div>
        <div class="hero-cover"><img src="{prefix}{esc(album.artwork)}" alt="{esc(album.title)} artwork"></div>
      </div>
    </section>{video_section}
    <section class="section"{track_section_id}>
      <div class="wrap layout-two">
        <div>
          <h2>Track Map</h2>
          <div class="track-list">{tracks}</div>
        </div>
        <aside class="panel">
          <h2>Bigger Picture</h2>
          <p>{esc(album.deeper_system)}</p>
          <h3>Visual World</h3>
          <p>{esc(album.visual_world)}</p>
          <h3>Paid Download Packaging</h3>
          <p><a href="{prefix}downloads.html">Use the packaging lab</a> to decide what files and bonus material belong in this album pack.</p>
          <h3>Source</h3>
          <p>{source}</p>
        </aside>
      </div>
    </section>
    """
    return layout(f"{album.title} - i C. infinity", album.summary, body, prefix)


def song_page(song: Song, album: Album) -> str:
    prefix = "../../"
    lyrics = esc(song.lyrics) if song.lyrics else "Lyrics are not imported yet. Add the final lyric text here in the next content pass."
    seeds = "".join(f"""
      <article class="seed-card">
        <h3>{esc(seed['title'])}</h3>
        <p>{esc(seed['body'])}</p>
      </article>
    """ for seed in song.video_seeds)
    tags = "".join(f"<span>{esc(tag)}</span>" for tag in song.themes)
    release = listen_links_html(song) or "No public release link attached yet."
    spotify_embed = spotify_embed_html(song)
    youtube_embed = youtube_song_embed_html(song)
    media_embeds = spotify_embed + youtube_embed
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
            <h2>Meaning Layer</h2>
            <p>{esc(song.meaning)}</p>
          </div>
          {media_embeds}
          <h2>Lyrics</h2>
          <pre class="lyrics">{lyrics}</pre>
          <h2>Video Seed Ideas</h2>
          <div class="feature-grid">{seeds}</div>
        </article>
        <aside class="panel">
          <h2>Production Brief</h2>
          <p><strong>Lyric status:</strong><br>{esc(song.lyric_status)}</p>
          <p><strong>Release links:</strong></p>
          {release}
          <p><strong>Album system:</strong><br>{esc(album.deeper_system)}</p>
          <p><strong>Infinity Engine handoff:</strong><br>Use the lyrics and seeds to create a lyric analysis JSON, then draft comic panels before spending on video generation.</p>
        </aside>
      </div>
    </section>
    """
    return layout(f"{song.title} - i C. infinity", song.meaning, body, prefix)


def engine_page() -> str:
    steps = [
        ("1. Obsidian Nexus", "Structure each song as a note with title, album, themes, mood, lyrics, links, and status. This becomes the local truth source."),
        ("2. Lyrical Intelligence Swarm", "Extract core themes, emotional arc, symbols, narrative tension, and possible visual metaphors before generating expensive media."),
        ("3. Human Direction Point", "Luke chooses the preferred narrative direction while the system handles drafts, variants, and bookkeeping."),
        ("4. Comic-as-Storyboard", "Make still panels first. They are cheaper, easier to revise, and become a visual test before full video."),
        ("5. Keyframe-to-Video", "Use approved panels as start and end frames for short vertical video shots with controlled motion."),
        ("6. Review and Flywheel", "Approve, revise, or export. Audience response and creative notes feed back into the catalogue."),
    ]
    step_html = "".join(f'<article class="engine-step"><h3><strong>{esc(title)}</strong></h3><p>{esc(text)}</p></article>' for title, text in steps)
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Infinity Engine</h1>
          <p>The site is not just a brochure. It is the front door to a production pipeline where songs become lyric briefs, comics, vertical micro-dramas, and future album graphic novels.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-building-protopia.jpg" alt="Building Protopia artwork"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="engine-map">{step_html}</div>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap layout-two">
        <div class="panel">
          <h2>Cheapest sensible path</h2>
          <p>Do the thinking first: lyrics, themes, story beats, panels, then short clips. Keep lip-sync avoided where possible. Use local or low-cost tools for rough passes.</p>
        </div>
        <div class="panel">
          <h2>Best quality path</h2>
          <p>Use higher-end video generation and smarter assembly only after the comic/storyboard layer proves the idea. The expensive stage should receive already-approved visual direction.</p>
        </div>
      </div>
    </section>
    """
    return layout("Infinity Engine - i C. infinity", "The production engine behind i C. infinity song videos and comics.", body)


def about_page() -> str:
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>About</h1>
          <p>i C. infinity is Luke Catalyst Nathan Hayes' music artist and producer project: songs as emotional technology, local myth, AI-era philosophy, and practical world-building.</p>
          <div class="action-row">
            <a class="button" href="{MAIN_SITE}">iseeinfinity.com</a>
            <a class="button secondary" href="{SPOTIFY_ARTIST}">Spotify</a>
            <a class="button secondary" href="{APPLE_ARTIST}">Apple Music</a>
          </div>
        </div>
        <div class="hero-cover"><img src="assets/img/hero-luke-universal-creator.jpg" alt="Luke Universal Creator image"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap feature-grid">
        <article class="feature-card"><h3>Artist Layer</h3><p>Music, lyrics, releases, lyric videos, albums, and public song pages.</p></article>
        <article class="feature-card"><h3>System Layer</h3><p>Aura, G.A.J.R.A. Earth, joyful responsible abundance, cognitive architecture, and protopian design.</p></article>
        <article class="feature-card"><h3>Production Layer</h3><p>Infinity Engine seeds for comics, vertical micro-dramas, video keyframes, and future automated pipelines.</p></article>
      </div>
    </section>
    """
    return layout("About - i C. infinity", "About i C. infinity and I See Infinity.", body)


def sources_page() -> str:
    public_sources = [
        ("I See Infinity", MAIN_SITE, "Current public WordPress home and artist context."),
        ("Apple Music artist page", APPLE_ARTIST, "Public release list and album track lists used for the first catalogue scaffold."),
        ("Spotify artist page", SPOTIFY_ARTIST, "Public streaming destination."),
        ("Starseed Code YouTube playlist", STARSEED_YOUTUBE_PLAYLIST_URL, "Vertical mobile-video playlist supplied for the Starseed Code visual layer."),
        ("Amazon Music artist page", "https://music.amazon.com.br/artists/B0DP1BJD2S/i-c-infinity", "Secondary public release reference seen during discovery."),
    ]
    source_cards = "".join(f'<article class="source-card"><h3>{esc(name)}</h3><p>{esc(note)}</p><p><a href="{esc(url)}">{esc(url)}</a></p></article>' for name, url, note in public_sources)
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div>
          <h1>Sources</h1>
          <p>This page keeps the public source trail visible without exposing private local file paths or workshop-only notes.</p>
        </div>
        <div class="hero-cover"><img src="assets/img/cover-chronicles.jpg" alt="Chronicles artwork"></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="source-grid">{source_cards}</div>
        <div class="notice" style="margin-top: 24px;">Local supplied planning documents shaped the Infinity Engine summaries. They are treated as workshop source material, not published as raw documents here.</div>
      </div>
    </section>
    """
    return layout("Sources - i C. infinity", "Sources and notes for the i C. infinity music universe site.", body)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
            "starseed_youtube_playlist": STARSEED_YOUTUBE_PLAYLIST_URL,
            "paid_downloads": STRANGE_DOWNLOADS,
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
                "youtube_playlist_url": STARSEED_YOUTUBE_PLAYLIST_URL if album.slug == STARSEED_ALBUM_SLUG else "",
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
                "youtube_url": youtube_video_url(song.youtube_video_id) if song.youtube_video_id else "",
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
        "reference_checkout": STRANGE_DOWNLOADS,
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
                "candidate_contents": ["three released albums", "most of A Protopian Gambit", "B-sides", "bonus videos", "drafts", "AI podcast selections", "selected works in progress"],
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
- Infinity Engine notes for turning songs into comics, lyric videos, and vertical micro-dramas
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
    write(REPO / "order.html", order_page())
    write(REPO / "infinity-engine.html", engine_page())
    write(REPO / "about.html", about_page())
    write(REPO / "sources.html", sources_page())
    write(REPO / "robots.txt", "User-agent: *\nAllow: /\n")

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
