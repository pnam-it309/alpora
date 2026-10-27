#!/usr/bin/env bash
# ALPORA bootstrap for Arch Linux and Arch-based distributions. Run as your normal desktop user.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_dry_run=false
install_skip_packages=false
install_replace_config=false
install_ui_only=false
install_core_only=false
install_ignore_distro=false
install_theme=''
install_wizard=false
install_preview=false
source "$project_dir/integrations/installer-ui.sh"
for argument in "$@"; do
    case "$argument" in
        --dry-run) install_dry_run=true ;;
        --skip-packages) install_skip_packages=true ;;
        --replace-config) install_replace_config=true ;;
        --ui-only) install_ui_only=true; install_skip_packages=true ;;
        --core-only|--minimal) install_core_only=true ;;
        --ignore-distro-check|--force-distro) install_ignore_distro=true ;;
        --uninstall)
            exec "$project_dir/uninstall.sh" "${@:2}"
            ;;
        --theme=*) install_theme=${argument#--theme=} ;;
        --wizard) install_wizard=true ;;
        --preview) install_preview=true ;;
        -h|--help)
            cat <<'HELP'
ALPORA installer for Arch Linux and Arch-based distributions
Usage: ./install.sh [OPTIONS]

  --ui-only               Install standalone ALPORA UI shell only. Does NOT install system
                          packages and does NOT alter existing Hyprland configuration.
                          Ideal for custom Arch kernels (zen/lts/hardened), non-Arch distros, or custom setups.
  --minimal, --core-only  Install only core compositor & shell packages (~28 packages);
                          skips bundled applications (Firefox, Nautilus, Kitty, Foot, Fuzzel, etc.).
  --ignore-distro-check   Bypass Arch distribution detection and attempt pacman installation.
  --uninstall             Cleanly remove ALPORA symlinks, services, and optionally restore configs.
  --dry-run               Print the plan without downloading or changing anything.
  --skip-packages         Use already installed dependencies (development/testing).
  --replace-config        Back up and replace an existing Hyprland configuration.
  --theme=ID              Choose alpine, moon-lake, forest-mist, warm-desert,
                          northern-lights, rose-sunset or timeline.
  --wizard                Show the theme chooser, including with --dry-run.
  --preview               Show only the welcome screen; never install or change files.

Run as a normal user, not with sudo. The package step invokes sudo itself.
An existing session configuration requires explicit replacement consent.
HELP
            exit 0 ;;
        *) printf 'Unknown option: %s\n' "$argument" >&2; exit 2 ;;
    esac
done
case "$install_theme" in
    ''|alpine|moon-lake|forest-mist|warm-desert|northern-lights|rose-sunset|timeline) ;;
    *) printf 'Unknown theme: %s\n' "$install_theme" >&2; exit 2 ;;
esac
if [[ "$install_preview" == true ]]; then
    if [[ "$install_wizard" == true && -t 0 && -t 1 && -z "$install_theme" ]]; then
        alpora_choose_theme
    fi
    if command -v python3 >/dev/null; then
        preview_arguments=()
        if [[ -n "$install_theme" ]]; then preview_arguments+=(--theme "$install_theme"); fi
        "$project_dir/bin/alpora-fetch" "${preview_arguments[@]}"
    else
        alpora_colour
        alpora_banner
        alpora_summary
    fi
    printf '\n  PREVIEW / No installation or system changes.\n\n'
    exit 0
fi
if [[ "$EUID" -eq 0 && "$install_dry_run" != true ]]; then
    echo 'Run ./install.sh as your normal user, without sudo.' >&2
    exit 1
fi

is_arch_based=false
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    if [[ "${ID:-}" == "arch" || "${ID_LIKE:-}" =~ (^|[[:space:]])arch([[:space:]]|$) || "${ID:-}" =~ ^(endeavouros|cachyos|manjaro|garuda|artix|arcolinux|archcraft)$ ]]; then
        is_arch_based=true
    fi
fi

if [[ "$install_ui_only" != true && "$install_ignore_distro" != true ]]; then
    if [[ "$is_arch_based" != true ]]; then
        printf 'This full installer currently supports Arch Linux and Arch-based distributions.\n' >&2
        printf 'Detected: %s (%s)\n' "${NAME:-Unknown}" "${ID:-unknown}" >&2
        printf 'Tip: Use ./install.sh --ui-only to install the standalone ALPORA UI on any distro or custom kernel setup.\n' >&2
        printf '     Use ./install.sh --ignore-distro-check to force pacman package installation on this system.\n' >&2
        exit 1
    fi
