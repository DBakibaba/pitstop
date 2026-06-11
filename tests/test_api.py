from fastapi.testclient import TestClient

 
from main import app

 
client=TestClient(app)

def test_root_status_code():
    response=client.get("/")

    assert response.status_code==200

    assert response.json()=={
        "message":"Pitstop API is running"
    }

def test_find_washroom_status_code():
    response=client.post("/find-washroom",json={
        "latitude": 43.6532,
        "longitude": -79.3832
    })
    assert response.status_code == 200

def test_find_washroom_returns_three_results():
    response = client.post(
    "/find-washroom",
    json={
    "latitude": 43.6532,
    "longitude": -79.3832
    }
    )

    data = response.json()

    assert len(data) == 3

def test_find_washroom_results_are_sorted():
    response = client.post(
    "/find-washroom",
    json={
    "latitude": 43.6532,
    "longitude": -79.3832
    }
    )
    data = response.json()

    assert data[0]["distance_km"] <= data[1]["distance_km"]
    assert data[1]["distance_km"] <= data[2]["distance_km"]

def test_find_washroom_invalid_latitude():
    response = client.post(
    "/find-washroom",
    json={
    "latitude": "banana",
    "longitude": -79.3832
    }
    )

    assert response.status_code == 422

    response=client.post("/find-washroom")

def test_add_washroom_success():
    response=client.post(
    "/washrooms",
    json={
    "name":"Dodo test wc",
    "latitude": 43.5020,
    "longitude": -79.4000
    }
    )
    assert response.status_code==200
    assert response.json()=={
        "message":"Washroom added successfully"
    }
def test_add_dublicated_washroom_success():
    response=client.post(
    "/washrooms",
    json={
    "name":"Dodo test wc",
    "latitude": 43.7000,
    "longitude": -79.4000
    }
    )
    assert response.status_code==409
    assert response.json()=={
        "detail":"Location already exist in database"
    }