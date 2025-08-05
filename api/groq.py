from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel
from config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, GROQ_API_BASE
from data.llama import system_prompt

groq_router = APIRouter(prefix="/groq",tags=["groq"] ) 

client = Groq(api_key=GROQ_API_KEY,)

# Initialiser l’historique de conversation
chat_history = [{"role": "assistant", "content": system_prompt}]

class ChatInput(BaseModel):
    message: str


def groq_answer(messages = []):
    
    # Appel à l'API
    response = client.chat.completions.create(
        model=GROQ_MODEL,  # ou autre modèle Groq
        messages=messages,
        temperature=TEMPERATURE,
    )

    chat_history.append({"role": "assistant", "content": response.choices[0].message.content})

    return response.choices[0].message.content

@groq_router.get("/overview")
def overview():
    chat_history.append({"role": "user", "content": """
                         Salut moi, 
                         parle moi de toi en maximum 30 mots 
                         et pose moi une question pour commencer
                        """})

    return groq_answer(chat_history)
     

@groq_router.post("/test")
def test(input: ChatInput): 
    # Ajouter le message utilisateur à l'historique
    chat_history.append({"role": "user", "content": input.message})

    # Récupérer et stocker la réponse de l'IA
    assistant_reply = groq_answer(chat_history)
    chat_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply