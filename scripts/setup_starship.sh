#!/bin/bash
set -e

echo "[1/2] Instalando Starship Prompt..."
sudo pacman -S --noconfirm --needed starship

echo "[2/2] Concluído! O Starship já está configurado no seu Fish shell."
