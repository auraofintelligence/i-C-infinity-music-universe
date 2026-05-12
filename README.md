# i C. infinity Music Universe

Static GitHub Pages site for the i C. infinity artist catalogue.

## What it contains

- 8 album/archive pages
- 103 generated song pages
- 89 songs with lyrics imported in this pass
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
