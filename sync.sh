#!/usr/bin/env bash
# ==============================================================================
# Script de sincronização do repositório de dotfiles
# Uso:
#   ~/dotfiles/sync.sh "feat(waybar): ajuste no estilo"
#   ~/dotfiles/sync.sh  (solicita mensagem ou gera descrição semântica automática)
# ==============================================================================

set -e

DOTFILES_DIR="$HOME/dotfiles"
COMMIT_MSG="$*"

echo "[1/4] Atualizando cópias das configurações locais..."
mkdir -p "$DOTFILES_DIR/.config"/{hypr,waybar,rofi,mako,wlogout,alacritty,fish} "$DOTFILES_DIR/wallpapers" "$DOTFILES_DIR/scripts"

cp -r ~/.config/hypr/hyprland.lua ~/.config/hypr/hyprland.conf ~/.config/hypr/lua ~/.config/hypr/hyprlock.conf ~/.config/hypr/hypr-ipc-proxy.py "$DOTFILES_DIR/.config/hypr/" 2>/dev/null || true
mkdir -p "$DOTFILES_DIR/.config/systemd/user"
cp ~/.config/systemd/user/hypr-ipc-proxy.service "$DOTFILES_DIR/.config/systemd/user/" 2>/dev/null || true
cp -r ~/.config/waybar/config ~/.config/waybar/style.css ~/.config/waybar/modules "$DOTFILES_DIR/.config/waybar/" 2>/dev/null || true
cp -r ~/.config/rofi/* "$DOTFILES_DIR/.config/rofi/" 2>/dev/null || true
cp -r ~/.config/mako/config "$DOTFILES_DIR/.config/mako/" 2>/dev/null || true
cp -r ~/.config/wlogout/* "$DOTFILES_DIR/.config/wlogout/" 2>/dev/null || true
cp -r ~/.config/alacritty/* "$DOTFILES_DIR/.config/alacritty/" 2>/dev/null || true
cp ~/.config/fish/config.fish "$DOTFILES_DIR/.config/fish/" 2>/dev/null || true
cp ~/.config/starship.toml "$DOTFILES_DIR/.config/" 2>/dev/null || true
cp ~/Downloads/Wallpapers/*.fish ~/Downloads/Wallpapers/*.rasi "$DOTFILES_DIR/wallpapers/" 2>/dev/null || true
cp -r ~/Downloads/Wallpapers/script "$DOTFILES_DIR/wallpapers/" 2>/dev/null || true
cp ~/Documents/setup_*.sh "$DOTFILES_DIR/scripts/" 2>/dev/null || true

# Remover credenciais ou arquivos sensíveis copiados por engano
find "$DOTFILES_DIR/.config" -type f \( -name "*auth*.json" -o -name "*token*.json" -o -name "*credentials*.json" -o -name "*secret*.json" \) ! -name "*.example" -delete 2>/dev/null || true

echo "[2/4] Verificando status do Git..."
cd "$DOTFILES_DIR"

git add -A

if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "✨ Nenhuma alteração detectada. O repositório já está 100% atualizado."
    exit 0
fi

# Se nenhuma mensagem foi passada como argumento no comando
if [ -z "$COMMIT_MSG" ]; then
    # Se estiver em terminal interativo, pergunta ao usuário
    if [ -t 0 ]; then
        echo ""
        read -r -p "📝 Digite a mensagem do commit (Enter para gerar automaticamente): " USER_MSG
        COMMIT_MSG="$USER_MSG"
    fi
fi

# Se continuar vazio, analisa os arquivos modificados e gera uma mensagem semântica
if [ -z "$COMMIT_MSG" ]; then
    SCOPES=$(git diff --cached --name-only | while read -r f; do
        case "$f" in
            .config/hypr/*) echo "hypr" ;;
            .config/waybar/*) echo "waybar" ;;
            .config/rofi/*) echo "rofi" ;;
            .config/mako/*) echo "mako" ;;
            .config/wlogout/*) echo "wlogout" ;;
            .config/alacritty/*) echo "alacritty" ;;
            .config/fish/*) echo "fish" ;;
            .config/starship.toml) echo "starship" ;;
            wallpapers/*) echo "wallpapers" ;;
            scripts/*) echo "scripts" ;;
            README.md) echo "docs" ;;
            *) echo "misc" ;;
        esac
    done | sort -u | paste -sd, - | sed 's/,/, /g')

    if [ -z "$SCOPES" ]; then
        SCOPES="config"
    fi

    COMMIT_MSG="update($SCOPES): sync configuration changes"
fi

echo "[3/4] Criando commit: \"$COMMIT_MSG\"..."
git commit -m "$COMMIT_MSG"

echo "[4/4] Enviando para o GitHub..."
if git remote get-url origin >/dev/null 2>&1; then
    git push -u origin main
    echo "✅ Alterações enviadas com sucesso para o GitHub!"
else
    echo "⚠️ Remote 'origin' ainda não configurado."
fi
