# Radial theme menu — proposal v1

Generated with the built-in image_gen tool on 2026-10-21.
Image: `theme-wheel-proposal-v1.png`.
Edit target: `desktop-before-theme-wheel-20261021.png`, captured by the preceding session.
This is a visual proposal only; desktop input and theme switching are not implemented by this image.

## Intended interaction

- Right-click or two-finger secondary click on empty desktop opens the menu at the pointer, constrained to the available screen area.
- Seven cards represent the existing six themes and Timeline.
- The current theme has an outline and check mark; selecting another applies the existing theme workflow.
- Outside click and Escape dismiss the menu. Work/Vibe remains independent.
- Implementation must use semantic theme colors, existing thumbnail assets and configured radius/opacity/motion. Generated thumbnails here are illustrative.

## Generation prompt

Use case: ui-mockup.
Asset type: high fidelity visual reference for Poly Shell Hyprland desktop radial theme selector.
Input image 1 is the EDIT TARGET: a real 1920x1080 screenshot of the user's empty desktop. Preserve its low-poly alpine lake sunrise wallpaper, entire top bar, left clock widget and right weather and music widgets exactly in their original positions and scale. Add only a beautiful usable circular theme-selection context menu over the open center of the wallpaper, approximately centered at x=995,y=565 and about 580px across. Render a single full-screen desktop screenshot with no surrounding frame, no presentation captions.
Menu design: seven distinct rounded landscape-thumbnail cards arranged evenly around an open circular hub, genuinely radial, not a rectangular settings window or a list. Card sizes roughly 132x86 px, with compact readable Russian labels below each thumbnail. Use low-poly miniature landscape artwork for each theme: alpine sunrise mountains, moonlit blue lake, misty green forest, warm ochre desert, aurora over snowy mountains, pink sunset, and Timeline day/night landscape. Exactly seven options, no duplicates. Labels: "Альпийский рассвет", "Лунное озеро", "Лесной туман", "Тёплая пустыня", "Северное сияние", "Розовый закат", "Timeline". Break long labels onto two lines if needed. A thin sage outline and tiny check badge marks the Alpine thumbnail as selected. Each card has a compact dark charcoal-sage backing, rounded corners and subtle stroke matching existing widgets. Center is a restrained dark round hub about 150px diameter with a small faceted mountain icon and legible text "Темы" and smaller "Альпийский рассвет". Subtle connecting arc, tasteful depth and faint shadow; the wallpaper stays clearly visible between separate cards. Overall deliberate beautiful low-poly/stylized desktop product design. Keep hub and cards compact with ample separation, restrained sage/cream/charcoal palette sampled from existing shell, no neon, no massive backdrop, no full-screen darkening, no big blur, no sci-fi holograms, no extra application windows, no change to existing widgets or wallpaper. A small mouse cursor near selected theme makes this feel like an actual context menu. High quality sharp typography.
