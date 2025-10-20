# socket_server.py
from fastapi import APIRouter
import socketio


socket_router = APIRouter(prefix="/socket",tags=["socket"] )  
 
from fastapi_socketio import SocketManager

app = FastAPI()
sio = SocketManager(app=app)

@app.on_event("startup")
async def startup_event():
    await sio.connect() # Connexion au serveur Socket.IO
    print("Serveur Socket.IO démarré.")

@app.get("/")
async def read_root():
    return {"message": "Serveur FastAPI avec Socket.IO"}

@sio.on("connect")
async def handle_connect(sid, *args, **kwargs):
    print(f"Client connecté : {sid}")
    await sio.emit("message_from_server", {"data": "Bienvenue sur le chat !"}, to=sid)

@sio.on("message_from_client")
async def handle_message(sid, data):
    print(f"Message de {sid} : {data}")
    await sio.emit("message_to_client", {"data": data}, skip_sid=sid)

@sio.on("disconnect")
async def handle_disconnect(sid):
    print(f"Client déconnecté : {sid}")




# ✅ Endpoint de test visible dans /docs
@socket_router.post("/test/send_message")
async def test_send_message(data: dict):
    """
    Envoie un message Socket.IO à un utilisateur connecté.
    """
    sender = data.get("from")
    receiver = data.get("to")
    message = data.get("message")
    receiver_sid = connected_users.get(receiver)
    
    connect(sender)

    if receiver_sid:
        await sio.emit("receive_message", data, to=receiver_sid)
        return {"status": "Message envoyé ✅", "to": receiver}
    else:
        return {"error": f"Utilisateur {receiver} non connecté ❌"}