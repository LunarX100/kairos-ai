 
import os
import json
from flask import Flask, request, jsonify, render_template_string
from cryptography.fernet import Fernet
import requests

# -------------------------
# ENCRYPTED MEMORY
# -------------------------
MEMORY_FILE = "kairos_memory.json"
KEY_FILE = "kairos_key.key"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "rb") as f:
        decrypted = fernet.decrypt(f.read())
        return json.loads(decrypted)

def save_memory(memory):
    encrypted = fernet.encrypt(json.dumps(memory).encode())
    with open(MEMORY_FILE, "wb") as f:
        f.write(encrypted)

memory = load_memory()

# -------------------------
# GEMINI API CONFIG
# Replace with your Gemini endpoint and API key
# -------------------------
GEMINI_API_URL = "https://api.gemini.ai/v1/chat"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

def kairos_respond(user_input):
    # Include memory context
    context = "\n".join(memory.values())[-2000:]  # last 2k chars
    prompt = f"You are Kairos, a truth-first mentor AI for Daniel. Incorporate memory context:\n{context}\nDaniel: {user_input}\nKairos:"
    
    # Call Gemini API
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_tokens": 500, "temperature":0.2}  # low temp for factual
    try:
        r = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        r.raise_for_status()
        response = r.json().get("text", "")
    except Exception as e:
        response = f"Kairos says: There was an error calling Gemini: {e}"

    # Save memory
    memory[user_input] = response
    save_memory(memory)
    return response

# -------------------------
# FLASK APP + BROWSER UI
# -------------------------
app = Flask(__name__)

CHAT_HTML = """
<!doctype html>
<html>
<head>
<title>Kairos Chat</title>
<style>
body { font-family: Arial; background:#1e1e1e; color:#e0e0e0; margin:0; padding:0;}
#chat { padding:10px; height:80vh; overflow-y:scroll; }
input { width:80%; padding:10px; margin:5px; border-radius:5px; border:none; }
button { padding:10px; border-radius:5px; border:none; background:#4caf50; color:white; }
.message { margin-bottom:10px; }
.user { color:#4caf50; }
.kairos { color:#ff9800; }
</style>
</head>
<body>
<div id="chat"></div>
<input type="text" id="input" placeholder="Ask Kairos...">
<button onclick="sendMessage()">Send</button>
<script>
function appendMessage(sender, msg){
    var chat=document.getElementById("chat");
    var div=document.createElement("div");
    div.className="message " + sender;
    div.innerHTML="<b>"+sender+":</b> "+msg;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}
async function sendMessage(){
    let input=document.getElementById("input");
    let msg=input.value;
    if(msg.trim()=="") return;
    appendMessage("user", msg);
    input.value="";
    let resp=await fetch("/kairos", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message:msg})});
    let data=await resp.json();
    appendMessage("kairos", data.response);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(CHAT_HTML)

@app.route("/kairos", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"error": "No input"}), 400
    answer = kairos_respond(user_input)
    return jsonify({"response": answer})

if __name__ == "__main__":
    print("Kairos v0.1 Gemini Chat running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)