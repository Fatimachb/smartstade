# simulateur_etudiante1_avec_vision.py
import asyncio
import random
import requests
import os
import cv2  # <-- ajouté
from datetime import datetime
from fastapi import FastAPI

app = FastAPI(title="SmartStade – Simulateur Capteurs + Caméras (Étudiante 1)")

AZURE_URL = os.getenv("AZURE_URL")          # ton futur endpoint /traffic-data
YOLO_API_URL = os.getenv("YOLO_URL")        # URL ngrok de l'Étudiante 2
API_KEY = os.getenv("API_KEY", "etudiante1-secret-2025")

zones = ["stade-nord", "stade-sud", "parking-a", "entrée-principale", "sortie-ouest"]
video_sources = {
    "stade-nord": "videos/stade_nord.mp4",
    "stade-sud": "videos/match_cameroun.mp4",
    "parking-a": "videos/parking_full.mp4",
    "entrée-principale": "videos/entree_bousculee.mp4",
    "sortie-ouest": "videos/sortie_rapide.mp4"
}

# Pré-charge les vidéos une seule fois
caps = {}
for zone, path in video_sources.items():
    if os.path.exists(path):
        cap = cv2.VideoCapture(path)
        caps[zone] = cap

async def envoyer_donnees_completes():
    while True:
        zone = random.choice(zones)
        
        # 1. Données classiques (comme avant)
        data = {
            "zone": zone,
            "vehicules_simules": random.randint(15, 300),
            "vitesse_moyenne_kmh": round(random.uniform(0, 80), 1),
            "timestamp": datetime.now().isoformat()
        }

        # 2. On récupère une frame de la vidéo correspondant à la zone
        frame = None
        if zone in caps and caps[zone].isOpened():
            ret, frame = caps[zone].read()
            if not ret:
                caps[zone].set(cv2.CAP_PROP_POS_FRAMES, 0)  # boucle
                ret, frame = caps[zone].read()
        
        yolo_result = None
        if frame is not None:
            # Envoi vers l'API YOLO de l'Étudiante 2
            _, img_encoded = cv2.imencode('.jpg', cv2.resize(frame, (640, 640)))
            files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
            try:
                resp = requests.post(YOLO_API_URL, files=files, timeout=8)
                if resp.status_code == 200:
                    yolo_result = resp.json()
            except:
                pass

        # 3. On combine tout et on envoie vers TON backend (Azure Functions, FastAPI, etc.)
        payload_final = {
            **data,
            "source": "simulateur_etudiante1",
            "vision": yolo_result or {"vehicles": None, "density": "unknown", "error": "no_yolo"},
            "vehicules_reels": yolo_result.get("vehicles") if yolo_result else None,
            "densite_reelle": yolo_result.get("density") if yolo_result else None,
            "alerte_embouteillage": yolo_result.get("density") in ["dense", "very_dense"] if yolo_result else False
        }

        try:
            requests.post(AZURE_URL, json=payload_final, 
                         headers={"X-API-Key": API_KEY}, timeout=5)
            print(f"Envoyé → {zone} | Simulé: {data['vehicules_simules']} | Réel (YOLO): {payload_final['vehicules_reels']}")
        except:
            print("Backend injoignable")

        await asyncio.sleep(2.5)  # toutes les 2,5 secondes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(envoyer_donnees_completes())

@app.get("/")
def home():
    return {"role": "ÉTUDIANTE 1 – Simulateur Capteurs + Vision", "status": "actif", "vision": "activée"}
