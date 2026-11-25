# ALPORA System Reference Configuration (`config/`)

This directory contains pristine, reference configuration files and templates for the ALPORA Desktop Environment.

## Purpose & Distribution
* **Packaging Target:** Installed by Arch PKGBUILD to `/usr/share/alpora/config/` as system defaults.
* **Fallback & Recovery:** Used when creating fresh user profiles, resetting desktop configurations, or installing in non-Stow environments.

## Relationship with `dotfiles/`
* `dotfiles/` contains package-structured directories (`<pkg>/.config/...`) specifically tailored for **GNU Stow** symlink management and live user deployment.
* Changes to desktop configurations (such as Hyprland keybindings, Foot terminal styling, or Fcitx5 IME settings) should be maintained in both trees to keep system defaults and live dotfiles in sync.
