import json
import os
from datetime import datetime

# 📌 Chemin du dossier des conversations
HISTORY_FOLDER = "history"
CONTEXT_FILE = "conversation.json"
MAX_CONTEXT_MESSAGES = 8  # 4 échanges (user + assistant)

# 📌 Assurer que le dossier history existe
os.makedirs(HISTORY_FOLDER, exist_ok=True)

# 📌 Générer un nom de fichier avec horodatage
def generate_history_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(HISTORY_FOLDER, f"conversation_{timestamp}.json")

# 📌 Trouver le fichier d'historique le plus récent
def get_latest_history_file():
    files = [f for f in os.listdir(HISTORY_FOLDER) if f.startswith("conversation_")]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(HISTORY_FOLDER, files[0])

# 📌 Charger l'historique court (fenêtre de contexte)
def load_context():
    try:
        with open(CONTEXT_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"summary": "", "history": []}

# 📌 Sauvegarder l'historique court
def save_context(conversation):
    with open(CONTEXT_FILE, "w") as file:
        json.dump(conversation, file, indent=4)

# 📌 Sauvegarder l'historique global dans un fichier horodaté
def save_full_history(user_input, assistant_reply):
    latest_file = get_latest_history_file()

    # Si aucun fichier n'existe, en créer un nouveau
    if latest_file is None:
        latest_file = generate_history_filename()

    try:
        with open(latest_file, "r") as file:
            full_history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        full_history = {"history": []}

    # Ajouter la nouvelle entrée avec un timestamp
    full_history["history"].append({
        "timestamp": datetime.now().isoformat(),
        "role": "user",
        "content": user_input
    })
    full_history["history"].append({
        "timestamp": datetime.now().isoformat(),
        "role": "assistant",
        "content": assistant_reply
    })

    # Sauvegarder
    with open(latest_file, "w") as file:
        json.dump(full_history, file, indent=4)

# 📌 Créer une nouvelle conversation (nouveau fichier)
def start_new_conversation():
    new_file = generate_history_filename()
    with open(new_file, "w") as file:
        json.dump({"history": []}, file, indent=4)
    return new_file

# 📌 Charger la dernière conversation
def load_latest_conversation():
    latest_file = get_latest_history_file()
    if latest_file:
        with open(latest_file, "r") as file:
            return json.load(file)
    return {"history": []}

# 📌 Mettre à jour le contexte et gérer le résumé
def update_history(user_input, assistant_reply, get_summary_function):
    conversation = load_context()
    history = conversation["history"]

    # Ajouter le message utilisateur et la réponse IA
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": assistant_reply})

    # Vérifier si on dépasse la limite
    if len(history) > MAX_CONTEXT_MESSAGES:
        # Demander à l'IA de faire un résumé
        summary_request = "Fais un résumé concis de cette conversation :\n" + "\n".join(
            [msg["content"] for msg in history[:-MAX_CONTEXT_MESSAGES]]
        )
        summary = get_summary_function(summary_request)

        # Mettre à jour le fichier contexte
        conversation["summary"] = summary
        conversation["history"] = history[-MAX_CONTEXT_MESSAGES:]

    save_context(conversation)
    save_full_history(user_input, assistant_reply)

def get_context_for_api(user_message):
    conversation = load_context()
    context_messages = conversation["history"]

    # On inclut le résumé s'il existe
    if conversation["summary"]:
        context_messages.insert(0, {"role": "system", "content": conversation["summary"]})

    # Ajout du message utilisateur actuel
    context_messages.append({"role": "user", "content": user_message})

    return context_messages