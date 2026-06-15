import os
import psycopg

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg.connect(DATABASE_URL)
    return conn

def init_db():
    conn=get_connection()
    cursor=conn.cursor()
  
    cursor.execute("""
                   
        CREATE TABLE IF NOT EXISTS washrooms         
        (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT,
            is_open24h BOOLEAN DEFAULT FALSE,
            opening_time INTEGER,
            closing_time INTEGER,
            is_accessible BOOLEAN DEFAULT FALSE,
            comments TEXT,
            UNIQUE(latitude, longitude)
         )                  
""" )
    conn.commit()
    conn.close()

def seed_db():

    conn=get_connection()
    cursor=conn.cursor()
    washrooms=[("Tim Hortons - Lakeshore Blvd W", 43.6362, -79.4853, "2088 Lake Shore Blvd W, Toronto", 1, None, None, 0, "Easy parking, 24h"),
    ("McDonald's - Dundas St W", 43.6553, -79.4582, "1408 Dundas St W, Toronto", 1, None, None, 1, "24h drive-through area"),
    ("Petro Canada - Keele St", 43.6891, -79.4773, "2787 Keele St, Toronto", 1, None, None, 0, "Gas station, always open"),
    ("Esso - Lawrence Ave W", 43.7183, -79.4584, "1240 Lawrence Ave W, Toronto", 1, None, None, 0, "Quick stop"),
    ("Tim Hortons - Eglinton Ave W", 43.6979, -79.4263, "970 Eglinton Ave W, Toronto", 1, None, None, 0, "24h, good parking"),
    ("Shell - Weston Rd", 43.7124, -79.5198, "1970 Weston Rd, Toronto", 1, None, None, 0, "Gas station"),
    ("McDonald's - Wilson Ave", 43.7285, -79.4682, "1282 Wilson Ave, Toronto", 1, None, None, 1, "24h, easy access"),]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO  washrooms
        (name,latitude,longitude,address,is_open24h,opening_time,closing_time,is_accessible,comments)VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
""",washrooms)
    
    conn.commit()
    conn.close()

    