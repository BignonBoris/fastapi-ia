from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel
from config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, GROQ_API_BASE, MONGO_URI
from data.llama import build_system_prompt 
from models.models import UserInput, ChatInput
from motor.motor_asyncio import AsyncIOMotorClient
import json
import uuid
from types import SimpleNamespace

groq_router = APIRouter(prefix="/groq",tags=["groq"] ) 

groqClient = Groq(api_key=GROQ_API_KEY,)

mongoClient = AsyncIOMotorClient(MONGO_URI)
db = mongoClient.sample_mflix  # Nom de ta base

# Initialiser l’historique de conversation
chat_history = [ ]


async def getInitPrompt (user_id: str):
    userItem = await db.users.find_one({"user_id" : user_id})

    system_prompt = build_system_prompt(SimpleNamespace(**{ "name" : "", "age" : "", "sexe" : "", })) 

    if userItem:
        system_prompt = build_system_prompt(SimpleNamespace(**{
            "name" : userItem.get("name"),
            "age" : userItem.get("age"),
            "sexe" : userItem.get("sexe"),
            # "country" : userItem.get("country"),
        })) 
    
    return system_prompt  



async def save_answer(user_id : str):
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    # print(conversationItem)
    if conversationItem :
        await db.projets.update_one(
            {"user_id": conversationItem.get("user_id")},              # Filtre
            {"$set": {"messages": chat_history}}     # Action
        )
    else :
        await db.projets.insert_one({
            "user_id" : user_id, 
            "messages" : chat_history
        })

    # return 'result'

async def save_user(data : UserInput): 
    unique_code = str(uuid.uuid4())
    await db.users.insert_one({
        "user_id" : unique_code,
        "email" : unique_code, 
        "name" : data.name, 
        "age" : data.age,
        "sexe" : data.sexe,
        # "country" : data.country,
    })

    return unique_code


async def groq_answer(user_id : str):
    
    # Appel à l'API
    response = groqClient.chat.completions.create(
        model=GROQ_MODEL,  # ou autre modèle Groq
        messages=chat_history,
        temperature=TEMPERATURE,
    )

    chat_history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    if not response.choices[0].message.content:
        return "no found"
        # Appel à l'API
        response = groqClient.chat.completions.create(
            model=GROQ_MODEL,  # ou autre modèle Groq
            messages=chat_history,
            temperature=TEMPERATURE,
        )

    await save_answer(user_id)

    print(response)

    return response.choices[0].message.content


@groq_router.post("/create_user")
async def createUser(input: UserInput):
    user_id = await save_user(input)
    return user_id

# Ajouter un tableau d'objets
@groq_router.post("/add_data")
async def add_data():
    data = {
        "nom": "Projet IA",
        "taches": [
            {"id": 1, "titre": "Créer API", "fait": False},
            {"id": 2, "titre": "Déployer sur Render", "fait": True}
        ]
    }
    result = await db.projets.insert_one(data)
    return {"id_inseré": str(result.inserted_id)}

@groq_router.get("/overview/{user_id}")
async def overview(user_id: str):
    # await init_messages(user_id)

    global chat_history
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    
    print(conversationItem)
    if conversationItem:
        chat_history = conversationItem.get("messages")
        # chat_history.append({"role": "user", "content": """continue la conversation avec une autre question"""})
    else:
        chat_history = [{"role": "assistant", "content": await getInitPrompt(user_id) }]
        chat_history.append({"role": "user", "content": """ 
                Salut moi,  parle moi de toi en maximum 30 mots et pose moi une question pour commencer
            """}) 
        await groq_answer(user_id)

    return chat_history[2:]
     

@groq_router.post("/test/{user_id}")
async def test(user_id: str , input: ChatInput): 
    # await init_messages(user_id)
    # Ajouter le message utilisateur à l'historique
    chat_history.append({"role": "user", "content": input.message})

    # Récupérer et stocker la réponse de l'IA
    assistant_reply = await groq_answer(user_id)
    # chat_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply

@groq_router.get("/test/reload/{user_id}")
async def reloadAnswer(user_id: str): 

    global chat_history
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    
    print(conversationItem)
    if conversationItem:
        chat_history = conversationItem.get("messages")
        # on filtre les messages envoyés par l’assistant
        assistant_messages = [msg for msg in chat_history if msg["role"] == "assistant"]
        # si au moins un message trouvé, on prend le dernier
        return assistant_messages[-1]["content"] if assistant_messages else None
    else:
        return None 
    

@groq_router.get("/sagesse/{user_id}")
async def getSagesse(user_id: str):
    
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    historical = []
    
    if conversationItem: 
        historical = conversationItem.get("messages")
    else:
        historical = [{"role": "assistant", "content": await getInitPrompt(user_id) }]
    
    historical.append({
        "role": "user",
        "content" : """En te basant sur nos échanges précédents, et en conservant ton rôle de conseiller matrimonial :
                        Fournis une sagesse pertinente pour aider à mieux gérer la situation amoureuse actuelle.
                        Ta réponse doit inclure une explication claire et la leçon à retenir.
                        Le tout doit être structuré **exclusivement** au format JSON avec les clés suivantes :
                        {"sagesse", "explanation", "lesson"}
                        **Ne retourne que le JSON. Aucun autre texte n'est autorisé.**
                        """
    })

    # Appel à l'API
    response = groqClient.chat.completions.create(
        model=GROQ_MODEL,  # ou autre modèle Groq
        messages=historical,
        temperature=TEMPERATURE,
    )
    response = response.choices[0].message.content
    
    print(response)
    return json.loads(response)


@groq_router.get("/sms/{user_id}")
async def getSms(user_id: str):
    
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    historical = []
    
    if conversationItem: 
        historical = conversationItem.get("messages")
    else:
        historical = [{"role": "assistant", "content": await getInitPrompt(user_id) }]
    
    
    historical.append({
        "role": "user",
        "content" : """Agis comme un assistant romantique expert en communication amoureuse.
                    Génère un message amoureux unique et sincère qui pourrait être envoyé à un partenaire pour renforcer ou raviver les sentiments.
                    Le message doit être élégant, respectueux et chaleureux.
                    Pour chaque proposition :
                    message → une phrase ou un court paragraphe exprimant l’émotion (tu peux utiliser des icônes, le formatage gras ou italique si nécessaire).
                    moment → une liste non ordonnée (- élément) contenant 3 moments précis où ce message peut être envoyé.
                    reaction → une liste non ordonnée (- élément) contenant 3 effets recherchés ou réactions attendues de la personne qui reçoit ce message.
                    Structure de sortie obligatoire : retourne uniquement un JSON au format suivant, sans aucun texte autour :
                    { 
                    "message": "...",
                    "moment": [ "- ...", "- ...", "- ..." ],
                    "reaction": [ "- ...", "- ...", "- ..." ]
                    }
                    """
        })
    
    # Appel à l'API
    response = groqClient.chat.completions.create(
        model=GROQ_MODEL,  # ou autre modèle Groq
        messages=historical,
        temperature=TEMPERATURE,
    )
    response = response.choices[0].message.content
    
    print(response)
    return json.loads(response)