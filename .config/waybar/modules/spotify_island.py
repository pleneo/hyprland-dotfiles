#!/usr/bin/env python3
import json
import os
import subprocess
import urllib.request
import hashlib
from PIL import Image, ImageDraw

COVER_MINI = "/tmp/spotify_cover.png"
COVER_LARGE = "/tmp/spotify_cover_large.png"
CACHE_DIR = "/tmp/spotify_art_cache"

os.makedirs(CACHE_DIR, exist_ok=True)

def round_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def process_cover(art_url):
    if not art_url:
        return
    try:
        url_hash = hashlib.md5(art_url.encode()).hexdigest()
        local_src = os.path.join(CACHE_DIR, f"{url_hash}.raw")

        if not os.path.exists(local_src):
            if art_url.startswith("file://"):
                file_path = art_url[7:]
                with open(file_path, "rb") as f_in, open(local_src, "wb") as f_out:
                    f_out.write(f_in.read())
            elif art_url.startswith("http://") or art_url.startswith("https://"):
                req = urllib.request.Request(art_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    with open(local_src, "wb") as f_out:
                        f_out.write(resp.read())

        if os.path.exists(local_src):
            with Image.open(local_src) as img:
                img = img.convert("RGBA")
                # Mini cover (22x22, radius 6)
                mini = img.resize((22, 22), Image.Resampling.LANCZOS)
                mini = round_corners(mini, 6)
                mini.save(COVER_MINI, "PNG")

                # Large cover (110x110, radius 16)
                large = img.resize((110, 110), Image.Resampling.LANCZOS)
                large = round_corners(large, 16)
                large.save(COVER_LARGE, "PNG")
    except Exception:
        pass

def get_spotify_info():
    try:
        # Verificar se o spotify está rodando
        check = subprocess.run(["playerctl", "--player=spotify", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1)
        if check.returncode != 0:
            return None

        cmd = [
            "playerctl",
            "--player=spotify",
            "metadata",
            "--format",
            "{{status}};;;{{artist}};;;{{title}};;;{{album}};;;{{mpris:artUrl}};;;{{duration(position)}};;;{{duration(mpris:length)}}"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
        if res.returncode != 0 or not res.stdout.strip():
            return None

        parts = res.stdout.strip().split(";;;")
        if len(parts) < 7:
            return None

        status, artist, title, album, art_url, pos, length = parts
        if not title.strip():
            return None

        return {
            "status": status.strip(),
            "artist": artist.strip() or "Desconhecido",
            "title": title.strip() or "Música",
            "album": album.strip() or "",
            "art_url": art_url.strip(),
            "pos": pos.strip() or "0:00",
            "length": length.strip() or "0:00",
        }
    except Exception:
        return None

info = get_spotify_info()

if not info or info["status"] == "Stopped":
    # Spotify não está aberto ou está parado -> Limpar e ocultar completamente
    try:
        if os.path.exists(COVER_MINI):
            os.remove(COVER_MINI)
    except Exception:
        pass
    print(json.dumps({"text": "", "alt": "stopped", "class": "empty", "tooltip": ""}))
else:
    process_cover(info["art_url"])
    icon = "󰓇"
    
    # Formatação do texto da música (limite de 30 chars)
    full_text = f"{info['artist']} - {info['title']}"
    if len(full_text) > 30:
        display_text = full_text[:27] + "..."
    else:
        display_text = full_text

    tooltip_lines = [
        f"<span color='#1db954'><b>󰓇  Spotify</b></span>",
        f"<b>Música:</b> {info['title']}",
        f"<b>Artista:</b> {info['artist']}",
    ]
    if info['album']:
        tooltip_lines.append(f"<b>Álbum:</b> {info['album']}")
    tooltip_lines.append(f"<b>Tempo:</b> {info['pos']} / {info['length']} ({info['status']})")

    tooltip = "\n".join(tooltip_lines)
    css_class = "playing" if info["status"] == "Playing" else "paused"
    
    print(json.dumps({
        "text": f"{icon} {display_text}",
        "tooltip": tooltip,
        "class": css_class,
        "alt": css_class
    }))
