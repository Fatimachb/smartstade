import asyncio
import random
import requests
import os
from fastapi import FastAPI

app = FastAPI(title="SmartStade – Simulation Capteurs iot")

AZURE_URL = os.getenv("AZURE_URL")
API_KEY = os.getenv("API_KEY", "etudiante1-secret-2025")

zones = ["stade-nord", "stade-sud", "parking-a", "entrée-principale", "sortie-ouest"]

async def envoyer_donnees():
    while True:
        data = {
            "zone": random.choice(zones),
            "vehicules": random.randint(15, 300),
            "vitesse_moyenne": round(random.uniform(0, 80), 1),
            "timestamp": ""
        }
        try:
            requests.post(AZURE_URL, json=data, headers={"X-API-Key": API_KEY}, timeout=5)
        except:
            pass
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(envoyer_donnees())

@app.get("/")
def home():
    return {"role": "Simulation capteurs PaaS", "status": "actif"}
