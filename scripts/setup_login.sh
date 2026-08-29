#!/bin/bash
set -e

echo "Restaurando tema padrão do SDDM com seu usuário pré-selecionado..."
cat > /etc/sddm.conf.d/wayland.conf << "EOF"
[General]
DisplayServer=wayland
GreeterEnvironment=XCURSOR_THEME=capitaine-cursors,XCURSOR_SIZE=24

[Wayland]
CompositorCommand=weston --shell=kiosk

[Theme]
CursorTheme=capitaine-cursors
CursorSize=24
EOF

echo "✓ Restaurado!"
