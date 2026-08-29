#!/bin/bash
set -e

echo "[1/4] Instalando tema Nordic para o SDDM..."
pacman -S --noconfirm --needed sddm-nordic-theme-git

THEME_DIR=$(find /usr/share/sddm/themes -maxdepth 1 -iname "*nordic*" | head -n 1)

if [ -z "$THEME_DIR" ]; then
    echo "Erro: pasta do tema nordic não encontrada em /usr/share/sddm/themes"
    exit 1
fi

THEME_NAME=$(basename "$THEME_DIR")
echo "Tema detectado: $THEME_NAME ($THEME_DIR)"

echo "[2/4] Aplicando wallpaper estático do Totoro no tema Nordic..."
# Substituir possíveis arquivos de fundo do Nordic
find "$THEME_DIR" -type f \( -iname "*background*" -o -iname "*wall*" -o -iname "*.jpg" -o -iname "*.png" \) -exec cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png {} + 2>/dev/null || true

# Configurar theme.conf se existir
if [ -f "$THEME_DIR/theme.conf" ]; then
    cp /home/lenin/Downloads/Wallpapers/totoro-stargazing-moewalls-com.png "$THEME_DIR/totoro.png"
    sed -i 's|^background=.*|background=totoro.png|g' "$THEME_DIR/theme.conf"
    sed -i 's|^Background=.*|Background=totoro.png|g' "$THEME_DIR/theme.conf"
fi

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
echo ""
echo "Para testar a prévia, rode:"
echo "sddm-greeter-qt6 --test-mode --theme $THEME_DIR"
