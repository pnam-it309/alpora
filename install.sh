#!/usr/bin/env bash
# ALPORA bootstrap for Arch Linux. Run as your normal desktop user.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_dry_run=false
install_skip_packages=false
install_replace_config=false
install_theme=''
install_wizard=false
install_preview=false
source "$project_dir/integrations/installer-ui.sh"
for argument in "$@"; do
    case "$argument" in
        --dry-run) install_dry_run=true ;;
        --skip-packages) install_skip_packages=true ;;
        --replace-config) install_replace_config=true ;;
        --theme=*) install_theme=${argument#--theme=} ;;
        --wizard) install_wizard=true ;;
        --preview) install_preview=true ;;
        -h|--help)
            cat <<'HELP'
ALPORA installer for Arch Linux
Usage: ./install.sh [--dry-run] [--skip-packages] [--replace-config] [--theme=ID]

  --dry-run         Print the plan without downloading or changing anything.
  --skip-packages   Use already installed dependencies (development/testing).
  --replace-config  Back up and replace an existing Hyprland configuration.
  --theme=ID        Choose alpine, moon-lake, forest-mist, warm-desert,
                    northern-lights, rose-sunset or timeline.
  --wizard          Show the theme chooser, including with --dry-run.
  --preview         Show only the welcome screen; never install or change files.

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
source /etc/os-release
if [[ "$ID" != arch ]]; then
    echo 'This installer currently supports Arch Linux only.' >&2
    exit 1
fi
packages=(
    hyprland quickshell qt6-svg qt6-imageformats qt6-multimedia
    python python-pillow python-gobject gtk3 glib2
    pipewire pipewire-pulse wireplumber upower networkmanager nm-connection-editor
    bluez bluez-utils brightnessctl power-profiles-daemon
    hyprlock hypridle hyprsunset hyprpolkitagent
    xdg-desktop-portal xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
    mako swaybg foot kitty nautilus firefox fuzzel pavucontrol hyprshutdown
    wl-clipboard grim slurp libnotify playerctl xdg-utils xdg-user-dirs
    noto-fonts noto-fonts-emoji adwaita-icon-theme git curl
)
alpora_colour
alpora_banner
if [[ -t 0 && -t 1 && -z "$install_theme" && ( "$install_dry_run" != true || "$install_wizard" == true ) ]]; then
    alpora_choose_theme
fi
alpora_summary
if [[ "$install_dry_run" == true ]]; then
    printf 'ALPORA installation plan (no changes)\nProject: %s\n' "$project_dir"
    printf 'Packages: %s\n' "${packages[*]}"
    echo '1. Fully update Arch and install packages with pacman (unless --skip-packages).'
    echo '2. Download pinned, checksum-verified Papirus and Bibata themes into user data.'
    echo '3. Back up existing Hyprland configuration; require consent before replacement.'
    echo '4. Install ALPORA, session startup, default keybindings, lock and screenshot helpers.'
    echo '5. Apply icon/cursor settings; prepare the selected theme for next login.'
    echo '6. Enable NetworkManager/Bluetooth and user audio services when appropriate.'
    echo 'No drivers, bootloader or display manager will be modified.'
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
alpora_step 1 'Prepare Arch Linux'
if [[ "$install_skip_packages" != true ]]; then
    command -v sudo >/dev/null || { echo 'Install sudo and allow your user to manage packages first.' >&2; exit 1; }
    sudo pacman -Syu --needed "${packages[@]}" 2>&1 | tee -a "$ALPORA_INSTALL_LOG"
else
    printf '    Packages skipped by request; runtime dependencies will be checked.\n'
fi
arguments=()
if [[ "$install_replace_config" == true ]]; then arguments+=(--replace-config); fi
if [[ -n "$install_theme" ]]; then arguments+=(--theme "$install_theme"); fi
python3 "$project_dir/scripts/setup-arch-desktop" "${arguments[@]}"
