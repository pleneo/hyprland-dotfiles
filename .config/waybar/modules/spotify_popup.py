#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import subprocess
import os
import sys

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

class SpotifyIslandPopup(Gtk.Window):
    def __init__(self):
        super().__init__(title="Spotify Island Popup")
        self.set_role("spotify-island-popup")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(440, 140)
        self.can_close_on_focus_out = False
        self.is_seeking = False
        self.total_duration = 0

        self.connect("destroy", on_destroy)
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

        # Habilitar fechamento por clique fora após 500ms (evita fechar ao mover mouse da barra)
        GLib.timeout_add(500, self.enable_focus_out)

        # CSS Styling Premium
        css = b"""
        window {
            background-color: rgba(18, 19, 27, 0.96);
            border-radius: 22px;
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
        .btn-ctrl {
            background: rgba(255, 255, 255, 0.08);
            color: #cdd6f4;
            border: none;
            border-radius: 20px;
            min-width: 32px;
            min-height: 32px;
            padding: 0;
            font-size: 14px;
        }
        .btn-ctrl:hover {
            background: rgba(29, 185, 84, 0.3);
            color: #1db954;
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
        right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
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

        # Nome da Música
        self.title_lbl = Gtk.Label(label="Carregando...")
        self.title_lbl.get_style_context().add_class("title-label")
        self.title_lbl.set_halign(Gtk.Align.START)
        self.title_lbl.set_ellipsize(3)
        self.title_lbl.set_max_width_chars(26)
        right_vbox.pack_start(self.title_lbl, False, False, 0)

        # Artista • Álbum
        self.artist_lbl = Gtk.Label(label="")
        self.artist_lbl.get_style_context().add_class("artist-label")
        self.artist_lbl.set_halign(Gtk.Align.START)
        self.artist_lbl.set_ellipsize(3)
        self.artist_lbl.set_max_width_chars(30)
        right_vbox.pack_start(self.artist_lbl, False, False, 0)

        # Linha do Tempo Arrastável (Gtk.Scale Interativo)
        self.timeline_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.timeline_scale.set_draw_value(False)
        self.timeline_scale.connect("button-press-event", self.on_scale_press)
        self.timeline_scale.connect("button-release-event", self.on_scale_release)
        self.timeline_scale.connect("change-value", self.on_scale_change)
        right_vbox.pack_start(self.timeline_scale, False, False, 2)

        # Barra Inferior: Horário + Botões de Controle
        bottom_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Horários
        self.time_lbl = Gtk.Label(label="0:00 / 0:00")
        self.time_lbl.get_style_context().add_class("time-label")
        bottom_hbox.pack_start(self.time_lbl, False, False, 0)

        # Controles alinhados à direita
        ctrl_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        ctrl_hbox.set_halign(Gtk.Align.END)

        btn_prev = Gtk.Button(label="󰒮")
        btn_prev.get_style_context().add_class("btn-ctrl")
        btn_prev.connect("clicked", lambda b: self.exec_player("previous"))

        self.btn_play = Gtk.Button(label="󰏤")
        self.btn_play.get_style_context().add_class("btn-play")
        self.btn_play.connect("clicked", lambda b: self.exec_player("play-pause"))

        btn_next = Gtk.Button(label="󰒭")
        btn_next.get_style_context().add_class("btn-ctrl")
        btn_next.connect("clicked", lambda b: self.exec_player("next"))

        ctrl_hbox.pack_start(btn_prev, False, False, 0)
        ctrl_hbox.pack_start(self.btn_play, False, False, 0)
        ctrl_hbox.pack_start(btn_next, False, False, 0)

        bottom_hbox.pack_end(ctrl_hbox, False, False, 0)
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
                "{{status}};;;{{artist}};;;{{title}};;;{{album}};;;{{position}};;;{{mpris:length}};;;{{duration(position)}};;;{{duration(mpris:length)}}"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1)
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split(";;;")
                if len(parts) >= 8:
                    status, artist, title, album, pos_raw, len_raw, pos_str, len_str = parts
                    self.title_lbl.set_text(title)
                    self.artist_lbl.set_text(f"{artist} • {album}" if album else artist)

                    # Play / Pause Icon
                    self.btn_play.set_label("󰏤" if status == "Playing" else "󰐊")

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
