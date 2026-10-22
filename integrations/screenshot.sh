#!/usr/bin/env bash
set -euo pipefail
region="$(slurp)" || exit 0
pictures="$(xdg-user-dir PICTURES)"
mkdir -p "$pictures/Screenshots"
output="$pictures/Screenshots/ALPORA-$(date +%Y%m%d-%H%M%S-%N).png"
grim -g "$region" "$output"
wl-copy --type image/png < "$output"
notify-send 'ALPORA' "Screenshot saved: $output"
