from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message":"Pitstop API is running "}