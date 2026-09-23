import json
import requests
from datetime import datetime, timedelta

LOCATIONS = [

    # Norra Värmland
    ("Sysslebäck", 60.729, 13.006),
    ("Höljes", 60.815, 12.790),
    ("Likenäs", 60.640, 13.220),
    ("Branäs", 60.689, 13.189),
    ("Stöllet", 60.416, 13.256),
    ("Ambjörby", 60.480, 13.115),
    ("Vitsand", 60.542, 13.017),

    # Västra Värmland
    ("Torsby", 60.136, 13.006),
    ("Östmark", 60.314, 12.996),
    ("Värnäs", 60.285, 13.173),
    ("Lekvattnet", 59.802, 12.508),
    ("Bograngen", 60.337, 12.541),

    # Centrala Värmland
    ("Sunne", 59.837, 13.143),
    ("Munkfors", 59.833, 13.543),
    ("Hagfors", 60.024, 13.695),
    ("Ekshärad", 60.172, 13.497),
    ("Råda", 60.005, 13.602),
    ("Forshaga", 59.526, 13.481),
    ("Kil", 59.503, 13.314),

    # Östra Värmland
    ("Filipstad", 59.712, 14.168),
    ("Storfors", 59.531, 14.272),
    ("Kristinehamn", 59.309, 14.108),
    ("Lesjöfors", 59.985, 14.183),
    ("Nykroppa", 59.622, 14.308),

    # Södra Värmland
    ("Karlstad", 59.379, 13.503),
    ("Grums", 59.352, 13.111),
    ("Säffle", 59.132, 12.928),
    ("Arvika", 59.654, 12.591),
    ("Charlottenberg", 59.884, 12.303),
    ("Åmotfors", 59.762, 12.363),
    ("Edane", 59.627, 12.824),
    ("Vålberg", 59.391, 13.187)

]

OPENMETEO_MODELS = [
    "icon_eu",
    "dmi_seamless"
]


def fetch_json(url):
    last_error = None

    for _ in range(3):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_error = e

    raise last_error


def weathercode_from_yr(symbol):
    symbol = str(symbol).lower()

    if "clearsky" in symbol:
        return 0

    if "fair" in symbol:
        return 1

    if "partlycloudy" in symbol:
        return 2

    if "cloudy" in symbol:
        return 3

    if "fog" in symbol:
        return 45

    if "lightrain" in symbol:
        return 61

    if "rain" in symbol:
        return 63

    if "heavyrain" in symbol:
        return 65

    if "lightsleet" in symbol:
        return 68

    if "sleet" in symbol:
        return 69

    if "lightsnow" in symbol:
        return 71

    if "snow" in symbol:
        return 73

    if "heavysnow" in symbol:
        return 75

    if "showers" in symbol:
        return 80

    if "thunder" in symbol:
        return 95

    return 3


def weathercode_from_smhi(symbol):
    mapping = {
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 3,
        6: 3,
        7: 45,
        8: 61,
        9: 63,
        10: 80,
        11: 95,
        12: 71,
        13: 73,
        14: 75,
        15: 95,
        16: 95,
        17: 95,
        18: 95,
        19: 95,
        20: 95,
        21: 95,
        22: 95,
        23: 95,
        24: 95,
        25: 95,
        26: 95,
        27: 95
    }

    return mapping.get(symbol, 3)


def convert_smhi(smhi):
    hourly = {
        "time": [],
        "temperature_2m": [],
        "surface_pressure": [],
        "wind_speed_10m": [],
        "wind_gusts_10m": [],
        "wind_direction_10m": [],
        "precipitation_probability": [],
        "precipitation": [],
        "weathercode": []
    }

    for row in smhi["timeSeries"]:
        d = row["data"]

        hourly["time"].append(row["time"][:16])

        hourly["temperature_2m"].append(
            d.get("air_temperature")
        )

        hourly["surface_pressure"].append(
            d.get("air_pressure_at_mean_sea_level")
        )

        hourly["wind_speed_10m"].append(
            round(d.get("wind_speed", 0) * 3.6, 1)
        )

        hourly["wind_gusts_10m"].append(
            round(d.get("wind_speed_of_gust", 0) * 3.6, 1)
        )

        hourly["wind_direction_10m"].append(
            d.get("wind_from_direction")
        )

        hourly["precipitation_probability"].append(
            d.get("probability_of_precipitation", 0)
        )

        hourly["precipitation"].append(
            d.get(
                "precipitation_amount_mean_deterministic",
                d.get("precipitation_amount_mean", 0)
            )
        )

        hourly["weathercode"].append(
            weathercode_from_smhi(
                d.get("symbol_code", 4)
            )
        )

    return {
        "latitude": smhi.get("geometry", {}).get("coordinates", [None, None])[1],
        "longitude": smhi.get("geometry", {}).get("coordinates", [None, None])[0],
        "hourly": hourly
    }


