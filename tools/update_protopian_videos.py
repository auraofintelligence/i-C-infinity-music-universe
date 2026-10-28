"""Refresh the corrected 22-track album without private source files."""
from dataclasses import fields
import json
import re

import build_site as site


def main() -> None:
    path = site.REPO / "data" / "catalogue.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    song_fields = {field.name for field in fields(site.Song)}
    songs = [site.Song(**{key: value for key, value in row.items() if key in song_fields},
                       album_title=row["album"]) for row in data["songs"]]
    by_slug = {song.slug: song for song in songs}
    album_fields = {field.name for field in fields(site.Album)} - {"tracks"}
    albums = [site.Album(**{key: value for key, value in row.items() if key in album_fields},
                         tracks=[by_slug[slug] for slug in row["tracks"]]) for row in data["albums"]]
    album = next(album for album in albums if album.slug == "a-protopian-gambit")
    album.tracks = site.protopian_tracks(album, by_slug)
    album.status = "22 landscape videos and corrected lyrics"
    album.source_url = site.album_playlist_url(album.slug)
    first = next(i for i, song in enumerate(songs) if song.album_slug == album.slug)
    songs = [song for song in songs if song.album_slug != album.slug]
    songs[first:first] = album.tracks
    site.apply_protopian_videos(songs)
    site.write(site.REPO / "albums" / album.slug / "index.html", site.album_page(album))
    for song in album.tracks:
        site.write(site.REPO / "songs" / song.slug / "index.html", site.song_page(song, album))
    site.write(site.REPO / "songs.html", site.songs_index(songs))
    site.write(site.REPO / "index.html", site.home_page(albums, songs))
    site.write(site.REPO / "albums.html", site.albums_index(albums))
    site.write(site.REPO / "site-map.html", site.site_map_page(albums, songs))
    site.write(site.REPO / "sitemap.xml", site.xml_sitemap(albums, songs))
    site.write(site.REPO / "builders" / "human-ingestion.html", site.human_ingestion_page(songs))
    for builder in site.STUDIO_BUILDERS:
        if builder.get("key") != "humanIngestion":
            site.write(site.REPO / "builders" / builder["href"], site.builder_page(builder["key"], songs))
    site.write_protopian_legacy_links()
    site.export_data(albums, songs)
    # Keep the maintained project links and documentation when updating counts.
    readme_path = site.REPO / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme = re.sub(r"- \d+ generated song pages", f"- {len(songs)} generated song pages", readme)
    readme = re.sub(r"- \d+ songs with lyrics imported in this pass", f"- {sum(song.ready() for song in songs)} songs with lyrics imported in this pass", readme)
    site.write(readme_path, readme)
    print(f"Updated {len(album.tracks)} tracks, landscape videos and corrected lyrics.")


if __name__ == "__main__":
    main()
