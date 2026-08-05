# Hero banner generator

Generates `assets/hero-dark.svg` and `assets/hero-light.svg` — the animated
profile banner at the top of the README. Pure SVG + SMIL, no JavaScript, so it
animates inside a GitHub README.

## Regenerating

```bash
python tools/hero/gen_hero.py
```

Both themes come from one source, so the layout can never drift between them —
only the palette differs.

## Changing the portrait

`portrait.py` holds the ASCII grid and is generated from a photo:

```bash
python tools/hero/photo_to_ascii.py
```

Point `SRC` at the image first. A transparent-background PNG works best — the
alpha channel is what crops the subject and masks the background.

Glyph density follows brightness, so the lit face carries the detail. Tones
below `FLOOR` collapse to a single faint glyph instead of being dithered down
the ramp; a dithered shadow reads as scattered noise, a quantised one reads as
a solid mass and carries the silhouette.

## Editing content

Name, roles, info rows and the stack pills are constants near the top of
`gen_hero.py`. The pills wrap themselves, so items can be added or removed
without touching the layout.

## Notes

- Hover effects on the pills only fire when the SVG is opened directly. GitHub
  renders READMEs images through `<img>`, which is not interactive — the pills
  carry an autonomous glow pulse so they still look alive there.
- GitHub caches images through its camo proxy. After pushing a change the old
  banner can persist for a while.
