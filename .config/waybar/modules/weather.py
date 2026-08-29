#!/usr/bin/env python3
import datetime
import json
import os
import time
import urllib.request

CACHE_FILE = "/tmp/waybar_weather_cache.json"
CACHE_TTL = 900  # 15 minutos de cache

# Mapeamento Wttr Code -> (Ícone Dia, Ícone Noite, Descrição Dia, Descrição Noite)
WEATHER_ICONS = {
    "113": ("󰖙", "󰖔", "Ensolarado", "Céu Limpo"),
    "116": ("󰖕", "󰼱", "Parcialmente Nublado", "Parcialmente Nublado"),
    "119": ("󰖐", "󰖐", "Nublado", "Nublado"),
    "122": ("󰖐", "󰖐", "Encoberto", "Encoberto"),
    "143": ("󰖑", "󰖑", "Neblina", "Neblina"),
    "176": ("󰖗", "󰖗", "Chuva Fraca", "Chuva Fraca"),
    "179": ("󰖘", "󰖘", "Neve Fraca", "Neve Fraca"),
    "182": ("󰖘", "󰖘", "Granizo Leve", "Granizo Leve"),
    "185": ("󰖘", "󰖘", "Garoa Congelante", "Garoa Congelante"),
    "200": ("󰖓", "󰖓", "Possibilidade de Trovoadas", "Possibilidade de Trovoadas"),
    "227": ("󰖘", "󰖘", "Neve e Vento", "Neve e Vento"),
    "230": ("󰖘", "󰖘", "Nevasca", "Nevasca"),
    "248": ("󰖑", "󰖑", "Nevoeiro", "Nevoeiro"),
    "260": ("󰖑", "󰖑", "Nevoeiro Congelante", "Nevoeiro Congelante"),
    "263": ("󰖗", "󰖗", "Garoa Fraca", "Garoa Fraca"),
    "266": ("󰖗", "󰖗", "Garoa Leve", "Garoa Leve"),
    "281": ("󰖗", "󰖗", "Garoa Fria", "Garoa Fria"),
    "284": ("󰖗", "󰖗", "Garoa Pesada", "Garoa Pesada"),
    "293": ("󰖗", "󰖗", "Chuva Leve", "Chuva Leve"),
    "296": ("󰖗", "󰖗", "Chuva Leve", "Chuva Leve"),
    "299": ("󰖗", "󰖗", "Chuva Moderada", "Chuva Moderada"),
    "302": ("󰖖", "󰖖", "Chuva Forte", "Chuva Forte"),
    "305": ("󰖖", "󰖖", "Pancadas de Chuva", "Pancadas de Chuva"),
    "308": ("󰖖", "󰖖", "Chuva Forte Contínua", "Chuva Forte Contínua"),
    "311": ("󰖗", "󰖗", "Chuva Gelada", "Chuva Gelada"),
    "353": ("󰖗", "󰖗", "Pancadas Leves de Chuva", "Pancadas Leves de Chuva"),
    "356": ("󰖖", "󰖖", "Pancadas Moderadas", "Pancadas Moderadas"),
    "359": ("󰖖", "󰖖", "Temporal / Chuva Forte", "Temporal / Chuva Forte"),
    "386": ("󰖓", "󰖓", "Chuva com Trovoadas", "Chuva com Trovoadas"),
    "389": ("󰖓", "󰖓", "Tempestade com Raios", "Tempestade com Raios"),
}

WMO_ICONS = {
    0: "󰖙", 1: "󰖙", 2: "󰖕", 3: "󰖐", 45: "󰖑", 48: "󰖑",
    51: "󰖗", 53: "󰖗", 55: "󰖗", 61: "󰖗", 63: "󰖗", 65: "󰖖",
    80: "󰖗", 81: "󰖖", 82: "󰖖", 95: "󰖓", 96: "󰖓", 99: "󰖓"
}

def get_weather_data():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached = json.load(f)
                if time.time() - cached.get("time", 0) < CACHE_TTL:
                    return cached.get("data")
        except Exception:
            pass

    req = urllib.request.Request("https://wttr.in/?format=j1", headers={"User-Agent": "curl/8.0"})
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data_wttr = json.loads(response.read().decode("utf-8"))
            
            # Buscar previsão estendida de 4 dias no Open-Meteo
            try:
                area = data_wttr["nearest_area"][0]
                lat = area["latitude"]
                lon = area["longitude"]
                url_om = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
                req_om = urllib.request.Request(url_om, headers={"User-Agent": "curl/8.0"})
                with urllib.request.urlopen(req_om, timeout=5) as resp_om:
                    data_wttr["open_meteo"] = json.loads(resp_om.read().decode("utf-8"))
            except Exception:
                pass

            with open(CACHE_FILE, "w") as f:
                json.dump({"data": data_wttr, "time": time.time()}, f)
            return data_wttr
    except Exception as e:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f).get("data")
            except Exception:
                pass
        return None

