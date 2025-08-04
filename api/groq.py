from groq import Groq
from fastapi import APIRouter
from config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, GROQ_API_BASE
from data.llama import system_prompt

groq_router = APIRouter(prefix="/groq",tags=["groq"] ) 

client = Groq(api_key=GROQ_API_KEY,)

# Initialiser l’historique de conversation
chat_history = [{"role": "assistant", "content": system_prompt}]

@groq_router.post("/test")
def test(user_input: str): 
    # Ajouter le message utilisateur à l'historique
    chat_history.append({"role": "user", "content": user_input})

    # Appel à l'API
    response = client.chat.completions.create(
        model=GROQ_MODEL,  # ou autre modèle Groq
        messages=chat_history,
        temperature=TEMPERATURE,
    )

    # Récupérer et stocker la réponse de l'IA
    assistant_reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply