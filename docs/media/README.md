# ALPORA — presentation and provenance

The README gallery was refreshed on **22 October 2026**, after Papirus/Bibata
integration. All product screenshots are captures of the running desktop at
1920×1080, scale 1. The banner is authored SVG branding, not a software screenshot.

## Current README assets

| Asset | Actual content |
| --- | --- |
| `showcase-alpine.png` | Floating Nautilus and Foot windows, the live ALPORA Fetch system card, themed folders, widgets, dock and robot |
| `showcase-moon.png` | Moon Lake desktop with the live system card |
| `palette-alpine.png` | Alpine Dawn with the desktop widgets and dock |
| `palette-moon-lake.png` | Moon Lake, same layout |
| `palette-forest-mist.png` | Forest Mist, same layout |
| `palette-warm-desert.png` | Warm Desert, same layout |
| `palette-northern-lights.png` | Northern Lights, same layout |
| `palette-rose-sunset.png` | Rose Sunset, same layout |
| `theme-orbit.png` | Actual circular desktop theme chooser |
| `settings-appearance.png` | Appearance controls, including the application's own illustrative preview |
| `theme-switching.mp4` | Native screen recording: selecting Moon Lake, then Northern Lights from Alpine Dawn, with the open system card following the palette |
| `theme-switching.gif` | Same recording encoded at 960×540 / 12 fps for inline GitHub display |

The source recording is 1920×1080 at 30 fps, without audio. It was captured with
wf-recorder, then encoded for the README with FFmpeg. No synthetic transition,
speed-up or inserted UI was added. PNG captures were made with Grim and remain
unretouched. The normal screen capture omits the hardware cursor, while the video
shows the native cursor interaction.

Foot runs the actual `bin/alpora-fetch` command in live mode. Its logo, borders,
text and swatches follow the desktop theme during the video. Kernel, memory and
uptime are read from the running machine; there are no invented system values.
No installation actions run during capture. Nautilus displays a temporary demonstration directory with
three example folders. Personal windows remain on other workspaces. No notes,
clipboard contents, fake music or device values are seeded for the screenshots.
Weather shows the configured city and actual service data; the music widget is
in its real empty state. The theme, flight preference, workspace and cursor
position were restored after capture. Only created demonstration windows were
positioned and closed.

Older captures remain here for history and are not the main README gallery.
`showcase-moon.png` was also refreshed with the live system card and is linked
from the ALPORA Fetch feature row; Alpine remains the main image. Historical `assets/reference/*approved*` and `*proposal*`
images are design references and are not presented as current software.

## Presentation references reviewed

- [HyDE](https://github.com/HyDE-Project/HyDE): branded entry point and direct navigation to installation/themes.
- [Caelestia](https://github.com/caelestia-dots/shell): demonstrating a working desktop before long configuration details.
- [Cozy Nord on r/unixporn](https://www.reddit.com/r/unixporn/comments/1k31yj8/), with its [linked dotfiles and screenshots](https://github.com/Rosh404/hyprland): a coordinated working desktop with real application windows.
- [As fluid as it gets on r/unixporn](https://www.reddit.com/r/unixporn/comments/1s84jik/hyprland_as_fluid_as_it_gets/): using motion to show interaction and theme changes.
- [rxyhn / Tokyo](https://github.com/rxyhn/tokyo): a consistent palette and grouped desktop views.

These were composition and documentation references. Their screenshots, wallpaper
art, logos and README prose are not copied into ALPORA. Downloaded reference
images were reviewed outside the repository and are not redistributed here.

[Artwork provenance](../artwork.md) · [Third-party notices](../../THIRD_PARTY_NOTICES.md)
