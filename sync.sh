#!/usr/bin/env bash
# Script para sincronizar configurações locais para a pasta dotfiles e dar push no Git

set -e

DOTFILES_DIR="$HOME/dotfiles"

echo "[1/4] Atualizando cópias das configurações..."
mkdir -p "$DOTFILES_DIR/.config"/{hypr,waybar,rofi,mako,wlogout,alacritty,fish} "$DOTFILES_DIR/wallpapers" "$DOTFILES_DIR/scripts"

cp -r ~/.config/hypr/hyprland.lua ~/.config/hypr/hyprland.conf ~/.config/hypr/lua ~/.config/hypr/hyprlock.conf "$DOTFILES_DIR/.config/hypr/" 2>/dev/null || true
cp -r ~/.config/waybar/config ~/.config/waybar/style.css ~/.config/waybar/modules "$DOTFILES_DIR/.config/waybar/" 2>/dev/null || true
cp -r ~/.config/rofi/* "$DOTFILES_DIR/.config/rofi/" 2>/dev/null || true
cp -r ~/.config/mako/config "$DOTFILES_DIR/.config/mako/" 2>/dev/null || true
cp -r ~/.config/wlogout/* "$DOTFILES_DIR/.config/wlogout/" 2>/dev/null || true
cp -r ~/.config/alacritty/* "$DOTFILES_DIR/.config/alacritty/" 2>/dev/null || true
cp ~/.config/fish/config.fish "$DOTFILES_DIR/.config/fish/" 2>/dev/null || true
cp ~/.config/starship.toml "$DOTFILES_DIR/.config/" 2>/dev/null || true
cp ~/Downloads/Wallpapers/*.fish "$DOTFILES_DIR/wallpapers/" 2>/dev/null || true
cp ~/Documents/setup_*.sh "$DOTFILES_DIR/scripts/" 2>/dev/null || true

echo "[2/4] Verificando status do Git..."
cd "$DOTFILES_DIR"

git add -A

if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "Nenhuma alteração detectada para commit."
else
    echo "[3/4] Criando commit de backup..."
    git commit -m "backup: atualizacao automatica das configs $(date +'%Y-%m-%d %H:%M:%S')"
fi

echo "[4/4] Enviando para o GitHub..."
if git remote get-url origin >/dev/null 2>&1; then
    git push -u origin main
    echo "✅ Backup sincronizado com sucesso no GitHub!"
else
    echo "⚠️ Remote 'origin' ainda não configurado."
fi
