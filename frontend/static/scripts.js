// Récupération des éléments
const chatInput = document.getElementById("chatInput");
const sendMessageBtn = document.getElementById("sendMessage");
const messagesContainer = document.getElementById("messages");
const newChatBtn = document.getElementById("newChat");
const settingsBtn = document.getElementById('settings');
const settingsMenu = document.getElementById('settingsMenu');
const connectionBtn = document.getElementById('settingConnection')

let abortController = null; // Variable pour contrôler l'annulation de la requête
let connexion_setting = 0 ; 
// Fonction pour ajouter un message dans la conversation
function addMessage(content, isUser = false) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", isUser ? "user" : "bot");

    if (isUser) {
        messageElement.innerText = `👤 Vous : ${content}`;
    } else {
        messageElement.innerText = `🤖 Ollama : ${content}`;
    }
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Fonction pour gérer l'envoi du message
function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    chatInput.value = "";
    sendMessageBtn.innerText = "❌";
    
    abortController = new AbortController();

    fetch("http://localhost:6080/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
        signal: abortController.signal
    })
    .then(response => response.body.getReader())
    .then(reader => {
        const botMessageElement = document.createElement("div");
        botMessageElement.classList.add("message", "bot");
        botMessageElement.innerHTML = "🤖 Ollama : ";
        messagesContainer.appendChild(botMessageElement);
        
        let completeResponse = "";

        function createCodeBlock(code) {
            // Créer le conteneur du bloc de code avec positionnement relatif
            const codeContainer = document.createElement("div");
            codeContainer.style.position = "relative";
            
            // Créer le bloc de code
            const codeBlock = document.createElement("pre");
            codeBlock.className = "code-block";
            codeBlock.textContent = code;
            
            // Créer le bouton de copie
            const copyButton = document.createElement("button");
            copyButton.innerHTML = "📋"; // Icône de copie
            copyButton.style.cssText = `
                position: absolute;
                top: 5px;
                right: 5px;
                padding: 5px 10px;
                background: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #fff;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
            `;
            
            // Effet de hover
            copyButton.onmouseover = () => copyButton.style.opacity = "1";
            copyButton.onmouseout = () => copyButton.style.opacity = "0.7";
            
            // Fonction de copie
            copyButton.onclick = () => {
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = copyButton.innerHTML;
                    copyButton.innerHTML = "✓";
                    setTimeout(() => {
                        copyButton.innerHTML = originalText;
                    }, 1000);
                });
            };
            
            // Assembler le tout
            codeContainer.appendChild(codeBlock);
            codeContainer.appendChild(copyButton);
            
            return codeContainer;
        }

        function processResponse(text) {
            // Supprimons tout le contenu précédent
            while (botMessageElement.firstChild) {
                botMessageElement.removeChild(botMessageElement.firstChild);
            }
            if (connexion_setting == 0 ){botMessageElement.innerHTML = "🤖 Ollama : ";}
            else {botMessageElement.innerHTML = "🤖 Groq: ";}

            // Séparons la réponse en segments
            const segments = text.split("```");
            
            // Traitons chaque segment
            segments.forEach((segment, index) => {
                if (index % 2 === 0) {
                    // Segment de texte normal
                    const textNode = document.createTextNode(segment);
                    botMessageElement.appendChild(textNode);
                } else {
                    // Segment de code - on utilise notre nouvelle fonction createCodeBlock
                    const codeContainer = createCodeBlock(segment);
                    botMessageElement.appendChild(codeContainer);
                }
            });
        }

        function readStream() {
            return reader.read().then(({done, value}) => {
                if (done) {
                    processResponse(completeResponse);
                    sendMessageBtn.innerText = "➤";
                    return;
                }
                
                const chunk = new TextDecoder().decode(value);
                completeResponse += chunk;
                processResponse(completeResponse);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                return readStream();
            });
        }

        return readStream();
    })
    .catch(error => {
        if (error.name === "AbortError") {
            console.log("Requête interrompue.");
        } else {
            console.error("Erreur :", error);
        }
        sendMessageBtn.innerText = "➤";
    });
}




// Fonction pour stopper l'envoi du message en cours
function stopMessage() {
    if (abortController) {
        abortController.abort(); // Annule la requête en cours
    }
    sendMessageBtn.innerText = "➤"; // Réinitialise le bouton
}

// Événements
sendMessageBtn.addEventListener("click", () => {
    if (sendMessageBtn.innerText === "➤") {
        sendMessage(); // Envoie le message
    } else {
        stopMessage(); // Annule l'envoi
    }
});

chatInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") sendMessage(); // Envoie le message avec Enter
});

// Fonction pour réinitialiser le chat
newChatBtn.addEventListener("click", () => {
    messagesContainer.innerHTML = ""; // Supprime tous les messages
    sendMessageBtn.innerText = "➤"; // Réinitialise le bouton
});

// Fonction pour fermer le menu si on clique ailleurs
function closeMenu(event) {
    if (!settingsBtn.contains(event.target) && !settingsMenu.contains(event.target)) {
        settingsMenu.classList.remove('active');
        document.removeEventListener('click', closeMenu);
    }
}

// Gestionnaire pour le bouton settings
settingsBtn.addEventListener('click', (event) => {
    event.stopPropagation(); // Empêche la propagation du clic
    
    // Toggle le menu
    if (settingsMenu.classList.contains('active')) {
        settingsMenu.classList.remove('active');
        document.removeEventListener('click', closeMenu);
    } else {
        settingsMenu.classList.add('active');
        // Ajout d'un petit délai pour éviter que l'événement de clic soit immédiatement capturé
        setTimeout(() => {
            document.addEventListener('click', closeMenu);
        }, 0);
    }
});


// Gestionnaire pour le bouton settings
connectionBtn.addEventListener('click', () => {
    // Définir l'état du bouton en fonction de son texte actuel
    let newMode;  // Déclaration de la variable mode
    let newText;

    // Si le texte du bouton est "🌐 En Ligne", passer à "Hors Ligne"
    if (connectionBtn.innerText === "🌐 En Ligne") {
        newMode = 1; // Envoie 1 pour "Hors Ligne"
        newText = "🌐 Hors Ligne";
    } else {
        newMode = 0; // Envoie 0 pour "En Ligne"
        newText = "🌐 En Ligne";
    }

    connexion_setting = newMode;
    // Mettre à jour l'état du bouton avant d'envoyer la requête
    connectionBtn.innerText = newText;

    // Faire la requête POST à l'API pour mettre à jour le mode
    fetch("http://localhost:6080/mode/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: newMode }), // Envoi de la bonne valeur de mode
    })
    .then(response => {
        // Vérifier si la requête a réussi (status 200-299)
        if (response.ok) {
            console.log("Mode mis à jour avec succès");
        } else {
            // Si la réponse n'est pas OK, afficher une erreur
            throw new Error("Échec de la mise à jour du mode");
        }
    })
    .catch(error => {
        // Si une erreur est capturée (réseau, serveur, etc.), restaurer le texte du bouton
        console.error("Erreur:", error.message);

        // Restaurer l'état précédent du bouton si l'API échoue
        connectionBtn.innerText = newMode === 0 ? "🌐 En Ligne" : "🌐 Hors Ligne";
        
        // Optionnel : Afficher un message d'erreur à l'utilisateur
        alert("Impossible de mettre à jour le mode. Veuillez réessayer plus tard.");
    });
});


document.getElementById('settingPrompt').addEventListener('click', () => {
    console.log('Changer la police');
});

document.getElementById('settingModels').addEventListener('click', () => {
    console.log('Changer la langue');
});


