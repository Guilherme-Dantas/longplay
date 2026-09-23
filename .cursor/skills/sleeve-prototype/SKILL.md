---
name: sleeve-prototype
description: >-
  Iterate the longplay phone screen in design/sleeve.html (disc gauge, search
  phrases, album carousel) before any Expo port. Use when the user asks to
  change the phone UI, the sleeve, the disc, the gauge, the carousel, Press
  play, or the visual prototype.
---

# Sleeve prototype

`design/sleeve.html` is the phone screen. `apps/mobile` is not the design until someone asks to port it.

## Change it

1. Edit `design/sleeve.html` only.
2. If nothing is serving it, start one from `design/`:

```powershell
F:\homelab\longplay\.venv\Scripts\python.exe -m http.server 8090
```

3. Open `http://127.0.0.1:8090/sleeve.html?v=<new-token>` so the browser does not keep an old file.
4. Exercise the path you changed in the browser before finishing: type, drag, submit, and return. A still screenshot is not enough.

## Look

Dark page, Geist, rounded glass card, a little liquid glass (blur, faint border, inset highlight). Session length is a disc: the slider is a gauge around the minute number, and the thumb travels the ring.

Leave the cream disc, Bodoni, and copper sleeve behind.

## Behavior

Keep this unless the user changes it:

- Minutes run from 5 to 240. Click the number to type. Drag with `clientX` / `clientY` and the disc bounding rect. Do not use `locationX` (it is missing on web and yields NaN).
- The text field expands on focus or when it has text, and wraps lines.
- Press play does not call the network. Empty text focuses the field.
- While searching, the number hides. A short arc sweeps the ring and these lines take the hub, one at a time: "Looking across the shelf", "Measuring the runtime", "Keeping the clock", "One that follows the ask".
- The disc then becomes the album carousel in the same place. One recommendation, plus up to four other fits. Drag, click a visible edge, or use the dots. Covers are flat color. No real album art.
- On the shortlist the text field is gone. "Look for something else" restores the disc and the field, including the text already written.
- The white button says "Press play" on the disc and the centered album name on the shortlist.
- UI copy stays English.

Shortlist copy stays a recommendation versus other fits: people, year, duration, and a why line on the recommendation. The clock still wins. Do not add activity trees, Spotify login, or `POST /runs` to this file.
