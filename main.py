from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests, time
from typing import Union, List
from cors import setup_cors
from fastapi_socketio import SocketManager
from fastapi.staticfiles import StaticFiles
# from api.socket_server import  socket_router  # ✅ Import de ton fichier socket
import socketio
from models.models import Item, ModelName, IaModel
from api.openia import openia_router 
# from api.chromadb import chromadb_router
from api.llama_local import llama_router 
from api.groq import groq_router
from api.matching import matching_router
from api.user import user_router
from api.notification import notification_router , sendNotificationService
from api.auth import auth_router
from api.connexion import connexion_router
from repositories.matching import getAllUserConnexionsRepo
from fastapi.encoders import jsonable_encoder

app = FastAPI() 

# Chemin vers le dossier d'upload
UPLOAD_DIR = "uploads"

# Création du dossier si nécessaire
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔥 Permet d'accéder aux fichiers à l'adresse : http://127.0.0.1:8000/uploads/<filename>
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS pour éviter les erreurs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu peux limiter à localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_cors(app)

sio = SocketManager(app=app, mount_location="/socket.io")


app.include_router(openia_router)
# app.include_router(chromadb_router)
app.include_router(llama_router)
app.include_router(groq_router)
app.include_router(matching_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(auth_router)
app.include_router(connexion_router)
# app.include_router(socket_router)



@app.get("/")
def read_root():
    file_path = os.path.join("static", "test_socket.html")
    while True:
        try:
            r = requests.get("https://fastapi-ia-74eo.onrender.com/", timeout=10)
            print("Ping réussi ✅", r.status_code)
            with open(file_path, "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
        except Exception as e:
            print("Erreur de ping ❌", e)
        time.sleep(600)  # toutes les 10 minutes



# @app.on_event("startup")
# async def startup_event():
#     await sio.connect() # Connexion au serveur Socket.IO
#     print("Serveur Socket.IO démarré.")


@sio.on("connect")
async def handle_connect(sid, *args, **kwargs):
    print(f"Client connecté : {sid}")
    await sio.emit("server_to_client", {"data": "Bienvenue sur le chat !"}, to=sid)

@sio.on("client_to_server")
async def handle_message(sid, data ):
    print(f"Message de {sid} : {data }")
    print(f"Message de {sid} : {data.get('connexion_id')}")
    # await sio.emit("receive_message", {"msg": data}, broadcast=True)
    # await sio.emit("server_to_client", {"msg": data}, to=sid )
    await sio.emit(f"server_to_client_#{data.get('connexion_id')}", {"user_id": data.get("user_id"), "message": data.get("message")}, skip_sid=sid)
    await sendNotificationService(data)


@sio.on("client_to_server_user_connexion_update")
async def handle_message_to_update_connexion_list(sid, data ):
    # await sio.emit("receive_message", {"msg": data}, broadcast=True)
    # await sio.emit("server_to_client", {"msg": data}, to=sid )
    user_id = data.get('user_id')
    guest_id = data.get('guest_id')

    response_user = await getAllUserConnexionsRepo(user_id)
    await sio.emit(f"server_to_client_user_connexion_update#{user_id}", {"data": jsonable_encoder(response_user)}, to=sid)

    response_guest = await getAllUserConnexionsRepo(guest_id)
    await sio.emit(f"server_to_client_user_connexion_update#{guest_id}", {"data": jsonable_encoder(response_guest)}, to=sid)



@sio.on("disconnect")
async def handle_disconnect(sid):
    print(f"Client déconnecté : {sid}")
