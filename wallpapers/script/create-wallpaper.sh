#!/usr/bin/env bash
# ==============================================================================
# Script de Automação de Wallpapers Animados para Hyprland / Gslapper
# Autor: Lenin / Antigravity
# Uso: ./create-wallpaper.sh "/caminho/do/video.mp4"
# ==============================================================================

set -e

# Cores para feedback no terminal
GREEN="\033[1;32m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
CYAN="\033[1;36m"
NC="\033[0m"

WALLPAPERS_DIR="$HOME/Downloads/Wallpapers"
mkdir -p "$WALLPAPERS_DIR"

# 1. Validação do argumento
if [ -z "$1" ]; then
    echo -e "${RED}Erro: Nenhum arquivo foi informado.${NC}"
    echo -e "${YELLOW}Uso:${NC} $0 <caminho-do-arquivo.mp4>"
    echo -e "Exemplo: $0 ~/Downloads/totoro-on-top-of-a-tree.1920x1080.mp4"
    exit 1
fi

INPUT_FILE=$(realpath "$1" 2>/dev/null || echo "$1")

if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Erro: O arquivo '$INPUT_FILE' não foi encontrado.${NC}"
    exit 1
fi

# 2. Verificação de dependências
for cmd in ffprobe ffmpeg; do
    if ! command -v "$cmd" &>/dev/null; then
        echo -e "${RED}Erro: A ferramenta '$cmd' não está instalada no sistema.${NC}"
        exit 1
    fi
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🎬 Processador Automático de Wallpapers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "📁 Arquivo de entrada: ${YELLOW}$INPUT_FILE${NC}"

# 3. Reconhecimento de resolução e dimensões
WIDTH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$INPUT_FILE" 2>/dev/null)
HEIGHT=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$INPUT_FILE" 2>/dev/null)
DURATION=$(ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=p=0 "$INPUT_FILE" 2>/dev/null || echo "10")

if [ -z "$WIDTH" ] || [ -z "$HEIGHT" ]; then
    echo -e "${RED}Erro: Não foi possível identificar o fluxo de vídeo do arquivo.${NC}"
    exit 1
fi

echo -e "📐 Resolução original: ${GREEN}${WIDTH}x${HEIGHT}${NC}"

# 4. Formatação e limpeza do nome do arquivo
FILENAME=$(basename "$INPUT_FILE")
EXT="${FILENAME##*.}"
RAW_NAME="${FILENAME%.*}"

# Remove marcações de resolução como .1920x1080 ou -1920x1080 do nome final
CLEAN_NAME=$(echo "$RAW_NAME" | sed -E 's/[\._-]?(1920x1080|3840x2160|2560x1440|1080p|4k|2k)$//I')
# Remove espaços ou substitui por hífen para manter o padrão
CLEAN_NAME=$(echo "$CLEAN_NAME" | tr ' ' '-')

TARGET_MP4="$WALLPAPERS_DIR/${CLEAN_NAME}.mp4"
TARGET_PNG="$WALLPAPERS_DIR/${CLEAN_NAME}.png"

echo -e "🎯 Destino do vídeo:   ${YELLOW}$TARGET_MP4${NC}"
echo -e "🖼️ Destino miniatura: ${YELLOW}$TARGET_PNG${NC}"

# 5. Compressão / Otimização Inteligente
# Obter taxa de bits (bitrate) e tamanho em bytes
BITRATE=$(ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=p=0 "$INPUT_FILE" 2>/dev/null || echo "0")
if [ -z "$BITRATE" ] || [ "$BITRATE" = "N/A" ] || [ "$BITRATE" = "0" ]; then
    BITRATE=$(ffprobe -v error -show_entries format=bit_rate -of csv=p=0 "$INPUT_FILE" 2>/dev/null || echo "0")
fi
FILE_SIZE_BYTES=$(stat -c%s "$INPUT_FILE" 2>/dev/null || echo "0")

NEED_RESCALE=false
NEED_COMPRESS=false

if [ "$WIDTH" -gt 1920 ] || [ "$HEIGHT" -gt 1080 ]; then
    NEED_RESCALE=true
fi

# Se o bitrate for superior a 3500 kbps ou o arquivo tiver mais de 15 MB, vale muito a pena comprimir
if [ "$FILE_SIZE_BYTES" -gt 15728640 ] || [ "$BITRATE" -gt 3500000 ]; then
    NEED_COMPRESS=true
fi

if [ "$NEED_RESCALE" = true ]; then
    echo -e "${YELLOW}⚙️  Vídeo superior a 1080p (${WIDTH}x${HEIGHT}). Redimensionando e comprimindo...${NC}"
    ffmpeg -y -i "$INPUT_FILE" \
        -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black" \
        -c:v libx264 -crf 22 -preset medium -an \
        "$TARGET_MP4" < /dev/null 2>/dev/null
    echo -e "${GREEN}✓ Redimensionado para 1080p com sucesso!${NC}"
elif [ "$NEED_COMPRESS" = true ]; then
    echo -e "${YELLOW}⚡ Vídeo 1080p com bitrate/tamanho elevado ($(numfmt --to=iec $FILE_SIZE_BYTES)).${NC}"
    echo -e "${YELLOW}   Otimizando para execução leve em loop (sem perda visual e removendo áudio desnecessário)...${NC}"
    ffmpeg -y -i "$INPUT_FILE" \
        -c:v libx264 -crf 22 -preset medium -an \
        "$TARGET_MP4" < /dev/null 2>/dev/null
    echo -e "${GREEN}✓ Otimização concluída com sucesso!${NC}"
else
    echo -e "${GREEN}✓ Resolução (${WIDTH}x${HEIGHT}) e tamanho já ideais e leves.${NC}"
    if [ "$INPUT_FILE" != "$TARGET_MP4" ]; then
        echo -e "📋 Copiando vídeo para a pasta Wallpapers..."
        cp -f "$INPUT_FILE" "$TARGET_MP4"
    fi
fi

# 6. Criação da miniatura (.png) para a galeria do Rofi e Pywal
echo -e "📸 Gerando miniatura em alta qualidade..."

# Escolhe o segundo 2 como frame de captura (ou metade do vídeo se for muito curto)
SEEK_TIME="2"
if (( $(echo "$DURATION < 3" | bc -l 2>/dev/null || echo 0) )); then
    SEEK_TIME="0.5"
fi

ffmpeg -y -ss "$SEEK_TIME" -i "$TARGET_MP4" -frames:v 1 -update 1 "$TARGET_PNG" < /dev/null 2>/dev/null

if [ ! -f "$TARGET_PNG" ]; then
    # Fallback no primeiro frame se falhar
    ffmpeg -y -ss 0 -i "$TARGET_MP4" -frames:v 1 -update 1 "$TARGET_PNG" < /dev/null 2>/dev/null
fi

# 7. Finalização e feedback
ORIGINAL_SIZE=$(du -h "$INPUT_FILE" 2>/dev/null | cut -f1)
FINAL_SIZE=$(du -h "$TARGET_MP4" 2>/dev/null | cut -f1)
THUMB_SIZE=$(du -h "$TARGET_PNG" 2>/dev/null | cut -f1)

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Wallpaper configurado com sucesso!${NC}"
echo -e "   • Tamanho original: $ORIGINAL_SIZE"
echo -e "   • Tamanho do vídeo: $FINAL_SIZE"
echo -e "   • Miniatura:       $THUMB_SIZE"
echo -e "   • Atalho da galeria: ${CYAN}Super + W${NC} para aplicar agora!"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
