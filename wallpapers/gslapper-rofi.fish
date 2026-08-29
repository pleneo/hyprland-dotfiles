#!/usr/bin/fish
trap '' SIGTERM

set WALL_DIR (dirname (realpath (status filename)))
set THEME_FILE "$WALL_DIR/wallpaper-gallery.rasi"

# Abrir Rofi com os 3 wallpapers lado a lado e miniaturas
set SELECAO (
    for video in $WALL_DIR/*.mp4
        set raw (basename -s .mp4 $video)
        set thumb "$WALL_DIR/$raw.png"
        set clean (string replace -a '-' ' ' -- $raw | string replace -i ' moewalls com' '' | string replace -i ' moewalls' '' | string trim)
        printf "%s\0icon\x1f%s\n" "$clean" "$thumb"
    end | rofi -dmenu -i -show-icons -p "󰐊 Wallpaper" -theme "$THEME_FILE"
)

test -z "$SELECAO" && exit 0

# Recuperar o nome original do arquivo
set NOME_LIMPO ""
for video in $WALL_DIR/*.mp4
    set raw (basename -s .mp4 $video)
    set clean (string replace -a '-' ' ' -- $raw | string replace -i ' moewalls com' '' | string replace -i ' moewalls' '' | string trim)
    if test "$clean" = "$SELECAO"
        set NOME_LIMPO "$raw"
        break
    end
end

test -z "$NOME_LIMPO" && set NOME_LIMPO (string replace -r '\.mp4$' '' -- $SELECAO)

# Salvar o wallpaper atual para iniciar no boot
mkdir -p ~/.cache
echo "$NOME_LIMPO" > ~/.cache/current_wallpaper

# 1. Pywal (Gera cores)
if test -f "$WALL_DIR/$NOME_LIMPO.png"
    wal -i "$WALL_DIR/$NOME_LIMPO.png" -n
end

# 2. Gslapper (Wallpaper animado otimizado via dispatcher Lua do Hyprland)
killall swaybg 2>/dev/null
pkill gslapper 2>/dev/null
sleep 0.2
hyprctl dispatch "hl.dsp.exec_cmd(\"gslapper -o \\\"no-audio loop\\\" \\\"*\\\" \\\"$WALL_DIR/$NOME_LIMPO.mp4\\\"\")"

# 3. Waybar hot reload (Sinal USR2 recarrega o CSS sem fechar a barra)
pkill -USR2 waybar

# 4. Hyprland hot reload
hyprctl reload config-only

exit 0
