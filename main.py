from fastapi import FastAPI
import asyncio
import random
import requests
import time
import os

app = FastAPI(
    title="SmartStade - IoT Streaming Simulator",
    description="Simulation en temps réel des capteurs autour du stade → envoi vers IAAS Azure",
    version="1.0"
)

AZURE_URL = os.getenv("AZURE_URL")
API_KEY = os.getenv("API_KEY")
headers = {"X-API-Key": API_KEY}

zones = ["stade-nord", "stade-sud", "parking-a", "parking-b", "entrée-est", "sortie-ouest"]

async def simulate_sensors():
    while True:
        data = {
            "zone": random.choice(zones),
            "vehicules": random.randint(10, 280),
            "vitesse_moyenne": round(random.uniform(0, 75), 1),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        try:
            requests.post(AZURE_URL, json=data, headers=headers, timeout=5)
            print(f"Envoyé → {data['zone']} | {data['vehicules']} véhicules")
        except:
            print("Azure hors ligne")
        await asyncio.sleep(2)

@app.on_event("startup")
async def start():
    asyncio.create_task(simulate_sensors())

@app.get("/")
def home():
    return {"project": "SmartStade", "role": "PAAS - IoT Simulator", "status": "capteurs actifs"}