fi

core_packages=(
    hyprland quickshell qt6-svg qt6-imageformats qt6-multimedia
    python python-pillow python-gobject gtk3 glib2
    pipewire pipewire-pulse wireplumber upower networkmanager nm-connection-editor
    bluez bluez-utils brightnessctl power-profiles-daemon
    hyprlock hypridle hyprsunset hyprpolkitagent
    xdg-desktop-portal xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
    swaybg wl-clipboard grim slurp libnotify playerctl xdg-utils xdg-user-dirs
    noto-fonts noto-fonts-emoji adwaita-icon-theme git curl
)

bundled_apps=(
    mako foot kitty nautilus firefox fuzzel pavucontrol hyprshutdown
)

if [[ "$install_core_only" == true ]]; then
    packages=("${core_packages[@]}")
else
    packages=("${core_packages[@]}" "${bundled_apps[@]}")
fi

alpora_colour
alpora_banner
if [[ -t 0 && -t 1 && -z "$install_theme" && ( "$install_dry_run" != true || "$install_wizard" == true ) ]]; then
    alpora_choose_theme
fi
alpora_summary
if [[ "$install_dry_run" == true ]]; then
    printf 'ALPORA installation plan (no changes)\nProject: %s\n' "$project_dir"
    if [[ "$install_ui_only" == true ]]; then
        echo 'Mode: Standalone UI only (no system packages, no Hyprland config changes)'
        echo '1. Link poly-shell, alpora-fetch, and quickshell QML UI.'
        echo '2. Seed user preferences and themes.'
        echo '3. Install systemd user service poly-shell.service.'
    else
        printf 'Packages (%d): %s\n' "${#packages[@]}" "${packages[*]}"
        echo '1. Fully update Arch/derivative and install packages with pacman (unless --skip-packages).'
        echo '2. Download pinned, checksum-verified Papirus and Bibata themes into user data.'
        echo '3. Back up existing Hyprland configuration; require consent before replacement.'
        echo '4. Install ALPORA, session startup, default keybindings, lock and screenshot helpers.'
        echo '5. Apply icon/cursor settings; prepare the selected theme for next login.'
        echo '6. Enable NetworkManager/Bluetooth and user audio services when appropriate.'
        echo 'No drivers, bootloader or display manager will be modified.'
    fi
    exit 0
fi
install_log_dir="${XDG_STATE_HOME:-$HOME/.local/state}/poly-shell/install-logs"
mkdir -p "$install_log_dir"
chmod 700 "$install_log_dir"
ALPORA_INSTALL_LOG="$install_log_dir/$(date +%Y%m%d-%H%M%S)-$$.log"
export ALPORA_INSTALL_LOG
touch "$ALPORA_INSTALL_LOG"
chmod 600 "$ALPORA_INSTALL_LOG"
printf '\n  Installation log: %s\n' "$ALPORA_INSTALL_LOG"
trap 'printf "\n  Installation stopped. Review the log: %s\n" "$ALPORA_INSTALL_LOG" >&2' ERR

if [[ "$install_ui_only" == true ]]; then
    alpora_step 1 'Prepare ALPORA Standalone UI'
    printf '    UI-only mode enabled: skipping system package installation and pacman updates.\n'
else
    alpora_step 1 'Prepare Arch Linux & Dependencies'
    if [[ "$install_skip_packages" != true ]]; then
        command -v sudo >/dev/null || { echo 'Install sudo and allow your user to manage packages first.' >&2; exit 1; }
        sudo pacman -Syu --needed "${packages[@]}" 2>&1 | tee -a "$ALPORA_INSTALL_LOG"
    else
        printf '    Packages skipped by request; runtime dependencies will be checked.\n'
    fi
fi

arguments=()
if [[ "$install_ui_only" == true ]]; then arguments+=(--ui-only); fi
if [[ "$install_replace_config" == true ]]; then arguments+=(--replace-config); fi
if [[ -n "$install_theme" ]]; then arguments+=(--theme "$install_theme"); fi
python3 "$project_dir/scripts/setup-arch-desktop" "${arguments[@]}"
