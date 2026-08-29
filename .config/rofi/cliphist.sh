#!/usr/bin/env bash

# Abrir menu do cliphist via Rofi
SELECTION=$(cliphist list | rofi -dmenu -i -p " " -theme ~/.config/rofi/clipboard.rasi)

if [ -n "$SELECTION" ]; then
    echo "$SELECTION" | cliphist decode | wl-copy
fi
