from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from distance import haversine
from database import get_connection, init_db
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()

    yield

app = FastAPI(lifespan=lifespan)
#single responsibilty rule
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/app")
def serve_frontend():
    return FileResponse("/app/index.html")

@app.get("/")
def root():
    return {"message":"Pitstop API is running"}

class LocationInput(BaseModel):
    latitude:float
    longitude:float

@app.post("/find-washroom")
def find_washroom(location: LocationInput):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM washrooms")
    columns = [desc[0] for desc in cursor.description]
    washrooms = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    results=[]
    for w in washrooms:
        dist=haversine(location.latitude,location.longitude,
        w["latitude"],w["longitude"])
        results.append({

             "id": w["id"],
            "name": w["name"],
            "address": w["address"],
            "distance_km": round(dist, 2),
            "is_open24h": w["is_open24h"],
            "is_accessible": w["is_accessible"],
            "comments": w["comments"],
            "latitude": w["latitude"],
            "longitude": w["longitude"]
        })

    results.sort(key=lambda x: x["distance_km"])
    return results[:3]

@app.get("/washrooms")
def all_washrooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM washrooms")
    columns = [desc[0] for desc in cursor.description]
    washrooms = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return washrooms

class WashroomInput(BaseModel):
    name:str
    latitude:float
    longitude:float
    address:str= None
    is_open24h:bool=False
    opening_time:str=None
    closing_time:str=None
    is_accessible:bool=False
    comments:str=None



@app.post("/washrooms")
def add_washroom(washroom:WashroomInput):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO washrooms (name, latitude, longitude, address, is_open24h, opening_time, closing_time, is_accessible, comments)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        washroom.name,
        washroom.latitude,
        washroom.longitude,
        washroom.address,
        washroom.is_open24h,
        washroom.opening_time,
        washroom.closing_time,
        washroom.is_accessible,
        washroom.comments

    ))
    conn.commit()
    conn.close()
    return {"message": "Washroom added successfully"}


 