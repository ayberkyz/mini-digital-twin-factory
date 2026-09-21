from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Digital Factory Twin API")

# React arayüzünün (veya tarayıcının) API'ye rahatça erişebilmesi için CORS izni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_FILE = "factory_state.json"

@app.get("/")
def home():
    return {"message": "Digital Factory Twin API aktif!"}

@app.get("/state")
def get_factory_state():
    if not os.path.exists(STATE_FILE):
        raise HTTPException(status_code=404, detail="Henuz fabrika verisi olusmadi. Simulator calisiyor mu?")
    
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veri okunurken hata: {str(e)}")