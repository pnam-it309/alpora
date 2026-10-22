# Poly World — Alpine artwork v1

Generated using the built-in image_gen tool on 2026-10-21.
These are still-image source assets, not an installed animated wallpaper.
Exact generation prompts are recorded in prompts.json.

## Files

- panorama.png: continuous lake → forest/cabin → rocky slope environment.
- foreground.png: transparent foreground rocks, grass and evergreen branches.
- clouds.png: transparent sunset cloud overlay.

All images are 2172 × 724 pixels (3:1), the actual generator output.
They are not 4K sources. Transparency was verified in both RGBA overlays.
Review translucent edges against the intended sky before runtime use.

## Animation direction for implementation

- Slow cloud translation independent of the camera; clip clouds to the sky
  or constrain their height so they do not pass in front of the mountains.
- Gentle masked water distortion, preserving the bank, dock and cabin.
- A separate procedural smoke effect anchored to the cabin chimney.
- Faster foreground parallax during workspace transitions.
- The source forest remains baked into the base; independent tree swaying
  requires extra extracted assets/masks and is not delivered by these PNGs.

The 3:1 panorama provides overlapping 16:9 views, not three disjoint 16:9
wallpapers: the view width is about 59.3% of the panorama width. A starting
camera arrangement is left / center / right with overlapping scenery.
The right region is a rocky lakeshore slope rather than an entirely separate pass.

A renderer should respect reduced motion, suspend when the background is fully
covered or the session sleeps, and keep Work/Vibe independent of the theme.
No shell configuration or current wallpaper has been changed by this asset batch.

