#!/bin/bash
set -e

echo "[1/4] Instalando tema oficial do CachyOS para o SDDM..."
pacman -S --noconfirm --needed cachyos-themes-sddm

THEME_DIR=$(find /usr/share/sddm/themes -maxdepth 1 -name "cachyos*" | head -n 1)

if [ -z "$THEME_DIR" ]; then
    echo "Erro: pasta do tema cachyos não encontrada em /usr/share/sddm/themes"
    exit 1
fi

THEME_NAME=$(basename "$THEME_DIR")
echo "Tema detectado: $THEME_NAME"

echo "[2/4] Aplicando wallpaper estático do Totoro no tema do CachyOS..."
if [ -f "$THEME_DIR/background.jpg" ]; then
    cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png "$THEME_DIR/background.jpg"
fi
if [ -f "$THEME_DIR/background.png" ]; then
    cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png "$THEME_DIR/background.png"
fi
if [ -f "$THEME_DIR/Background.png" ]; then
    cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png "$THEME_DIR/Background.png"
fi

# Copiar como fallback
cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png "$THEME_DIR/totoro.png"

echo "[3/4] Atualizando configuração do SDDM..."
cat > /etc/sddm.conf.d/wayland.conf << EOF
[General]
DisplayServer=wayland
GreeterEnvironment=XCURSOR_THEME=capitaine-cursors,XCURSOR_SIZE=24

[Wayland]
CompositorCommand=weston --shell=kiosk

[Theme]
Current=$THEME_NAME
CursorTheme=capitaine-cursors
CursorSize=24
EOF

echo "[4/4] Concluído com sucesso!"
echo "Para testar, rode:"
echo "sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/$THEME_NAME"