try:
    data = get_weather_data()
    if not data:
        print(json.dumps({"text": "󰖐 --°C", "tooltip": "Clima indisponível no momento", "class": "weather"}))
        exit(0)

    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    city = area["areaName"][0]["value"]
    region = area["region"][0]["value"]

    temp = current["temp_C"]
    feels_like = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind = current["windspeedKmph"]
    weather_code = current.get("weatherCode", "113")

    # Verificar se é dia ou noite
    is_day = True
    now_hour = datetime.datetime.now().hour
    if now_hour < 6 or now_hour >= 18:
        is_day = False

    icon_info = WEATHER_ICONS.get(weather_code, ("󰖙", "󰖔", "Tempo Firme", "Tempo Firme"))
    icon = icon_info[0] if is_day else icon_info[1]
    desc_pt = icon_info[2] if is_day else icon_info[3]

    # Chance de chuva máxima de hoje
    today_forecast = data["weather"][0]
    rain_chances = [int(h["chanceofrain"]) for h in today_forecast["hourly"]]
    max_rain_today = max(rain_chances) if rain_chances else 0

    # Texto limpo na barra: ícone + 1 espaço + temperatura
    bar_text = f"{icon} {temp}°C"

    # Construção do Tooltip
    tooltip_lines = [
        f"<span color='#ffead3'><b>{city}, {region}</b></span>",
        f"<span color='#ffcc66'><b>{desc_pt} - {temp}°C</b></span>\n",
        f"<b>Sensação Térmica:</b> {feels_like}°C",
        f"<b>Chance de Chuva:</b> {max_rain_today}%",
        f"<b>Umidade:</b> {humidity}% | <b>Vento:</b> {wind} km/h\n",
        "<span color='#99ffdd'><b>Próximos Dias:</b></span>"
    ]

    weekdays_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    # Exibir 4 dias de previsão (Hoje + 3 próximos dias)
    if "open_meteo" in data and "daily" in data["open_meteo"]:
        daily = data["open_meteo"]["daily"]
        times = daily["time"][:4]
        codes = daily["weathercode"][:4]
        t_max = daily["temperature_2m_max"][:4]
        t_min = daily["temperature_2m_min"][:4]
        rains = daily["precipitation_probability_max"][:4]

        for i in range(len(times)):
            d_obj = datetime.date.fromisoformat(times[i])
            w_name = "Hoje" if i == 0 else ("Amanhã" if i == 1 else weekdays_pt[d_obj.weekday()])
            day_icon = WMO_ICONS.get(codes[i], "󰖙")
            tooltip_lines.append(f"{w_name:<7} {day_icon}  {round(t_min[i]):>2}° ~ {round(t_max[i]):>2}°C   ☂ {rains[i]:>2}%")
    else:
        for i, day in enumerate(data["weather"][:3]):
            date_obj = datetime.date.fromisoformat(day["date"])
            weekday_name = "Hoje" if i == 0 else ("Amanhã" if i == 1 else weekdays_pt[date_obj.weekday()])
            min_t = day["mintempC"]
            max_t = day["maxtempC"]
            day_code = day["hourly"][4]["weatherCode"]
            day_icon_info = WEATHER_ICONS.get(day_code, ("󰖙", "󰖔", "Tempo Firme", "Tempo Firme"))
            day_icon = day_icon_info[0]
            day_rain = max([int(h["chanceofrain"]) for h in day["hourly"]])
            tooltip_lines.append(f"{weekday_name:<7} {day_icon}  {min_t:>2}° ~ {max_t:>2}°C   ☂ {day_rain:>2}%")

    tooltip = "<tt>" + "\n".join(tooltip_lines) + "</tt>"
    print(json.dumps({"text": bar_text, "tooltip": tooltip, "class": "weather"}))

except Exception as e:
    print(json.dumps({"text": "󰖐 --°C", "tooltip": f"Erro: {str(e)}", "class": "weather"}))
