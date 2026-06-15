import time
import re

from dotenv import load_dotenv
load_dotenv()

import requests
from database import get_connection, init_db
import json

def parse_hours(hours_string):
    if not hours_string:
        return (None, None)

    text = hours_string.lower().strip()

    if "24" in text and "hour" in text:
        return (0, 24)

    pattern = r'(\d{1,2})(?::\d{2})?\s*(a\.?\s*m\.?|p\.?\s*m\.?)'
    matches = re.findall(pattern, text)

    if len(matches) < 2:
        return (None, None)

    def convert_to_24_hour(hour, period):
        hour = int(hour)
        period = period.replace(".", "").replace(" ", "")

        if period == "am":
            if hour == 12:
                return 0
            return hour

        if period == "pm":
            if hour == 12:
                return 12
            return hour + 12

        return None

    opening_hour = convert_to_24_hour(matches[0][0], matches[0][1])
    closing_hour = convert_to_24_hour(matches[1][0], matches[1][1])

    return (opening_hour, closing_hour)

def fetch_places(place_name, lat, lon, radius=20000):
    query = f"""
    [out:json][timeout:25];
    (
      node["name"="{place_name}"](around:{radius},{lat},{lon});
      way["name"="{place_name}"](around:{radius},{lat},{lon});
    );
    out center;
    """
    
    response = requests.get(
        "https://overpass-api.de/api/interpreter",
        params={"data": query},
        headers={"User-Agent": "PitStop/1.0"}
    )
    time.sleep(1)
    
    print("status:", response.status_code)
    return response.json()["elements"]

def populate_places(place_name, lat, lon):
    print(f"Fetching {place_name}...")
    elements = fetch_places(place_name, lat, lon)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    for el in elements:
        if el["type"] == "way":
            place_lat = el["center"]["lat"]
            place_lon = el["center"]["lon"]
        else:
            place_lat = el["lat"]
            place_lon = el["lon"]
        
        name = el.get("tags", {}).get("name", place_name)
        address = el.get("tags", {}).get("addr:street", None)
        
        try:
            cursor.execute("""
            INSERT INTO washrooms (name, latitude, longitude, address, is_open24h, is_accessible, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (latitude, longitude) DO NOTHING
        """, (name, place_lat, place_lon, address, False, True, "Source: OpenStreetMap"))
            count += 1
        except Exception as e:
            conn.rollback()
            print(f"Skipped: {type(e).__name__}: {e}")
            break  # stop after first error so we can read it
    
    conn.commit()
    conn.close()
    print(f"Added {count} locations for {place_name}")




def fetch_by_amenity(amenity_type, lat, lon, radius=20000):
    query = f'[out:json][timeout:25];(node["amenity"="{amenity_type}"](around:{radius},{lat},{lon});way["amenity"="{amenity_type}"](around:{radius},{lat},{lon}););out center;'
    
    response = requests.get(
        "https://overpass-api.de/api/interpreter",
        params={"data": query},
        headers={"User-Agent": "PitStop/1.0"}
    )
    
    print("status:", response.status_code)
    return response.json()["elements"]

def populate_by_amenity(amenity_type, label, lat, lon):
    print(f"Fetching {label}...")
    elements = fetch_by_amenity(amenity_type, lat, lon)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    for el in elements:
        if el["type"] == "way":
            place_lat = el["center"]["lat"]
            place_lon = el["center"]["lon"]
        else:
            place_lat = el["lat"]
            place_lon = el["lon"]
        
        name = el.get("tags", {}).get("name", label)
        address = el.get("tags", {}).get("addr:street", None)
        
        try:
            cursor.execute("""
                INSERT INTO washrooms (name, latitude, longitude, address, is_open24h, is_accessible, comments)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (latitude, longitude) DO NOTHING
            """, (name, place_lat, place_lon, address, False, True, "Source: OpenStreetMap"))
            count += 1
        except Exception as e:
            conn.rollback()
            print(f"Skipped: {type(e).__name__}: {e}")
            break
            
    conn.commit()
    conn.close()
    print(f"Added {count} {label} locations")
def populate_toronto_washrooms():
    print("Fetching Toronto Open Data washrooms...")
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
    resource_id = "1c7d1063-2562-4de3-8cd3-4cef48419f6f"
    url = base_url + "/api/3/action/datastore_search"

    conn = get_connection()
    cursor = conn.cursor()

    limit = 100
    offset = 0
    count = 0

    while True:
        params = {"id": resource_id, "limit": limit, "offset": offset}
        response = requests.get(url, params=params)
        data = response.json()
        records = data["result"]["records"]

        if not records:
            break

        for record in records:
            name = record["location"]
            address = record["address"]
            geometry_string = record["geometry"]
            geometry = json.loads(geometry_string)
            longitude = geometry["coordinates"][0]
            latitude = geometry["coordinates"][1]

            hours = record.get("hours", "")
            opening_time,closing_time=parse_hours(hours)
            comments=f"Source: Toronto Open Data"
            if hours:
                comments=f"Source: Toronto Open Data | Hours:{hours}"
            is_open24h = True if hours and "24" in hours.lower() else False
            is_accessible = True if record.get("accessible") else False

            try:
                cursor.execute("""
                    INSERT INTO washrooms (name, latitude, longitude, address, is_open24h,opening_time,closing_time, is_accessible, comments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)
                    ON CONFLICT (latitude, longitude) DO UPDATE
                               SET comments=EXCLUDED.comments,
                               opening_time=EXCLUDED.opening_time,
                               closing_time=EXCLUDED.closing_time
                """, (name, latitude, longitude, address, is_open24h,opening_time,closing_time,is_accessible,comments))
                count += 1
            except Exception as e:
                conn.rollback()
                print(f"Skipped: {e}")

        offset += limit

    conn.commit()
    conn.close()
    print(f"Imported {count} Toronto washrooms")


if __name__ == "__main__":
    init_db()
    populate_toronto_washrooms()
    
    # TORONTO_LAT = 43.7001
    # TORONTO_LON = -79.4163
    
    # places = [
    #     "The Home Depot",
    #     "Canadian Tire",
    #     "Rona",
    #     "Loblaws",
    #     "FreshCo",
    # ]
    
    # for place in places:
    #     populate_places(place, TORONTO_LAT, TORONTO_LON)
    
    # populate_by_amenity("library", "Library", TORONTO_LAT, TORONTO_LON)
    # populate_by_amenity("community_centre", "Community Centre", TORONTO_LAT, TORONTO_LON)
    
    

    print("Done! Database populated.")