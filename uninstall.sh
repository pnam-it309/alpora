#!/usr/bin/env bash
# ALPORA clean uninstaller. Run as your normal desktop user.
set -euo pipefail

uninstall_dry_run=false
uninstall_purge=false
uninstall_restore_config=false

for argument in "$@"; do
    case "$argument" in
        --dry-run) uninstall_dry_run=true ;;
        --purge) uninstall_purge=true ;;
        --restore-config) uninstall_restore_config=true ;;
        -h|--help)
            cat <<'HELP'
ALPORA uninstaller
Usage: ./uninstall.sh [OPTIONS]

  --dry-run          Print actions that would be performed without removing files.
  --restore-config   Restore latest Hyprland configuration backup if available.
  --purge            Remove all ALPORA user configuration and state (~/.config/poly-shell, ~/.local/state/poly-shell).

Removes:
  - User symlinks: ~/.local/bin/poly-shell, ~/.local/bin/alpora-fetch
  - Quickshell UI symlink: ~/.config/quickshell/poly-shell
  - Systemd user service: ~/.config/systemd/user/poly-shell.service
  - Desktop launcher: ~/.local/share/applications/poly-shell-settings.desktop
HELP
            exit 0 ;;
        *) printf 'Unknown option: %s\n' "$argument" >&2; exit 2 ;;
    esac
done

if [[ "$EUID" -eq 0 ]]; then
    echo 'Run ./uninstall.sh as your normal user, without sudo.' >&2
    exit 1
fi

echo "=== ALPORA Uninstaller ==="

config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
state_home="${XDG_STATE_HOME:-$HOME/.local/state}"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
bin_dir="$HOME/.local/bin"

# 1. Stop active services and running instances
if [[ "$uninstall_dry_run" == true ]]; then
    echo "[dry-run] Would stop poly-shell service and running instance"
else
    echo "Stopping poly-shell service..."
    systemctl --user stop poly-shell.service 2>/dev/null || true
    systemctl --user disable poly-shell.service 2>/dev/null || true
    if command -v poly-shell >/dev/null 2>&1; then
        poly-shell stop 2>/dev/null || true
    fi
fi

# 2. Files and symlinks to remove
targets=(
    "$bin_dir/poly-shell"
    "$bin_dir/alpora-fetch"
    "$config_home/quickshell/poly-shell"
    "$config_home/systemd/user/poly-shell.service"
    "$data_home/applications/poly-shell-settings.desktop"
)

for target in "${targets[@]}"; do
    if [[ -e "$target" || -L "$target" ]]; then
        if [[ "$uninstall_dry_run" == true ]]; then
            echo "[dry-run] Would remove: $target"
        else
            echo "Removing: $target"
            rm -rf "$target"
        fi
    fi
done

if [[ "$uninstall_dry_run" != true ]]; then
    systemctl --user daemon-reload 2>/dev/null || true
fi

# 3. Check for Hyprland configuration backups
backup_dir="$state_home/poly-shell/backups"
latest_backup=""
if [[ -d "$backup_dir" ]]; then
    latest_backup=$(ls -dt "$backup_dir"/arch-install-* 2>/dev/null | head -n 1 || true)
fi

if [[ -n "$latest_backup" && -d "$latest_backup/hypr" ]]; then
    hypr_dir="$config_home/hypr"
    if [[ "$uninstall_restore_config" == true ]]; then
        if [[ "$uninstall_dry_run" == true ]]; then
            echo "[dry-run] Would restore Hyprland configuration from: $latest_backup/hypr -> $hypr_dir"
        else
            echo "Restoring Hyprland configuration from $latest_backup/hypr..."
            rm -rf "$hypr_dir"
            cp -a "$latest_backup/hypr" "$hypr_dir"
            echo "Restored Hyprland configuration to $hypr_dir"
        fi
    else
        echo ""
        echo "Found existing Hyprland backup at:"
        echo "  $latest_backup/hypr"
        echo "To restore it to $hypr_dir, run:"
        echo "  ./uninstall.sh --restore-config"
    fi
fi

# 4. Purge configs if requested
if [[ "$uninstall_purge" == true ]]; then
    purge_targets=(
        "$config_home/poly-shell"
        "$state_home/poly-shell"
        "$data_home/alpora"
        "$HOME/.cache/alpora"
    )
    for p_target in "${purge_targets[@]}"; do
        if [[ -d "$p_target" ]]; then
            if [[ "$uninstall_dry_run" == true ]]; then
                echo "[dry-run] Would purge directory: $p_target"
            else
                echo "Purging directory: $p_target"
                rm -rf "$p_target"
            fi
        fi
    done
fi

echo ""
if [[ "$uninstall_dry_run" == true ]]; then
    echo "Dry-run complete. No files were modified."
else
    echo "ALPORA has been successfully uninstalled."
fi
