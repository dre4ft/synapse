import requests
import json
from fastapi import HTTPException

# URL de l'API locale d'Ollama
OLLAMA_API_URL = "http://host.docker.internal:11434/api/chat"
MODEL = "qwen2.5-coder"

class OllamaAPIException(Exception):
    """Exception personnalisée pour les erreurs liées à l'API Ollama."""
    def __init__(self, detail: str):
        self.detail = detail

def get_ollama_response(user_message: str):
    """
    Envoie une requête à l'API Ollama pour obtenir une réponse en streaming.
    Si un problème survient, une exception personnalisée est levée.
    """
    if not user_message:
        raise OllamaAPIException("Le message ne peut pas être vide.")

    # Construction du message au format Ollama
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_message}],
        "stream": True
    }

    headers = {"Content-Type": "application/json"}

    try:
        # Envoie la requête à Ollama et commence à streamer la réponse
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True)
        
        if response.status_code != 200:
            raise OllamaAPIException(f"Erreur avec l'API Ollama, code : {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        # En cas de problème réseau ou autre erreur de requête
        raise OllamaAPIException(f"Erreur de communication avec l'API Ollama : {str(e)}")

    return response
