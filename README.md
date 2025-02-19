# Synapse  

**Synapse** is a web UI build in vanilla HTML/CSS/JS that allows you to seamlessly interact with **Ollama (local)** and **Groq (remote) APIs**. While it currently focuses on chatting, future updates will introduce full API management, model handling, and advanced features.  

## 🚀 Features  

- **Chat with Ollama & Groq** – Easily interact with both APIs from a unified web interface.  
- **Upcoming Features:**  
  - Manage available models  
  - Create and configure pre-prompts  
  - Pull and run new Ollama models directly from the web UI  
- **Chat History (Coming Soon)** – Save and review past conversations.  

## 🛠️ Getting Started  

### Prerequisites  
- **Docker** installed on your machine  
- **Access to Ollama (local) and/or Groq API (remote)**  

### Running Synapse with Docker  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/your-username/synapse.git
   cd synapse
   ```
2. **Add your Groq API key in backend/groq_api.py :**
   ```bash
   cd backend && vim groq_api.py 
   ```
  
4. **Build the Docker image:**  
   ```bash
   docker build -t synapse .
   ```

5. **Run the container:**  
   ```bash
   docker run -d -p 6080:80 --name synapse synapse
   ```

6. **Access the UI** in your browser:  
   ```
   http://localhost:6080
   ```

## 📌 Roadmap  

✅ Basic chat functionality with Ollama & Groq  
🔄 API management tools (Coming Soon)  
📝 Conversation history & logging (Coming Soon)  
📥 Model download & execution for Ollama (Planned)  

## 💡 Contributing  

Contributions are welcome! Feel free to fork the repo, submit issues, or suggest improvements.  

## 📜 License  

This project is licensed under the **MIT License**.  

---

This version makes it clear that the project runs in a Docker container and provides simple, step-by-step instructions. Let me know if you need any modifications! 🚀
