"""Refresh the video pages using committed lyrics, without private source files."""
from dataclasses import fields
import json

import build_site as site


def main() -> None:
    path = site.REPO / "data" / "catalogue.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    song_fields = {field.name for field in fields(site.Song)}
    songs = [site.Song(**{key: value for key, value in row.items() if key in song_fields},
                       album_title=row["album"]) for row in data["songs"]]
    site.apply_protopian_videos(songs)
    by_slug = {song.slug: song for song in songs}
    album_fields = {field.name for field in fields(site.Album)} - {"tracks"}
    albums = [site.Album(**{key: value for key, value in row.items() if key in album_fields},
                         tracks=[by_slug[slug] for slug in row["tracks"]]) for row in data["albums"]]
    album = next(album for album in albums if album.slug == "a-protopian-gambit")
    site.write(site.REPO / "albums" / album.slug / "index.html", site.album_page(album))
    for song in album.tracks:
        site.write(site.REPO / "songs" / song.slug / "index.html", site.song_page(song, album))
    site.write(site.REPO / "songs.html", site.songs_index(songs))
    site.write(site.REPO / "builders" / "human-ingestion.html", site.human_ingestion_page(songs))
    # Preserve all other catalogue fields exactly as supplied by the lyric build.
    for row in data["songs"]:
        song = by_slug[row["slug"]]
        if song.album_slug == album.slug:
            for key in ("youtube_video_id", "youtube_title", "youtube_videos"):
                row[key] = getattr(song, key)
            row["youtube_url"] = site.youtube_video_link(site.primary_youtube_video(song)) if song.youtube_videos else ""
    site.write(path, json.dumps(data, indent=2))
    print(f"Updated {len(album.tracks)} track entries; preserved every lyric version.")


if __name__ == "__main__":
    main()
