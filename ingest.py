import os
import schedule
import time
import logging
import requests
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ── Logs ─────────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/ingest.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("airlab")

# ── Connexion Supabase ────────────────────────────────────────────────────────
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ── Villes ───────────────────────────────────────────────────────────────────
CITIES = {
    "Paris":     (48.8566,  2.3522),
    "Lyon":      (45.7640,  4.8357),
    "Marseille": (43.2965,  5.3698),
    "Bordeaux":  (44.8378, -0.5792),
    "Lille":     (50.6292,  3.0573),
}

AQICN_TOKEN = os.getenv("AQICN_TOKEN")

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — EXTRACT
# ══════════════════════════════════════════════════════════════════════════════

def extract_air(city, lat, lon):
    try:
        r = requests.get(
            f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQICN_TOKEN}",
            timeout=10
        )
        r.raise_for_status()
        d    = r.json().get("data", {})
        iaqi = d.get("iaqi", {})
        return {
            "city":         city,
            "aqi":          d.get("aqi"),
            "pm25":         iaqi.get("pm25", {}).get("v"),
            "pm10":         iaqi.get("pm10", {}).get("v"),
            "o3":           iaqi.get("o3",   {}).get("v"),
            "no2":          iaqi.get("no2",  {}).get("v"),
            "dominant_pol": d.get("dominentpol"),
        }
    except Exception as e:
        log.error(f"[EXTRACT] Air {city} : {e}")
        return None

