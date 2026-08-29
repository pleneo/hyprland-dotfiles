#!/usr/bin/fish
set WALL_DIR (dirname (realpath (status filename)))

# Ler o último wallpaper salvo ou usar o primeiro disponível como fallback
set SELECAO ""
if test -f ~/.cache/current_wallpaper
    set SELECAO (cat ~/.cache/current_wallpaper | string replace -r '\.mp4$' '')
end

if test -z "$SELECAO" -o ! -f "$WALL_DIR/$SELECAO.mp4"
    set first_video (ls $WALL_DIR/*.mp4 2>/dev/null | head -n 1)
    if test -n "$first_video"
        set SELECAO (basename -s .mp4 $first_video | string replace -r '\.mp4$' '')
        mkdir -p ~/.cache
        echo "$SELECAO" > ~/.cache/current_wallpaper
    end
end

test -z "$SELECAO" && exit 0

set NOME_LIMPO (string replace -r '\.mp4$' '' -- $SELECAO)

# 1. Restaurar cores do Pywal
if test -f "$WALL_DIR/$NOME_LIMPO.png"
    wal -i "$WALL_DIR/$NOME_LIMPO.png" -n
end

# 2. Iniciar wallpaper animado com gslapper otimizado via dispatcher Lua do Hyprland
killall swaybg 2>/dev/null
pkill gslapper 2>/dev/null
sleep 0.2
hyprctl dispatch "hl.dsp.exec_cmd(\"gslapper -o \\\"no-audio loop\\\" \\\"*\\\" \\\"$WALL_DIR/$NOME_LIMPO.mp4\\\"\")"
