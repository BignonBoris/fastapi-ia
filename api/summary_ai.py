from fastapi import APIRouter, Request
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE
from models.models import IaModel
import openai

summary_router = APIRouter()

@summary_router.post("/summary")
async def summary_ai_test(ia: IaModel):
    openai.api_key = OPENAI_API_KEY 

    system =  "Tu es un professeur agrégée en français qui produit d'excellent résumé de texte de façon claire et concise." 

    text = f"""{system}, rédige un résumé du texte suivant : {ia.content}, 
                   rend le test le plus concis possible avec au plus les 1/10 du nombre de mots utiliser dans le texte original, 
                   le texte dans le style : {ia.style}"""

    response = openai.ChatCompletion.create(
        model= MODEL_NAME,
        messages=[{"role": "user", "content": text }],
        temperature= TEMPERATURE
    )

    return response 