def convert_yr(yr):
    hourly = {
        "time": [],
        "temperature_2m": [],
        "surface_pressure": [],
        "wind_speed_10m": [],
        "wind_gusts_10m": [],
        "wind_direction_10m": [],
        "precipitation_probability": [],
        "precipitation": [],
        "weathercode": []
    }

    for row in yr["properties"]["timeseries"]:
        inst = row["data"]["instant"]["details"]

        hourly["time"].append(row["time"][:16])

        hourly["temperature_2m"].append(
            inst.get("air_temperature")
        )

        hourly["surface_pressure"].append(
            inst.get("air_pressure_at_sea_level")
        )

        hourly["wind_speed_10m"].append(
            round(inst.get("wind_speed", 0) * 3.6, 1)
        )

        hourly["wind_gusts_10m"].append(
            round(inst.get("wind_speed_of_gust", 0) * 3.6, 1)
        )

        hourly["wind_direction_10m"].append(
            inst.get("wind_from_direction")
        )

        next1 = (
            row["data"].get("next_1_hours")
            or row["data"].get("next_6_hours")
            or row["data"].get("next_12_hours")
            or {}
        )

        hourly["precipitation_probability"].append(
            next1.get("details", {}).get(
                "probability_of_precipitation",
                0
            )
        )

        hourly["precipitation"].append(
            next1.get("details", {}).get(
                "precipitation_amount",
                0
            )
        )

        symbol = (
            next1.get("summary", {})
            .get("symbol_code", "cloudy")
        )

        hourly["weathercode"].append(
            weathercode_from_yr(symbol)
        )

    return {
        "latitude": yr.get("geometry", {}).get("coordinates", [None, None])[1],
        "longitude": yr.get("geometry", {}).get("coordinates", [None, None])[0],
        "hourly": hourly
    }


def fetch_openmeteo(lat, lon, model):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&models={model}"
        "&hourly="
        "temperature_2m,"
        "pressure_msl,"
        "wind_speed_10m,"
        "wind_gusts_10m,"
        "wind_direction_10m,"
        "precipitation_probability,"
        "precipitation,"
        "weathercode,"
        "cloud_cover"
        "&forecast_days=7"
    )

    data = fetch_json(url)

    if "hourly" in data:
        data["hourly"]["surface_pressure"] = \
            data["hourly"].pop("pressure_msl", [])

    return data

def fetch_yesterday(lat, lon):
    yesterday = (
        datetime.utcnow() - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={yesterday}"
        f"&end_date={yesterday}"
        "&daily="
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_sum,"
        "wind_speed_10m_mean"
        "&timezone=auto"
    )

    data = fetch_json(url)

    return {
        "date": yesterday,
        "max_temp": data["daily"]["temperature_2m_max"][0],
        "min_temp": data["daily"]["temperature_2m_min"][0],
        "rain": data["daily"]["precipitation_sum"][0],
        "wind": round(
            data["daily"]["wind_speed_10m_mean"][0] / 3.6,
            1
        )
    }
    
def fetch_weekly(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
"&daily="
"weathercode,"
"temperature_2m_max,"
"temperature_2m_min,"
"precipitation_probability_max,"
"precipitation_sum,"
"wind_speed_10m_mean,"
"wind_direction_10m_dominant,"
"wind_gusts_10m_mean,"
"surface_pressure_mean,"
"sunrise,"
"sunset"
        "&timezone=auto"
        "&forecast_days=7"
    )

    return fetch_json(url)

def save_forecast_snapshot(weather):
    print("save_forecast_snapshot körs")

    try:
        with open(
            "forecast_history.json",
            "r",
            encoding="utf-8"
        ) as f:
            history = json.load(f)

    except:
        history = {}

    snapshot_date = (
        datetime.utcnow() + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    if snapshot_date in history:
        return

    history[snapshot_date] = {}

    for place_name, place_data in weather.items():

        if place_name == "updated":
            continue

        daily = place_data["weekly"]["daily"]

        history[snapshot_date][place_name] = {
            "max_temp": daily["temperature_2m_max"][0],
            "min_temp": daily["temperature_2m_min"][0],
            "rain": daily["precipitation_sum"][0],
            "wind": round(
                daily["wind_speed_10m_mean"][0] / 3.6,
                1
            )
        }

    print("Antal orter:", len(history[snapshot_date]))

    with open(
        "forecast_history.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            ensure_ascii=False,
            separators=(",", ":")
        )

    print("forecast_history.json sparad")
weather = {
    "updated": datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
}

for name, lat, lon in LOCATIONS:
    print("Hämtar:", name)

    place = {}

    for model in OPENMETEO_MODELS:

        try:
            place[model] = fetch_openmeteo(
                lat,
                lon,
                model
            )

        except Exception as e:
            print(
                f"{model} misslyckades för {name}: {e}"
            )

            place[model] = {
                "hourly": {}
            }

    smhi_raw = fetch_json(
        f"https://smhi-proxy.mr-magoo21.workers.dev/?lat={lat}&lon={lon}"
    )

    yr_raw = fetch_json(
        f"https://yr-proxy.mr-magoo21.workers.dev/?lat={lat}&lon={lon}"
    )

    place["smhi"] = convert_smhi(smhi_raw)
    place["yr"] = convert_yr(yr_raw)

    try:
        place["weekly"] = fetch_weekly(
            lat,
            lon
        )

    except Exception as e:

        print(
            f"Weekly misslyckades för {name}: {e}"
        )

        place["weekly"] = {
            "daily": {
                "temperature_2m_max": [0],
                "temperature_2m_min": [0],
                "precipitation_sum": [0],
                "wind_speed_10m_mean": [0]
            }
        }

    try:
        place["yesterday"] = fetch_yesterday(
            lat,
            lon
        )

    except Exception as e:

        print(
            f"Yesterday misslyckades för {name}: {e}"
        )

        place["yesterday"] = {
            "date": "",
            "max_temp": 0,
            "min_temp": 0,
            "rain": 0,
            "wind": 0
        }

    weather[name] = place

with open("weather.json", "w", encoding="utf-8") as f:
    json.dump(
        weather,
        f,
        ensure_ascii=False,
        separators=(",", ":")
    )

save_forecast_snapshot(weather)

print("weather.json skapad")
print("forecast_history.json uppdaterad")
