# i C. infinity Music Universe

<!-- github-organisation:start -->

## Project links and history

- First substantive build: 21 September 2025.
- GitHub repository: [i-C-infinity-music-universe](https://github.com/auraofintelligence/i-C-infinity-music-universe).
- Public site: [visit the public site](https://auraofintelligence.github.io/i-C-infinity-music-universe/).

## Related public projects

Each link below reflects an evidenced family, lineage or direct connection. This project has 6 relevant public connections.

### Aura Systems Image Atlas source projects

- [aura-systems-image-atlas](https://github.com/auraofintelligence/aura-systems-image-atlas) - [public page](https://auraofintelligence.github.io/aura-systems-image-atlas/) - source project represented in this visual atlas.
- [explorer-music-video-lab](https://github.com/auraofintelligence/explorer-music-video-lab) - [public page](https://auraofintelligence.github.io/explorer-music-video-lab/) - earlier build; explorer-music-video-lab is later, explicit cross-reference, ordered build lineage, shared named build family.

### Direct and other supported connections

- [global-group-marriages](https://github.com/auraofintelligence/global-group-marriages) - [public page](https://auraofintelligence.github.io/global-group-marriages/) - explicit cross-reference.

### i C. infinity music and content system

- [i-C-infinity](https://github.com/auraofintelligence/i-C-infinity) - later build; i-C-infinity is earlier, explicit cross-reference, ordered build lineage, shared named build family.
- [infinity-content-engine](https://github.com/auraofintelligence/infinity-content-engine) - [public page](https://auraofintelligence.github.io/infinity-content-engine/) - earlier build; infinity-content-engine is later, explicit cross-reference, ordered build lineage, shared named build family.
- [infinity-engine](https://github.com/auraofintelligence/infinity-engine) - [public page](https://auraofintelligence.github.io/infinity-engine/) - earlier build; infinity-engine is later, explicit cross-reference, ordered build lineage, shared named build family.

<!-- github-organisation:end -->

Static GitHub Pages site for the i C. infinity artist catalogue.

**Public catalogue:** <https://auraofintelligence.github.io/i-C-infinity-music-universe/>

## What it contains

- 8 album/archive pages
- 127 generated song pages
- 118 songs with lyrics imported in this pass
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

The Protopian Gambit album uses the 22-video YouTube playlist order in
`data/protopian-videos.json` and the corrected 28 October 2026 lyric sheet
transcribed into `data/protopian-lyrics.json`. The deferred "Strange but True"
song stays with the fifth album, Straddie Fun.

To update Protopian Gambit, edit those two data files and run
`python tools/update_protopian_videos.py` with Python 3.10 or later. This
refreshes the album, corrected lyrics, landscape players, navigation, catalogue
and listening cockpit without requiring private source files. Published song
URLs are stable; duplicate draft URLs redirect to the current song pages.

To refresh all album pages from the committed catalogue without private lyric
files, run `python tools/update_album_pages.py`. Albums with YouTube videos
have one player above one song list. Watch video buttons load the chosen video
in that player; Lyrics buttons open the song pages. Existing bonus videos stay
in the same list.

## Notes

The old one-page prototype is preserved as `legacy-content-engine.html`.

The generated public data does not include Luke's local workshop paths. Other
albums still use the private lyric sources named in `tools/build_site.py` for
a full rebuild; the committed site remains browsable without those folders.

## Related public pages

- [i C. infinity](https://iseeinfinity.com/) - the official artist home.
- [Explorers Music Video Lab](https://auraofintelligence.github.io/explorer-music-video-lab/) - a generalised creator-controlled clip workflow.
- [Infinity Content Engine](https://auraofintelligence.github.io/infinity-content-engine/) - the earlier interactive pipeline concept.

## Licence

See the [Strange But True Public Source Licence](LICENSE).