def extract_weather(city, lat, lon):
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,"
            "wind_speed_10m,precipitation,pressure_msl,weather_code",
            timeout=10
        )
        r.raise_for_status()
        c = r.json().get("current", {})
        return {
            "city":          city,
            "temperature":   c.get("temperature_2m"),
            "humidity":      c.get("relative_humidity_2m"),
            "wind_speed":    c.get("wind_speed_10m"),
            "precipitation": c.get("precipitation"),
            "pressure":      c.get("pressure_msl"),
            "weather_code":  c.get("weather_code"),
        }
    except Exception as e:
        log.error(f"[EXTRACT] Météo {city} : {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — VALIDATE
# ══════════════════════════════════════════════════════════════════════════════

def validate_air(data):
    errors = []
    if not data.get("city"):
        errors.append("city manquante")
    aqi = data.get("aqi")
    if aqi is None:
        errors.append("aqi manquant")
    elif not (0 <= aqi <= 500):
        errors.append(f"aqi hors plage : {aqi}")
    if data.get("pm25") is not None and not (0 <= data["pm25"] <= 999):
        errors.append(f"pm25 aberrant : {data['pm25']}")
    if data.get("o3") is not None and not (0 <= data["o3"] <= 500):
        errors.append(f"o3 aberrant : {data['o3']}")
    if errors:
        log.warning(f"[VALIDATE] Air {data.get('city')} — {', '.join(errors)}")
        return False
    return True

def validate_weather(data):
    errors = []
    if not data.get("city"):
        errors.append("city manquante")
    temp = data.get("temperature")
    if temp is None:
        errors.append("temperature manquante")
    elif not (-50 <= temp <= 60):
        errors.append(f"température aberrante : {temp}°C")
    humidity = data.get("humidity")
    if humidity is not None and not (0 <= humidity <= 100):
        errors.append(f"humidité hors plage : {humidity}%")
    if errors:
        log.warning(f"[VALIDATE] Météo {data.get('city')} — {', '.join(errors)}")
        return False
    return True

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — CLEAN + NORMALISE
# ══════════════════════════════════════════════════════════════════════════════

def clean_air(data):
    return {
        "city":         data.get("city", "").strip().title(),
        "aqi":          int(data["aqi"])                        if data.get("aqi")          is not None else None,
        "pm25":         round(float(data["pm25"]), 2)           if data.get("pm25")         is not None else None,
        "pm10":         round(float(data["pm10"]), 2)           if data.get("pm10")         is not None else None,
        "o3":           round(float(data["o3"]),   2)           if data.get("o3")           is not None else None,
        "no2":          round(float(data["no2"]),  2)           if data.get("no2")          is not None else None,
        "dominant_pol": data.get("dominant_pol", "").lower()    if data.get("dominant_pol") else None,
    }

def clean_weather(data):
    return {
        "city":          data.get("city", "").strip().title(),
        "temperature":   round(float(data["temperature"]),   1) if data.get("temperature")   is not None else None,
        "humidity":      int(data["humidity"])                   if data.get("humidity")      is not None else None,
        "wind_speed":    round(float(data["wind_speed"]),    1) if data.get("wind_speed")    is not None else None,
        "precipitation": round(float(data["precipitation"]), 2) if data.get("precipitation") is not None else None,
        "pressure":      round(float(data["pressure"]),      1) if data.get("pressure")      is not None else None,
        "weather_code":  int(data["weather_code"])               if data.get("weather_code")  is not None else None,
    }

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — ENRICH
# ══════════════════════════════════════════════════════════════════════════════

def aqi_label(aqi):
    if aqi is None:  return "inconnu"
    if aqi <= 50:    return "bon"
    if aqi <= 100:   return "modéré"
    if aqi <= 150:   return "mauvais groupes sensibles"
    if aqi <= 200:   return "mauvais"
    if aqi <= 300:   return "très mauvais"
    return "dangereux"

WMO_LABELS = {
    0: "ciel dégagé", 1: "peu nuageux", 2: "partiellement nuageux",
    3: "couvert", 45: "brouillard", 48: "brouillard givrant",
    51: "bruine légère", 61: "pluie légère", 63: "pluie modérée",
    65: "pluie forte", 71: "neige légère", 73: "neige modérée",
    75: "neige forte", 80: "averses légères", 81: "averses modérées",
    82: "averses violentes", 95: "orage", 99: "orage avec grêle",
}

def enrich_air(data):
    data["aqi_label"] = aqi_label(data.get("aqi"))
    data["is_alert"]  = data.get("aqi") is not None and data["aqi"] > 100
    return data

def enrich_weather(data):
    code = data.get("weather_code")
    data["weather_label"] = WMO_LABELS.get(code, f"code {code}")
    return data

# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 5 — LOAD
# ══════════════════════════════════════════════════════════════════════════════

def load_air(data, ts):
    data["ts"] = ts
    supabase.table("air_quality").insert(data).execute()

def load_weather(data, ts):
    data["ts"] = ts
    supabase.table("weather").insert(data).execute()

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def run_pipeline():
    ts    = datetime.now(timezone.utc).isoformat()
    stats = {"ok": 0, "error": 0, "skipped": 0}

    log.info("=" * 60)
    log.info(f"Pipeline démarré — {ts}")
    log.info("=" * 60)

    for city, (lat, lon) in CITIES.items():

        # Qualité de l'air
        raw_air = extract_air(city, lat, lon)
        if raw_air is None:
            stats["error"] += 1
        elif not validate_air(raw_air):
            stats["skipped"] += 1
        else:
            result = enrich_air(clean_air(raw_air))
            load_air(result, ts)
            flag = "🚨" if result["is_alert"] else "✅"
            log.info(f"{flag} Air    {city} — AQI {result['aqi']} ({result['aqi_label']})")
            stats["ok"] += 1

        # Météo
        raw_wth = extract_weather(city, lat, lon)
        if raw_wth is None:
            stats["error"] += 1
        elif not validate_weather(raw_wth):
            stats["skipped"] += 1
        else:
            result = enrich_weather(clean_weather(raw_wth))
            load_weather(result, ts)
            log.info(f"✅ Météo  {city} — {result['temperature']}°C, {result['weather_label']}")
            stats["ok"] += 1

    log.info("-" * 60)
    log.info(f"Résultat : {stats['ok']} OK · {stats['skipped']} ignorés · {stats['error']} erreurs")
    log.info("=" * 60)

# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    log.info("AirLab France — pipeline démarré")
    log.info("Collecte automatique : chaque jour à 16h00")
    run_pipeline()
    schedule.every().day.at("16:00").do(run_pipeline)
    while True:
        schedule.run_pending()
        time.sleep(30)