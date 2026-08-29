#!/usr/bin/env python3
import calendar
import datetime
import json
import os
import subprocess
import sys

OFFSET_FILE = "/tmp/waybar_cal_offset.json"

def is_mouse_over_clock():
    try:
        out = subprocess.check_output(["hyprctl", "cursorpos"], text=True, timeout=0.2).strip()
        parts = [int(p.strip()) for p in out.split(",")]
        x, y = parts[0], parts[1]
        # Barra superior (y <= 65) na região central do relógio (700 <= x <= 1220)
        # ou se o cursor estiver sobre a área do popup do calendário (y <= 380 e 700 <= x <= 1220)
        if y <= 65 and 700 <= x <= 1220:
            return True
    except Exception:
        pass
    return False

def read_state():
    try:
        if os.path.exists(OFFSET_FILE):
            # Se o mouse saiu de cima do relógio, reseta automaticamente para o mês atual
            if not is_mouse_over_clock():
                write_state(0)
                return 0
            with open(OFFSET_FILE, "r") as f:
                data = json.load(f)
                return data.get("offset", 0)
    except Exception:
        pass
    return 0

def write_state(offset):
    try:
        with open(OFFSET_FILE, "w") as f:
            json.dump({"offset": offset}, f)
    except Exception:
        pass

# Tratar argumentos de scroll e clique
if len(sys.argv) > 1:
    action = sys.argv[1]
    curr_offset = 0
    try:
        if os.path.exists(OFFSET_FILE):
            with open(OFFSET_FILE, "r") as f:
                curr_offset = json.load(f).get("offset", 0)
    except Exception:
        pass

    if action == "up":
        write_state(curr_offset + 1)
    elif action == "down":
        write_state(curr_offset - 1)
    elif action == "reset":
        write_state(0)
    sys.exit(0)

def get_easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def get_br_holidays(year):
    easter = get_easter(year)
    return {
        datetime.date(year, 1, 1): "Confraternização Universal",
        easter - datetime.timedelta(days=47): "Carnaval",
        easter - datetime.timedelta(days=2): "Sexta-feira Santa",
        easter: "Páscoa",
        datetime.date(year, 4, 21): "Tiradentes",
        datetime.date(year, 5, 1): "Dia do Trabalho",
        easter + datetime.timedelta(days=60): "Corpus Christi",
        datetime.date(year, 9, 7): "Independência do Brasil",
        datetime.date(year, 10, 12): "Nossa Senhora Aparecida",
        datetime.date(year, 11, 2): "Finados",
        datetime.date(year, 11, 15): "Proclamação da República",
        datetime.date(year, 11, 20): "Consciência Negra",
        datetime.date(year, 12, 25): "Natal"
    }

today = datetime.date.today()
now = datetime.datetime.now()
offset = read_state()

# Calcular mês e ano alvo do scroll
total_months = today.year * 12 + today.month - 1 + offset
target_year = total_months // 12
target_month = (total_months % 12) + 1

month_names_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

cal = calendar.Calendar(firstweekday=6) # Domingo como primeiro dia
month_days = cal.monthdayscalendar(target_year, target_month)

title = f"{month_names_pt[target_month]} {target_year}"
header = f"<span color='#ffead3'><b>{title:^26}</b></span>"
week_header = "<span color='#ffcc66'><b>Do  Se  Te  Qu  Qu  Se  Sá</b></span>"

lines = [header, week_header]
for week in month_days:
    week_str = []
    for d in week:
        if d == 0:
            week_str.append("  ")
        elif d == today.day and target_month == today.month and target_year == today.year:
            week_str.append(f"<span color='#ff6699'><b><u>{d:2d}</u></b></span>")
        else:
            week_str.append(f"<span color='#ecc6d9'>{d:2d}</span>")
    lines.append("  ".join(week_str))

# Feriados do Brasil
all_hols = {**get_br_holidays(today.year), **get_br_holidays(today.year + 1)}
upcoming = [(d, name) for d, name in sorted(all_hols.items()) if d >= today][:5]
weekdays_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

hol_lines = ["\n<span color='#99ffdd'><b>Próximos Feriados:</b></span>"]
for d, name in upcoming:
    diff = (d - today).days
    diff_str = "Hoje!" if diff == 0 else f"em {diff}d" if diff == 1 else f"em {diff} dias"
    hol_lines.append(f"• {d.strftime('%d/%m')} ({weekdays_pt[d.weekday()]}) - {name} <small><i>({diff_str})</i></small>")

tooltip = "<tt>" + "\n".join(lines) + "\n" + "\n".join(hol_lines) + "</tt>"
months_short_pt = ["", "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
bar_text = f"󰥔 {now.strftime('%H:%M')} \n󰃭 {now.strftime('%e')} {months_short_pt[now.month]}"

print(json.dumps({"text": bar_text, "tooltip": tooltip, "class": "clock"}))
