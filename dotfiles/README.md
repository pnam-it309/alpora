# ALPORA User Dotfiles Repository (`dotfiles/`)

This directory contains user-stowable dotfile packages managed by **GNU Stow** and the ALPORA automated installer.

## Directory Structure
Each subfolder corresponds to an individual Stow package structured according to the XDG Base Directory specification:
* `hypr/` -> `.config/hypr/` (Hyprland compositor configuration, session rules, gestures)
* `foot/` -> `.config/foot/` (Foot terminal emulator configuration and color syncing)
* `kitty/` -> `.config/kitty/` (Kitty secondary terminal configuration)
* `fcitx5/` -> `.config/fcitx5/` (Vietnamese/international input method profiles)
* `fontconfig/` -> `.config/fontconfig/` (Typography hierarchy and fallback fonts)
* `fastfetch/` -> `.config/fastfetch/` (Terminal fetch configuration)
* `poly-shell/` -> `.config/quickshell/poly-shell/` (Shell links)
* `systemd/` -> `.config/systemd/user/` (User systemd services)

## Deployment Commands
To link or re-link dotfiles to `$HOME`:
```bash
./scripts/stow-dotfiles.sh link
```
To unlink:
```bash
./scripts/stow-dotfiles.sh unlink
```
