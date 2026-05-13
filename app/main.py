from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from distance import haversine
from database import get_connection, init_db, seed_db

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message":"Pitstop API is running "}

class LocationInput(BaseModel):
    latitude:float
    longitude:float

@app.post("/find-washroom")
def find_washroom(location: LocationInput):
    conn=get_connection()
    washrooms=conn.execute("SELECT*FROM washrooms").fetchall()
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
            "comments": w["comments"]
        })

    results.sort(key=lambda x: x["distance_km"])
    return results[:3]
    
