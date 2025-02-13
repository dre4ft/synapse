from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from ollama import get_ollama_response, OllamaAPIException  # Importation de la fonction et de l'exception personnalisée
import json
from groq_api import GroqAPIException, get_groq_response

app = FastAPI()

# Variable globale pour suivre l'état du mode
connectionSetting = True

@app.post("/mode/")
def change_mode(request_data: dict):
    global connectionSetting  # Indiquer que la variable est globale et peut être modifiée
    mode = request_data.get("mode", "")
    
    # Si mode est 1 (Hors ligne), on passe à False
    if mode == 1 :
        connectionSetting = False
    # Si mode est 0 (En ligne), on passe à True
    elif mode == 0 :
        connectionSetting = True

    # Retourne une réponse indiquant le nouvel état du mode
    return {"message": "Mode mis à jour avec succès", "new_mode": connectionSetting}

# Routes HTML
@app.get("/")
async def serve_index():
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend file not found")

@app.post("/chat/")
async def chat(request_data: dict):
  
    user_message = request_data.get("message", "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    if connectionSetting : 
        def event_stream(response):
                """
                Génère la réponse en temps réel pour le client.
                """
                try:
                    for line in response.iter_lines():
                        if line:
                            try:
                                json_line = json.loads(line)
                                if 'content' in json_line.get('message', {}):
                                    yield json_line['message']['content']
                            except json.JSONDecodeError:
                                pass  # Ignore les erreurs JSON
                except Exception as e:
                    yield f"\n[Erreur] {str(e)}"

        # Si mode "En ligne" (Ollama)
        try:
            # Appel à la fonction get_ollama_response pour obtenir la réponse en streaming
            response = get_ollama_response(user_message)
            return StreamingResponse(event_stream(response), media_type="text/event-stream")
        
        except OllamaAPIException as e:
            # Capture de l'exception OllamaAPIException et renvoi d'une HTTPException
            raise HTTPException(status_code=500, detail=f"Erreur avec l'API Ollama : {e.detail}")
    
    else:     
        def event_stream(response):
            try:

                # Nous lisons le flux de Groq et renvoyons les données ligne par ligne
                for chunk in response:
                    if chunk.choices:
                        yield chunk.choices[0].delta.content or ""  # Adapte selon la structure de Groq

            except Exception as e:
                yield f"\n[Erreur] {str(e)}"

        try:
            # Appel à la fonction get_groq_response pour obtenir la réponse en streaming
            response = get_groq_response(user_message)
            return StreamingResponse(event_stream(response), media_type="text/event-stream") 
        
        except GroqAPIException as e:
            # Capture de l'exception GroqAPIException et renvoi d'une HTTPException
            raise HTTPException(status_code=500, detail=f"Erreur avec l'API Groq : {e.detail}")



   
app.mount("/static", StaticFiles(directory="/root/frontend/static", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
