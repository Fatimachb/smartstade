import asyncio
import random
import requests
import os
from fastapi import FastAPI
from datetime import datetime, timedelta

app = FastAPI(title="SmartStade – Simulation Capteurs IoT (CAN 2025)")

AZURE_URL = os.getenv("AZURE_URL")  # http://158.158.40.100:8000/api/v1/traffic
API_KEY = os.getenv("API_KEY", "etudiante1-secret-2025")

# Données réalistes pour le Stade Mohammed V (ou n'importe quel stade CAN 2025)
ZONES = [
    {"id": "CAP_001", "name": "Stade Mohammed V - Entrée Nord"},
    {"id": "CAP_002", "name": "Stade Mohammed V - Entrée Sud"},
    {"id": "CAP_003", "name": "Parking VIP"},
    {"id": "CAP_004", "name": "Avenue Principale"},
    {"id": "CAP_005", "name": "Sortie Ouest - Supporters"},
]

async def envoyer_donnees():
    while True:
        zone = random.choice(ZONES)
        
        # Simule des pics pendant les heures de match (ex: 18h–22h)
        heure_actuelle = datetime.now().hour
        est_jour_match = 17 <= heure_actuelle <= 23
        facteur_match = random.uniform(1.5, 3.5) if est_jour_match else 1.0
        
        vehicules = int(random.randint(20, 180) * facteur_match)
        vitesse = round(random.uniform(0, 60) / facteur_match, 1)
        densite = round(min(vehicules / 300.0, 1.0), 2)  # densité entre 0 et 1
        
        data = {
            "sensor_id": zone["id"],
            "timestamp": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "vehicle_count": vehicules,
            "average_speed": vitesse,
            "density": densite,
            "location": zone["name"]
        }
        
        try:
            response = requests.post(
                AZURE_URL,
                json=data,
                headers={"X-API-Key": API_KEY},
                timeout=10
            )
            status = "OK" if response.status_code == 200 else f"ERREUR {response.status_code}"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] → {zone['name']} | {vehicules} véhicules | {vitesse} km/h | {status}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ÉCHEC envoi → {e}")
        
        # Envoi plus rapide pendant les heures de match pour la démo
        delay = 1 if est_jour_match else 2
        await asyncio.sleep(delay)

@app.on_event("startup")
async def startup_event():
    print("Simulation capteurs SmartStade CAN 2025 → DÉMARRÉE")
    print(f"Envoi vers → {AZURE_URL}")
    asyncio.create_task(envoyer_donnees())

@app.get("/")
def home():
    return {
        "projet": "SmartStade CAN 2025",
        "role": "Simulation capteurs IoT réalistes",
        "status": "ACTIF – Envoi en continu",
        "backend": AZURE_URL
    }
