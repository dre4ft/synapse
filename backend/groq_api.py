import json
from fastapi import HTTPException
from groq import Groq

# Initialisation du client Groq
client = Groq(
    api_key="TODO"
)

MODEL = "llama-3.3-70b-versatile"

class GroqAPIException(Exception):
    """Exception personnalisée pour les erreurs liées à l'API Groq."""
    def __init__(self, detail: str):
        self.detail = detail

def list_groq_models():

    try:
        response = client.models.list()
        return [model.id for model in response.data]  # Récupère uniquement les IDs des modèles
    
    except Exception as e:
        # En cas d'erreur avec Groq, on lance une exception personnalisée
        raise GroqAPIException(f"Erreur avec l'API Groq : {str(e)}")

def update_model(new_model : str):
    MODEL = new_model

def get_groq_response(user_message: str,model_used = MODEL):
    """
    Envoie une requête à l'API Groq pour obtenir une réponse en streaming.
    Si un problème survient, une exception personnalisée est levée.
    """
    if not user_message:
        raise GroqAPIException("Le message ne peut pas être vide.")

    try:
        # Construction de la requête pour Groq
        completion = client.chat.completions.create(
            model=model_used,  # Remplace avec ton modèle Groq spécifique
            messages=[{"role": "user", "content": user_message}],
            temperature=1,
            max_completion_tokens=9140,
            top_p=1,
            stream=True,
            stop=None,
        )
        
        return completion  # Retourne l'objet de complétion (streaming)
    
    except Exception as e:
        # En cas d'erreur avec Groq, on lance une exception personnalisée
        raise GroqAPIException(f"Erreur avec l'API Groq : {str(e)}")
