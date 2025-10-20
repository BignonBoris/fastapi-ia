from groq import Groq, AuthenticationError
from fastapi import HTTPException 
from config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, MONGO_URI

groqClient = Groq(api_key=GROQ_API_KEY,)

async def groqApi(messages = []):
    try:
        # Appel à l'API
        response = groqClient.chat.completions.create(
            model=GROQ_MODEL,  # ou autre modèle Groq
            messages=messages,
            temperature=TEMPERATURE,
        )
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
    
        if not response.choices[0].message.content:
            return "no found"

        print(response)

        return {"messages" : messages , "message" : response.choices[0].message.content}

    except AuthenticationError:
        raise HTTPException(
            status_code = 401,
            detail= "Api Key Invalid"
        )