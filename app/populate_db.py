import requests
from database import get_connection, init_db

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
                INSERT OR IGNORE INTO washrooms (name, latitude, longitude, address, is_open24h, is_accessible, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, place_lat, place_lon, address, 0, 1, f"Source: OpenStreetMap"))
            count += 1
        except Exception as e:
            print(f"Skipped: {e}")
    
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
                INSERT OR IGNORE INTO washrooms (name, latitude, longitude, address, is_open24h, is_accessible, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, place_lat, place_lon, address, 0, 1, f"Source: OpenStreetMap"))
            count += 1
        except Exception as e:
            print(f"Skipped: {e}")
    
    conn.commit()
    conn.close()
    print(f"Added {count} {label} locations")

if __name__ == "__main__":
    init_db()
    
    TORONTO_LAT = 43.7001
    TORONTO_LON = -79.4163
    
    places = [
        "The Home Depot",
        "Canadian Tire",
        "Rona",
        "Loblaws",
        "FreshCo",
    ]
    
    for place in places:
        populate_places(place, TORONTO_LAT, TORONTO_LON)
    
    populate_by_amenity("library", "Library", TORONTO_LAT, TORONTO_LON)
    populate_by_amenity("community_centre", "Community Centre", TORONTO_LAT, TORONTO_LON)
    
    print("Done! Database populated.")