from config import DB
from datetime import datetime

async def connexionLoginRepo(connexion_id : str, id : str):
    CURRENT_DATE = datetime.now()
    connexion = await DB.connexion.find_one({"connexion_id" : connexion_id}, {"_id": 0})
    isUser = lambda : connexion.get("user_id") == id
    if connexion:
        await DB.connexion.update_one(
            {"connexion_id": connexion_id},              # Filtre
            {"$set": {
                "updated_at" : CURRENT_DATE,
                "user_last_date" : CURRENT_DATE if (isUser()) else connexion.get("user_last_date") if connexion.get("user_last_date") else CURRENT_DATE,
                "guest_last_date" : CURRENT_DATE if (not isUser()) else connexion.get("guest_last_date") if connexion.get("guest_last_date") else CURRENT_DATE,
                "user_is_conntect": True if (isUser()) else connexion.get("user_is_conntect") if connexion.get("user_is_conntect") else False,
                "guest_is_connect": True if (not isUser()) else connexion.get("guest_is_connect") if connexion.get("guest_is_connect") else False,
                # ICI JE VERIFIE SI LE GUEST ENVOIE LE MESSAGE ET LE USER N'EST PAS CONNECTER DE COMPTER LE NOMBRE DE MESSAGE SINON DE METTRE 0
                "user_unread_message" : 0 if (isUser()) else connexion.get("user_unread_message") if connexion.get("user_unread_message") else 0,
                "guest_unread_message" : 0 if (not isUser()) else connexion.get("guest_unread_message") if connexion.get("guest_unread_message") else 0,
            } }     # Action
        )

    return connexion_id
    

async def connexionLogOutRepo(connexion_id : str, id : str):
    CURRENT_DATE = datetime.now()
    connexion = await DB.connexion.find_one({"connexion_id" : connexion_id}, {"_id": 0})
    isUser = lambda : connexion.get("user_id") == id
    if connexion:
        await DB.connexion.update_one(
            {"connexion_id": connexion_id},              # Filtre
            {"$set": {
                "updated_at" : CURRENT_DATE,
                "user_last_date" : CURRENT_DATE if (isUser()) else connexion.get("user_last_date") if connexion.get("user_last_date") else CURRENT_DATE,
                "guest_last_date" : CURRENT_DATE if (not isUser()) else connexion.get("guest_last_date") if connexion.get("guest_last_date") else CURRENT_DATE,
                "user_is_conntect": False if (isUser()) else connexion.get("user_is_conntect") if connexion.get("user_is_conntect") else False,
                "guest_is_connect": False if (not isUser()) else connexion.get("guest_is_connect") if connexion.get("guest_is_connect") else False,
            } }     # Action
        )

    return connexion_id
    