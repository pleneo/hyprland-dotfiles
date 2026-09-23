#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import subprocess
import os
import sys
import threading
import math
import random
import cairo

# Importar helper da API do Spotify
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import spotify_api
except Exception:
    spotify_api = None

# Definir nome do programa para o Hyprland reconhecer a classe na hora
GLib.set_prgname("spotify-island-popup")
GLib.set_application_name("spotify-island-popup")

LOCK_FILE = "/tmp/spotify_popup.pid"

# Toggle: se já estiver aberto, fecha
if os.path.exists(LOCK_FILE):
    try:
        with open(LOCK_FILE, "r") as f:
            old_pid = int(f.read().strip())
        os.remove(LOCK_FILE)
        os.kill(old_pid, 9)
        sys.exit(0)
    except Exception:
        pass

# Verificar se o Spotify está rodando
try:
    check = subprocess.run(["playerctl", "--player=spotify", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1)
    if check.returncode != 0:
        sys.exit(0)
except Exception:
    sys.exit(0)

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

def on_destroy(window):
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except Exception:
            pass
    Gtk.main_quit()

def format_time(seconds):
    try:
        s = int(seconds)
        m = s // 60
        sec = s % 60
        return f"{m}:{sec:02d}"
    except Exception:
        return "0:00"

class SparkleParticle:
    def __init__(self, x, y, angle, speed, color, is_star=False):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 22
        self.max_life = 22
        self.color = color
        self.size = random.uniform(2.2, 3.8)
        self.is_star = is_star

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Leve desaceleração para efeito suave de purpurina
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1
        return self.life > 0

class SpotifyIslandPopup(Gtk.Window):
    def __init__(self):
        super().__init__(title="Spotify Island Popup")
        self.set_role("spotify-island-popup")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(500, 150)
        self.can_close_on_focus_out = False
        self.is_seeking = False
        self.is_vol_seeking = False
        self.total_duration = 0
        self.current_track_id = ""
        self.is_liked = False
        self.last_volume = 1.0
        self.shuffle_state = "Off"
        self.loop_state = "None"
        self.sparkle_particles = []
        self.sparkle_anim_id = None

        self.connect("destroy", on_destroy)
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

        # Habilitar fechamento por clique fora após 500ms
        GLib.timeout_add(500, self.enable_focus_out)

        # CSS Styling Premium
        css = b"""
        window {
            background-color: rgba(18, 19, 27, 0.96);
            border-radius: 20px;
            border: 2px solid rgba(29, 185, 84, 0.6);
        }
        .main-container {
            padding: 14px 18px;
        }
        .cover-art {
            border-radius: 16px;
        }
        .header-title {
            font-family: 'JetBrainsMono Nerd Font', sans-serif;
            font-size: 12px;
            font-weight: 800;
            color: #1db954;
            letter-spacing: 0.5px;
        }
        .title-label {
            font-family: 'JetBrainsMono Nerd Font', 'Fira Sans', sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: #f5f5f7;
        }
        .artist-label {
            font-family: 'JetBrainsMono Nerd Font', sans-serif;
            font-size: 11px;
            color: #9399b2;
        }
        .time-label {
            font-family: 'JetBrainsMono Nerd Font', monospace;
            font-size: 10px;
            color: #6c7086;
        }
        .btn-close {
            background: transparent;
            color: #6c7086;
            border: none;
            font-size: 12px;
            padding: 0 4px;
        }
        .btn-close:hover {
            color: #f38ba8;
        }
        .btn-like {
            background: transparent;
            border: none;
            font-size: 16px;
            padding: 0 4px;
            color: #585b70;
            transition: color 0.15s ease;
        }
        .btn-like:hover {
            color: #a6adc8;
        }
        .btn-like.liked {
            color: #1db954;
        }
        .btn-like.liked:hover {
            color: #1ed760;
        }
        .btn-ctrl {
            background: rgba(255, 255, 255, 0.08);
            color: #cdd6f4;
            border: none;
            border-radius: 20px;
            min-width: 30px;
            min-height: 30px;
            padding: 0;
            font-size: 13px;
        }
        .btn-ctrl:hover {
            background: rgba(29, 185, 84, 0.3);
            color: #1db954;
        }
        .btn-ctrl.dimmed {
            color: #6c7086;
        }
        .btn-ctrl.dimmed:hover {
            color: #cdd6f4;
        }
        .btn-ctrl.active {
            color: #1db954;
            background: rgba(29, 185, 84, 0.22);
        }
        .btn-ctrl.active:hover {
            color: #1ed760;
            background: rgba(29, 185, 84, 0.35);
        }
        .btn-play {
            background: #1db954;
            color: #0b0c10;
            border: none;
            border-radius: 20px;
            min-width: 36px;
            min-height: 36px;
            padding: 0;
            font-size: 16px;
            font-weight: 900;
        }
        .btn-play:hover {
            background: #1ed760;
        }
        .vol-btn {
            background: transparent;
            border: none;
            color: #9399b2;
            font-size: 13px;
            padding: 0 2px;
        }
        .vol-btn:hover {
            color: #1db954;
        }
        scale {
            padding: 0;
            margin: 2px 0;
            outline: none;
        }
        scale trough {
            background-color: rgba(255, 255, 255, 0.12);
            border: none;
            box-shadow: none;
            border-radius: 3px;
            min-height: 4px;
        }
        scale highlight {
            background-color: #1db954;
            border: none;
            box-shadow: none;
            border-radius: 3px;
            min-height: 4px;
        }
        scale slider {
            background-color: #1db954;
            background-image: none;
            border: none;
            box-shadow: none;
            border-radius: 50%;
            min-height: 8px;
            min-width: 8px;
            margin: -2px 0;
        }
        scale slider:hover {
            background-color: #1ed760;
            min-height: 10px;
            min-width: 10px;
            margin: -3px 0;
        }
        .vol-scale {
            min-width: 65px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Layout Principal Horizontal
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        main_hbox.get_style_context().add_class("main-container")
        self.add(main_hbox)

        # Capa do Álbum à Esquerda
        self.cover_image = Gtk.Image()
        self.cover_image.get_style_context().add_class("cover-art")
        main_hbox.pack_start(self.cover_image, False, False, 0)

        # Coluna de Informações e Controles à Direita
        right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        main_hbox.pack_start(right_vbox, True, True, 0)

        # Topo: "󰓇  Spotify" + Botão Fechar ✕
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_lbl = Gtk.Label(label="󰓇  Spotify")
        header_lbl.get_style_context().add_class("header-title")
        header_lbl.set_halign(Gtk.Align.START)
        top_bar.pack_start(header_lbl, False, False, 0)

        btn_close = Gtk.Button(label="✕")
        btn_close.get_style_context().add_class("btn-close")
        btn_close.set_halign(Gtk.Align.END)
        btn_close.connect("clicked", lambda b: self.destroy())
        top_bar.pack_end(btn_close, False, False, 0)

        right_vbox.pack_start(top_bar, False, False, 0)

        # Linha de Título + Botão de Like
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.title_lbl = Gtk.Label(label="Carregando...")
        self.title_lbl.get_style_context().add_class("title-label")
        self.title_lbl.set_halign(Gtk.Align.START)
        self.title_lbl.set_ellipsize(3)
        self.title_lbl.set_max_width_chars(24)
        title_box.pack_start(self.title_lbl, True, True, 0)

        # Botão de Like (Coração)
        self.btn_like = Gtk.Button(label="󰋑")
        self.btn_like.get_style_context().add_class("btn-like")
        self.btn_like.set_tooltip_text("Curtir Música")
        self.btn_like.connect("clicked", self.on_like_clicked)
        self.btn_like.connect("draw", self.on_btn_like_draw)
        title_box.pack_end(self.btn_like, False, False, 0)

        right_vbox.pack_start(title_box, False, False, 0)

        # Artista • Álbum
        self.artist_lbl = Gtk.Label(label="")
        self.artist_lbl.get_style_context().add_class("artist-label")
        self.artist_lbl.set_halign(Gtk.Align.START)
        self.artist_lbl.set_ellipsize(3)
        self.artist_lbl.set_max_width_chars(32)
        right_vbox.pack_start(self.artist_lbl, False, False, 0)

        # Linha do Tempo Arrastável (Gtk.Scale Interativo)
        self.timeline_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.timeline_scale.set_draw_value(False)
        self.timeline_scale.connect("button-press-event", self.on_scale_press)
        self.timeline_scale.connect("button-release-event", self.on_scale_release)
        self.timeline_scale.connect("change-value", self.on_scale_change)
        right_vbox.pack_start(self.timeline_scale, False, False, 2)

        # Barra Inferior: Horário + Controles + Volume
        bottom_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Horários
        self.time_lbl = Gtk.Label(label="0:00 / 0:00")
        self.time_lbl.get_style_context().add_class("time-label")
        bottom_hbox.pack_start(self.time_lbl, False, False, 0)

        # Controles Centrais: Shuffle + Prev + Play/Pause + Next + Repeat
        ctrl_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ctrl_hbox.set_halign(Gtk.Align.CENTER)

        self.btn_shuffle = Gtk.Button(label="󰒝")
        self.btn_shuffle.get_style_context().add_class("btn-ctrl")
        self.btn_shuffle.get_style_context().add_class("dimmed")
        self.btn_shuffle.set_tooltip_text("Aleatório: Desativado")
        self.btn_shuffle.connect("clicked", self.on_shuffle_clicked)

        btn_prev = Gtk.Button(label="󰒮")
        btn_prev.get_style_context().add_class("btn-ctrl")
        btn_prev.connect("clicked", lambda b: self.exec_player("previous"))

        self.btn_play = Gtk.Button(label="󰏤")
        self.btn_play.get_style_context().add_class("btn-play")
        self.btn_play.connect("clicked", lambda b: self.exec_player("play-pause"))

        btn_next = Gtk.Button(label="󰒭")
        btn_next.get_style_context().add_class("btn-ctrl")
        btn_next.connect("clicked", lambda b: self.exec_player("next"))

        self.btn_repeat = Gtk.Button(label="󰑖")
        self.btn_repeat.get_style_context().add_class("btn-ctrl")
        self.btn_repeat.get_style_context().add_class("dimmed")
        self.btn_repeat.set_tooltip_text("Repetir: Desativado")
        self.btn_repeat.connect("clicked", self.on_repeat_clicked)

        ctrl_hbox.pack_start(self.btn_shuffle, False, False, 0)
        ctrl_hbox.pack_start(btn_prev, False, False, 0)
        ctrl_hbox.pack_start(self.btn_play, False, False, 0)
        ctrl_hbox.pack_start(btn_next, False, False, 0)
        ctrl_hbox.pack_start(self.btn_repeat, False, False, 0)
        bottom_hbox.pack_start(ctrl_hbox, True, True, 0)

        # Seção de Volume à Direita (Exclusivo do Spotify)
        vol_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        vol_hbox.set_halign(Gtk.Align.END)

        self.btn_vol = Gtk.Button(label="󰕾")
        self.btn_vol.get_style_context().add_class("vol-btn")
        self.btn_vol.connect("clicked", self.toggle_mute)
        vol_hbox.pack_start(self.btn_vol, False, False, 0)

        self.vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.vol_scale.get_style_context().add_class("vol-scale")
        self.vol_scale.set_draw_value(False)
        self.vol_scale.connect("button-press-event", lambda w, e: setattr(self, 'is_vol_seeking', True))
        self.vol_scale.connect("button-release-event", self.on_vol_release)
        self.vol_scale.connect("change-value", self.on_vol_change)
        vol_hbox.pack_start(self.vol_scale, False, False, 0)

        bottom_hbox.pack_end(vol_hbox, False, False, 0)
        right_vbox.pack_start(bottom_hbox, False, False, 0)

        self.update_data()
        GLib.timeout_add(1000, self.update_data)

    def enable_focus_out(self):
        self.can_close_on_focus_out = True
        return False

    def on_focus_out(self, widget, event):
        if self.can_close_on_focus_out:
            try:
                res = subprocess.run(["pgrep", "-x", "slurp"], stdout=subprocess.PIPE)
                if res.returncode == 0:
                    return
            except Exception:
                pass
            self.destroy()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def on_scale_press(self, widget, event):
        self.is_seeking = True

    def on_scale_release(self, widget, event):
        val = self.timeline_scale.get_value()
        subprocess.run(["playerctl", "--player=spotify", "position", str(val)])
        self.is_seeking = False
        GLib.timeout_add(100, self.update_data)

    def on_scale_change(self, widget, scroll, value):
        if self.is_seeking:
            cur_str = format_time(value)
            tot_str = format_time(self.total_duration)
            self.time_lbl.set_text(f"{cur_str} / {tot_str}")
        return False

    def on_vol_change(self, widget, scroll, value):
        val_float = min(1.0, max(0.0, float(value) / 100.0))
        subprocess.run(["playerctl", "--player=spotify", "volume", f"{val_float:.2f}"])
        self.update_vol_icon(val_float)
        return False

    def on_vol_release(self, widget, event):
        self.is_vol_seeking = False
        val_float = min(1.0, max(0.0, self.vol_scale.get_value() / 100.0))
        subprocess.run(["playerctl", "--player=spotify", "volume", f"{val_float:.2f}"])
        self.update_vol_icon(val_float)

    def update_vol_icon(self, vol):
        if vol <= 0.01:
            self.btn_vol.set_label("󰝟")
        elif vol < 0.33:
            self.btn_vol.set_label("󰕿")
        elif vol < 0.66:
            self.btn_vol.set_label("󰖀")
        else:
            self.btn_vol.set_label("󰕾")

    def toggle_mute(self, btn):
        try:
            cur_vol = float(subprocess.check_output(["playerctl", "--player=spotify", "volume"]).decode().strip())
            if cur_vol > 0.01:
                self.last_volume = cur_vol
                subprocess.run(["playerctl", "--player=spotify", "volume", "0"])
                self.vol_scale.set_value(0)
                self.update_vol_icon(0)
            else:
                target = self.last_volume if self.last_volume > 0.05 else 0.8
                subprocess.run(["playerctl", "--player=spotify", "volume", str(target)])
                self.vol_scale.set_value(target * 100.0)
                self.update_vol_icon(target)
        except Exception:
            pass

    def burst_sparkles(self):
        alloc = self.btn_like.get_allocation()
        cx = alloc.width / 2.0
        cy = alloc.height / 2.0
        colors = [
            (0.114, 0.725, 0.329),  # #1db954 (Verde Spotify)
            (0.118, 0.843, 0.376),  # #1ed760 (Verde Brilhante)
            (0.651, 0.957, 0.773),  # #a6f4c5 (Menta Claro / Brilho)
            (0.505, 0.780, 0.517),  # #81c784 (Verde Pastel)
            (1.000, 1.000, 0.800),  # Brilho dourado claro
        ]
        self.sparkle_particles.clear()
        num_particles = 14
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi + random.uniform(-0.18, 0.18)
            speed = random.uniform(1.8, 3.2)
            color = random.choice(colors)
            is_star = (i % 2 == 0)
            self.sparkle_particles.append(SparkleParticle(cx, cy, angle, speed, color, is_star))

        if self.sparkle_anim_id is None:
            self.sparkle_anim_id = GLib.timeout_add(16, self.animate_sparkles)
        self.btn_like.queue_draw()

    def animate_sparkles(self):
        alive = []
        for p in self.sparkle_particles:
            if p.update():
                alive.append(p)
        self.sparkle_particles = alive
        self.btn_like.queue_draw()
        if not self.sparkle_particles:
            self.sparkle_anim_id = None
            return False
        return True

    def on_btn_like_draw(self, btn, cr):
        if not self.sparkle_particles:
            return False
        cr.save()
        cr.reset_clip()
        for p in self.sparkle_particles:
            progress = p.life / p.max_life
            alpha = max(0.0, min(1.0, progress ** 1.3))
            r, g, b = p.color
            cr.set_source_rgba(r, g, b, alpha)
            size = p.size * (0.5 + 0.5 * progress)

            if p.is_star:
                cr.move_to(p.x, p.y - size * 1.6)
                cr.line_to(p.x + size * 0.4, p.y)
                cr.line_to(p.x, p.y + size * 1.6)
                cr.line_to(p.x - size * 0.4, p.y)
                cr.close_path()
                cr.fill()
            else:
                cr.arc(p.x, p.y, size, 0, 2 * math.pi)
                cr.fill()
        cr.restore()
        return False

    def on_like_clicked(self, btn):
        if not spotify_api or not self.current_track_id:
            return
        # Troca otimista imediata na UI
        self.is_liked = not self.is_liked
        self.update_like_ui(self.is_liked)
        if self.is_liked:
            self.burst_sparkles()

        # Executa na API em segundo plano
        def run_like():
            success = spotify_api.set_track_liked(self.current_track_id, self.is_liked)
            if not success:
                # Reverte se falhou
                self.is_liked = not self.is_liked
                GLib.idle_add(self.update_like_ui, self.is_liked)

        threading.Thread(target=run_like, daemon=True).start()

    def update_like_ui(self, liked):
        ctx = self.btn_like.get_style_context()
        self.btn_like.set_label("󰋑")
        if liked:
            self.btn_like.set_tooltip_text("Remover dos Favoritos")
            if not ctx.has_class("liked"):
                ctx.add_class("liked")
        else:
            self.btn_like.set_tooltip_text("Curtir Música")
            if ctx.has_class("liked"):
                ctx.remove_class("liked")

    def check_track_liked_async(self, track_id):
        if not spotify_api or not track_id:
            return
        def fetch():
            liked = spotify_api.is_track_liked(track_id)
            if track_id == self.current_track_id:
                self.is_liked = liked
                GLib.idle_add(self.update_like_ui, liked)
        threading.Thread(target=fetch, daemon=True).start()

    def update_shuffle_ui(self, state):
        ctx = self.btn_shuffle.get_style_context()
        if str(state).strip().lower() == "on":
            if not ctx.has_class("active"):
                ctx.add_class("active")
            if ctx.has_class("dimmed"):
                ctx.remove_class("dimmed")
            self.btn_shuffle.set_tooltip_text("Aleatório: Ativado (Clique para desativar)")
        else:
            if ctx.has_class("active"):
                ctx.remove_class("active")
            if not ctx.has_class("dimmed"):
                ctx.add_class("dimmed")
            self.btn_shuffle.set_tooltip_text("Aleatório: Desativado (Clique para ativar)")

    def update_repeat_ui(self, state):
        ctx = self.btn_repeat.get_style_context()
        st = str(state).strip().lower()
        if st == "track":
            self.btn_repeat.set_label("󰑘")
            if not ctx.has_class("active"):
                ctx.add_class("active")
            if ctx.has_class("dimmed"):
                ctx.remove_class("dimmed")
            self.btn_repeat.set_tooltip_text("Repetir: Faixa atual (1) (Clique para desativar)")
        elif st == "playlist":
            self.btn_repeat.set_label("󰑖")
            if not ctx.has_class("active"):
                ctx.add_class("active")
            if ctx.has_class("dimmed"):
                ctx.remove_class("dimmed")
            self.btn_repeat.set_tooltip_text("Repetir: Playlist inteira (Clique para repetir 1)")
        else:  # "none"
            self.btn_repeat.set_label("󰑖")
            if ctx.has_class("active"):
                ctx.remove_class("active")
            if not ctx.has_class("dimmed"):
                ctx.add_class("dimmed")
            self.btn_repeat.set_tooltip_text("Repetir: Desativado (Clique para repetir playlist)")

    def on_shuffle_clicked(self, btn):
        new_state = "Off" if self.shuffle_state.lower() == "on" else "On"
        self.shuffle_state = new_state
        self.update_shuffle_ui(new_state)
        subprocess.Popen(["playerctl", "--player=spotify", "shuffle", new_state])
        GLib.timeout_add(250, self.update_data)

    def on_repeat_clicked(self, btn):
        cur = self.loop_state.lower()
        # Ciclo: None -> Playlist -> Track (1) -> None
        if cur == "none":
            next_loop = "Playlist"
        elif cur == "playlist":
            next_loop = "Track"
        else:  # track
            next_loop = "None"

        self.loop_state = next_loop
        self.update_repeat_ui(next_loop)
        subprocess.Popen(["playerctl", "--player=spotify", "loop", next_loop])
        GLib.timeout_add(250, self.update_data)

    def exec_player(self, action):
        subprocess.run(["playerctl", "--player=spotify", action])
        GLib.timeout_add(100, self.update_data)

    def update_data(self):
        try:
            cmd = [
                "playerctl",
                "--player=spotify",
                "metadata",
                "--format",
                "{{status}};;;{{artist}};;;{{title}};;;{{album}};;;{{position}};;;{{mpris:length}};;;{{duration(position)}};;;{{duration(mpris:length)}};;;{{mpris:trackid}};;;{{volume}}"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1)
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split(";;;")
                if len(parts) >= 8:
                    status, artist, title, album, pos_raw, len_raw, pos_str, len_str = parts[:8]
                    track_id = parts[8] if len(parts) > 8 else ""
                    vol_raw = parts[9] if len(parts) > 9 else "1.0"

                    self.title_lbl.set_text(title)
                    self.artist_lbl.set_text(f"{artist} • {album}" if album else artist)

                    # Play / Pause Icon
                    self.btn_play.set_label("󰏤" if status == "Playing" else "󰐊")

                    # Verificar Like quando troca de música
                    if track_id and track_id != self.current_track_id:
                        self.current_track_id = track_id
                        self.check_track_liked_async(track_id)

                    # Shuffle e Repeat
                    try:
                        s_out = subprocess.check_output(["playerctl", "--player=spotify", "shuffle"], stderr=subprocess.DEVNULL, timeout=0.3).decode().strip()
                        if s_out:
                            self.shuffle_state = s_out
                            self.update_shuffle_ui(s_out)
                    except Exception:
                        pass

                    try:
                        l_out = subprocess.check_output(["playerctl", "--player=spotify", "loop"], stderr=subprocess.DEVNULL, timeout=0.3).decode().strip()
                        if l_out:
                            self.loop_state = l_out
                            self.update_repeat_ui(l_out)
                    except Exception:
                        pass

                    # Volume do Spotify
                    if not self.is_vol_seeking:
                        try:
                            vol_f = float(vol_raw)
                            self.vol_scale.set_value(vol_f * 100.0)
                            self.update_vol_icon(vol_f)
                        except Exception:
                            pass

                    # Progresso da Barra Interativa
                    try:
                        pos_s = float(pos_raw) / 1000000.0
                        len_s = float(len_raw) / 1000000.0
                        self.total_duration = len_s

                        if not self.is_seeking:
                            self.timeline_scale.set_range(0, max(1.0, len_s))
                            self.timeline_scale.set_value(min(len_s, max(0.0, pos_s)))
                            self.time_lbl.set_text(f"{pos_str or '0:00'} / {len_str or '0:00'}")
                    except Exception:
                        pass
            else:
                self.destroy()
                return False

            # Capa do Álbum
            cover_path = "/tmp/spotify_cover_large.png"
            if os.path.exists(cover_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(cover_path, 100, 100, True)
                self.cover_image.set_from_pixbuf(pixbuf)
            else:
                self.cover_image.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)

        except Exception:
            pass
        return True

if __name__ == "__main__":
    win = SpotifyIslandPopup()
    win.show_all()
    Gtk.main()

