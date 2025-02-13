from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from ollama import get_ollama_response, OllamaAPIException , list_ollama_models,update_model
import json
from groq_api import GroqAPIException, get_groq_response , list_groq_models,update_model
import handle_history  # Import du module d'historique

app = FastAPI()

connectionSetting = True

@app.post("/mode/")
def change_mode(request_data: dict):
    global connectionSetting
    mode = request_data.get("mode", "")
    
    if mode == 1:
        connectionSetting = False
    elif mode == 0:
        connectionSetting = True

    return {"message": "Mode mis à jour avec succès", "new_mode": connectionSetting}

@app.get("/models/")
def return_models():
    if connectionSetting:
        models = list_ollama_models()
    else :
        models = list_groq_models()
    return models



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

    def get_summary(summary_request):
        response = get_ollama_response(summary_request)
        return response.json().get("message", "")


    context_messages = handle_history.get_context_for_api(user_message)
    if connectionSetting:
        response = get_ollama_response(context_messages)

        # Fonction génératrice pour envoyer le flux en temps réel et stocker la réponse
        async def event_stream():
            response_stream = []
            try:
                for line in response.iter_lines():
                    if line:
                        json_line = json.loads(line)
                        content = json_line.get("message", {}).get("content", "")
                        response_stream.append(content)
                        yield content
            except Exception as e:
                yield f"\n[Erreur] {str(e)}"

            # Sauvegarde après le streaming
            handle_history.update_history(user_message, response_stream, get_summary)

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    else:
        response = get_groq_response(context_messages)

        async def event_stream():
            response_stream = []
            try:
                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    response_stream.append(content)
                    yield content
            except Exception as e:
                yield f"\n[Erreur] {str(e)}"

            handle_history.update_history(user_message, response_stream, get_summary)

        return StreamingResponse(event_stream(), media_type="text/event-stream")

app.mount("/static", StaticFiles(directory="/root/frontend/static", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
