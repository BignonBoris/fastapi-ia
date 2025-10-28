from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
import google.auth.transport.requests
import google.oauth2.service_account
import json
from repositories.matching import getConnexionRepo
from repositories.users import getUserRepo

notification_router = APIRouter(prefix="/notification",tags=["Notification"] )

# 🔑 Mets ici ta Server Key FCM (depuis Firebase Console → Paramètres du projet → Cloud Messaging)
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "AAAA9lSs1Gk:APA91bGzOs697Vrc0w8WN8oMXP9j5ymWDKEIb07-UKEnjZ7dyITIsaFLW4PgXC18ZBE8Exz2U65iJ1SfPfxoRCnrV3rt90ghogFP8SMdgbN2gR6usj6tGqzFEM69wTLcjQ8VGc4kLuFV")

SERVICE_ACCOUNT_FILE = "helper-92613-firebase-adminsdk-4psaf-bc9ef16cb1.json"

# 🔑 Scopes pour FCM
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# Mémoire temporaire (à remplacer par une base de données)
TOKENS = {"web": [], "mobile": []}

class Device(BaseModel):
    token: str
    platform: str  # "web" ou "mobile"

# Modèle pour la requête
class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str

def get_access_token():
    credentials = google.oauth2.service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    print(request)
    return credentials.token

@notification_router.post("/register_device")
def register_device(device: Device):
    if device.token not in TOKENS[device.platform]:
        TOKENS[device.platform].append(device.token)
    return {"status": "ok", "registered": TOKENS}


@notification_router.post("/send")
async def send_test_notification(req: NotificationRequest):
    access_token = get_access_token()
    project_id = json.load(open(SERVICE_ACCOUNT_FILE))["project_id"]
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    print(url) 
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8"
    }
    
    payload = {
        "message": {
            "token": req.token,
            "notification": {
                "title": req.title,
                "body": req.body
            },
            "webpush": {
                "fcm_options": {
                    "link": "/"
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return {"success": True, "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


async def sendNotificationService(data):
    connexion_id = data.get('connexion_id')
    message = data.get("message")
    sender_id = data.get("user_id") 
    connexion = await getConnexionRepo(connexion_id)
    if connexion: 
        sender = await getUserRepo(sender_id)
        receiver = await getUserRepo(connexion.get('user_id') if sender_id != connexion.get('user_id') 
                                 else connexion.get('guest_id'))
        if receiver: 
            if receiver.get('fcmToken') :
                 await send_test_notification(NotificationRequest(
                    token=receiver.get('fcmToken'),
                    title=sender.get('pseudo'),
                    body=message
                ))