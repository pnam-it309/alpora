#!/usr/bin/env bash
# ==============================================================================
# ALPORA Dotfiles Setup & Bootstrap Script
# ==============================================================================
# Automates GNU Stow symlinking, systemd service enablement, and dependency audit.

set -euo pipefail

DOTFILES_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME:-/home/$USER}"

echo "========================================================================"
echo "          ALPORA Desktop Environment - Dotfiles Setup                   "
echo "========================================================================"
echo "Source: $DOTFILES_DIR"
echo "Target: $TARGET_DIR"
echo ""

# 1. Check for GNU Stow
if ! command -v stow >/dev/null 2>&1; then
    echo "[!] GNU Stow is required to manage dotfile symlinks."
    echo "    On Arch Linux: sudo pacman -S --needed stow"
    exit 1
fi

# 2. Check essential dependencies
echo "[1/4] Checking core desktop dependencies..."
missing_deps=()
for dep in hyprland quickshell python3 fcitx5 foot systemd; do
    if ! command -v "$dep" >/dev/null 2>&1; then
        missing_deps+=("$dep")
    fi
done

if [[ ${#missing_deps[@]} -gt 0 ]]; then
    echo "  [Notice] The following packages are not yet in PATH:"
    for md in "${missing_deps[@]}"; do
        echo "    - $md"
    done
    echo "  You can continue symlinking now and install missing packages later via pacman."
    echo ""
else
    echo "  [OK] All core dependencies detected."
fi

# 3. Create target directory structure
echo "[2/4] Preparing target directories..."
mkdir -p "$TARGET_DIR/.config/hypr"
mkdir -p "$TARGET_DIR/.config/poly-shell"
mkdir -p "$TARGET_DIR/.config/foot"
mkdir -p "$TARGET_DIR/.config/kitty"
mkdir -p "$TARGET_DIR/.config/fcitx5/conf"
mkdir -p "$TARGET_DIR/.config/fastfetch"
mkdir -p "$TARGET_DIR/.config/systemd/user"
mkdir -p "$TARGET_DIR/.local/bin"

# 4. Run GNU Stow for each package
echo "[3/4] Symlinking dotfiles via GNU Stow..."
packages=(
    "hypr"
    "poly-shell"
    "foot"
    "kitty"
    "fcitx5"
    "shell"
    "fastfetch"
    "systemd"
)

cd "$DOTFILES_DIR"
for pkg in "${packages[@]}"; do
    if [[ -d "$pkg" ]]; then
        echo "  -> Stowing package: $pkg"
        stow -v -R -t "$TARGET_DIR" "$pkg" 2>&1 | sed 's/^/     /'
    fi
done

# 5. Enable & start ALPORA systemd user service
echo "[4/4] Configuring systemd user services..."
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload || true
    if systemctl --user enable poly-shell.service 2>/dev/null; then
        echo "  [OK] poly-shell.service enabled for user session."
        if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
            systemctl --user start poly-shell.service || true
            echo "  [OK] poly-shell.service started in current Wayland session."
        fi
    else
        echo "  [Notice] Could not enable systemd service (headless or non-systemd environment)."
    fi
fi

echo ""
echo "========================================================================"
echo "          ALPORA Dotfiles Successfully Installed!                       "
echo "========================================================================"
echo "Next Steps:"
echo "  1. Log into your Hyprland session (or start from TTY via 'Hyprland')."
echo "  2. ALPORA and Fcitx5 will autostart via exec-once."
echo "  3. Key shortcuts to remember:"
echo "     - Super + Enter  : Terminal (Foot)"
echo "     - Super + Space  : App Launcher"
echo "     - Super + I      : Quick Settings Panel"
echo "     - Super + Tab    : Workspace Overview"
echo "     - Super + L      : Lock Screen"
echo "     - Ctrl + Shift   : Switch Vietnamese / English Input"
echo "  4. Run health check at any time:"
echo "     poly-shell doctor"
echo "========================================================================"

