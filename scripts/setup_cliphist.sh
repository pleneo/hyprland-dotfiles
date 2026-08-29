#!/bin/bash
set -e

echo "[1/4] Instalando cliphist..."
sudo pacman -S --noconfirm --needed cliphist

echo "[2/4] Criando tema do clipboard para o Rofi..."
cat > /home/lenin/.config/rofi/clipboard.rasi << "EOF"
/* Rofi Modern Clipboard Theme */
@import "/home/lenin/.cache/wal/colors-rofi-dark.rasi"

configuration {
    font: "JetBrainsMono Nerd Font 11";
}

* {
    background-color: transparent;
    text-color: @foreground;
}

window {
    transparency: "real";
    location: center;
    anchor: center;
    fullscreen: false;
    width: 680px;
    border: 2px solid;
    border-radius: 20px;
    border-color: @selected-active-background;
    background-color: @background;
    cursor: "default";
}

mainbox {
    spacing: 12px;
    padding: 20px;
    background-color: transparent;
    children: [ "inputbar", "listview" ];
}

inputbar {
    spacing: 12px;
    padding: 12px 16px;
    border-radius: 14px;
    background-color: rgba(255, 255, 255, 0.05);
    text-color: @foreground;
    children: [ "prompt", "entry" ];
}

prompt {
    background-color: transparent;
    text-color: @selected-active-background;
    font: "JetBrainsMono Nerd Font 14";
    vertical-align: 0.5;
}

entry {
    background-color: transparent;
    text-color: @foreground;
    cursor: text;
    placeholder: "";
    vertical-align: 0.5;
}

listview {
    columns: 1;
    lines: 8;
    cycle: true;
    dynamic: true;
    scrollbar: false;
    layout: vertical;
    fixed-height: true;
    fixed-columns: true;
    spacing: 6px;
    background-color: transparent;
    text-color: @foreground;
}

element {
    spacing: 12px;
    padding: 10px 14px;
    border-radius: 12px;
    background-color: transparent;
    text-color: @foreground;
    cursor: pointer;
}

element normal.normal {
    background-color: transparent;
    text-color: @foreground;
}

element selected.normal {
    background-color: @selected-active-background;
    text-color: @background;
}

element-text {
    background-color: transparent;
    text-color: inherit;
    highlight: inherit;
    cursor: inherit;
    vertical-align: 0.5;
    horizontal-align: 0.0;
}
EOF

echo "[3/4] Criando script de launcher do clipboard..."
cat > /home/lenin/.config/rofi/cliphist.sh << "EOF"
#!/usr/bin/env bash

# Abrir menu do cliphist via Rofi
SELECTION=$(cliphist list | rofi -dmenu -i -p " " -theme ~/.config/rofi/clipboard.rasi)

if [ -n "$SELECTION" ]; then
    echo "$SELECTION" | cliphist decode | wl-copy
fi
EOF

chmod +x /home/lenin/.config/rofi/cliphist.sh

echo "[4/4] Concluído com sucesso!"
