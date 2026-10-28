"""Refresh album pages using the committed catalogue and lyrics."""
from dataclasses import fields
import json

import build_site as site


def main() -> None:
    data = json.loads((site.REPO / "data" / "catalogue.json").read_text(encoding="utf-8"))
    song_fields = {field.name for field in fields(site.Song)}
    songs = {
        row["slug"]: site.Song(
            **{key: value for key, value in row.items() if key in song_fields},
            album_title=row["album"],
        )
        for row in data["songs"]
    }
    album_fields = {field.name for field in fields(site.Album)} - {"tracks"}
    for row in data["albums"]:
        album = site.Album(
            **{key: value for key, value in row.items() if key in album_fields},
            tracks=[songs[slug] for slug in row["tracks"]],
        )
        site.write(site.REPO / "albums" / album.slug / "index.html", site.album_page(album))
    print(f"Updated {len(data['albums'])} album pages; preserved the catalogue and lyrics.")


if __name__ == "__main__":
    main()
