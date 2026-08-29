#!/bin/bash
set -e

echo "[1/4] Instalando sddm-astronaut-theme via paru (AUR)..."
if ! pacman -Qi sddm-astronaut-theme >/dev/null 2>&1; then
    paru -S --needed sddm-astronaut-theme
fi

THEME_DIR=$(find /usr/share/sddm/themes -maxdepth 1 -iname "*astronaut*" | head -n 1)

if [ -z "$THEME_DIR" ]; then
    echo "Erro: pasta do tema astronaut não encontrada em /usr/share/sddm/themes"
    exit 1
fi

THEME_NAME=$(basename "$THEME_DIR")
echo "Tema detectado: $THEME_NAME ($THEME_DIR)"

echo "[2/4] Copiando wallpaper estático do Totoro..."
sudo cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png "$THEME_DIR/totoro.png"

echo "[3/4] Configurando wallpaper no tema Astronaut..."
if [ -f "$THEME_DIR/theme.conf.user" ]; then
    sudo sed -i 's|^Background=.*|Background="totoro.png"|g' "$THEME_DIR/theme.conf.user"
    sudo sed -i 's|^background=.*|background="totoro.png"|g' "$THEME_DIR/theme.conf.user"
fi
if [ -f "$THEME_DIR/theme.conf" ]; then
    sudo sed -i 's|^Background=.*|Background="totoro.png"|g' "$THEME_DIR/theme.conf"
    sudo sed -i 's|^background=.*|background="totoro.png"|g' "$THEME_DIR/theme.conf"
fi

echo "[4/4] Atualizando configuração do SDDM..."
sudo bash -c "cat > /etc/sddm.conf.d/wayland.conf << EOF
[General]
DisplayServer=wayland
GreeterEnvironment=XCURSOR_THEME=capitaine-cursors,XCURSOR_SIZE=24

[Wayland]
CompositorCommand=weston --shell=kiosk

[Theme]
Current=$THEME_NAME
CursorTheme=capitaine-cursors
CursorSize=24
EOF"

echo "✓ Concluído com sucesso!"
echo ""
echo "Para testar a prévia na tela, rode:"
echo "sddm-greeter-qt6 --test-mode --theme $THEME_DIR"
