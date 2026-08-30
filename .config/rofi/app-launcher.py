#!/usr/bin/env python3
import os
import glob
import subprocess
import urllib.parse
import sys
import json

USAGE_FILE = os.path.expanduser("~/.cache/rofi-app-usage.json")
WOFI_HISTORY = os.path.expanduser("~/.cache/wofi-drun")

def load_app_usage():
    usage = {}
    # Carregar do JSON se existir
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                usage = json.load(f)
                return usage
        except Exception:
            pass

    # Se ainda não existe, migrar do histórico antigo do wofi
    if os.path.exists(WOFI_HISTORY):
        try:
            with open(WOFI_HISTORY, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(" ", 1)
                    if len(parts) == 2:
                        try:
                            usage[parts[1].strip()] = int(parts[0])
                        except Exception:
                            pass
        except Exception:
            pass
    return usage

def save_app_usage(usage):
    try:
        os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, indent=2)
    except Exception:
        pass

def get_installed_apps():
    apps = {}
    seen_names = set()
    dirs = [
        "/usr/share/applications",
        "/var/lib/flatpak/exports/share/applications",
        os.path.expanduser("~/.local/share/applications")
    ]

    for d in dirs:
        for f in glob.glob(os.path.join(d, "*.desktop")):
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                    name, icon, exec_cmd, nodisplay = "", "", "", False
                    for line in fp:
                        if line.startswith("Name=") and not name:
                            name = line[5:].strip()
                        elif line.startswith("Icon=") and not icon:
                            icon = line[5:].strip()
                        elif line.startswith("Exec=") and not exec_cmd:
                            exec_cmd = line[5:].strip()
                        elif line.startswith("NoDisplay=true"):
                            nodisplay = True
                    
                    if name and not nodisplay:
                        if name not in seen_names:
                            seen_names.add(name)
                            apps[name] = {
                                "icon": icon or "application-x-executable",
                                "file": f,
                                "exec": exec_cmd
                            }
            except Exception:
                pass
    return apps

def main():
    apps = get_installed_apps()
    usage = load_app_usage()

    # Função para obter a contagem de uso de cada aplicativo
    def get_count(app_name):
        f = apps[app_name]["file"]
        return usage.get(f, 0) + usage.get(app_name, 0)

    # Ordenar por frequência de uso (mais acessados primeiro), depois alfabeticamente
    sorted_names = sorted(apps.keys(), key=lambda s: (-get_count(s), s.lower()))

    # Formatar entradas para o Rofi com ícones
    rofi_input_lines = []
    for name in sorted_names:
        icon = apps[name]["icon"]
        rofi_input_lines.append(f"{name}\0icon\x1f{icon}")

    rofi_input = "\n".join(rofi_input_lines)
    theme_path = os.path.expanduser("~/.config/rofi/launcher.rasi")

    cmd = [
        "rofi",
        "-dmenu",
        "-i",
        "-show-icons",
        "-p", " ",
        "-theme", theme_path
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = proc.communicate(input=rofi_input)

    selection = out.strip()
    if not selection:
        sys.exit(0)

    # 1. Se for um aplicativo instalado, registra o uso e abre o aplicativo
    if selection in apps:
        desktop_file = apps[selection]["file"]
        desktop_name = os.path.basename(desktop_file).replace(".desktop", "")

        # Incrementar contagem de uso
        usage[desktop_file] = usage.get(desktop_file, 0) + 1
        save_app_usage(usage)

        try:
            subprocess.Popen(["gtk-launch", desktop_name])
        except Exception:
            cmd_exec = apps[selection]["exec"].split("%")[0].strip()
            subprocess.Popen(cmd_exec, shell=True)
        sys.exit(0)

    # 2. Se não for um aplicativo instalado, pesquisa no Google no navegador padrão (Floorp)
    encoded_query = urllib.parse.quote_plus(selection)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    
    subprocess.Popen(["xdg-open", search_url])

if __name__ == "__main__":
    main()
