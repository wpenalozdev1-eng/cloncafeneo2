from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging
from dotenv import load_dotenv
from main.src.domain.schemas import ChatRequest, ChatResponse
from main.src.services.chat_service import ChatService
from main.src.infrastructure.context_loader import ContextLoader

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar contexto al iniciar
try:
    context = ContextLoader.load_full_context()
    chat_service = ChatService(context)
except Exception as e:
    logger.error(f"Error al cargar contexto: {e}")
    raise

app = FastAPI(title="API Cafetería Selecto Granos")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html lang='es'>
    <head>
      <meta charset='UTF-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1.0' />
      <title>Cafetería Chat</title>
      <style>
        body { font-family: Arial, Helvetica, sans-serif; background:#f8f9fb; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; }
        .card { width: min(780px, 95vw); border-radius:12px; box-shadow:0 1rem 2rem rgba(0,0,0,.12); background:#fff; padding:1rem 1.1rem; }
        h1{ margin:0 0 0.75rem 0; font-size:1.4rem; }
        .history{ height:400px; overflow:auto; background:#fafbfc; border:1px solid #e3e7eb; border-radius:8px; padding:.8rem; margin-bottom:.8rem; }
        .msg{margin:.35rem 0; padding:.45rem .65rem; border-radius:8px;}
        .user{ background:#e2f1ff; align-self:flex-end; }
        .bot{ background:#f2f2f7; align-self:flex-start; }
        .input-group{ display:flex; gap:.5rem; }
        input{ flex:1; border:1px solid #cfd6e4; border-radius:8px; padding:.7rem; font-size:1rem; }
        button{ border:none; border-radius:8px; background:#0078d4; color:#fff; padding:.7rem 1rem; cursor:pointer; font-weight:700; }
        button:disabled { background:#8fbce6; cursor:not-allowed; }
      </style>
    </head>
    <body>
      <div class='card'>
        <h1>Chat Cafetería ☕</h1>
        <div class='history' id='history'></div>
        <div class='input-group'>
          <input id='message' placeholder='Escribe tu pregunta...' />
          <button id='send'>Enviar</button>
        </div>
      </div>
      <script>
        const history = document.getElementById('history');
        const message = document.getElementById('message');
        const send = document.getElementById('send');
        const conversation = [];

        function appendBubble(text, origin){
          const div = document.createElement('div');
          div.className = 'msg ' + (origin === 'user' ? 'user' : 'bot');
          div.textContent = text;
          history.appendChild(div);
          history.scrollTop = history.scrollHeight;
        }

        async function sendMessage(){
          const text = message.value.trim();
          if(!text) return;

          appendBubble('Tú: ' + text, 'user');
          conversation.push({role:'user', content:text});
          message.value='';
          send.disabled=true;
          appendBubble('Cargando...', 'bot');

          try {
            const res = await fetch('/chat', {
              method:'POST',
              headers:{'Content-Type':'application/json'},
              body: JSON.stringify({pregunta:text, historial:conversation})
            });
            const data = await res.json();
            const botText = 'Bot: ' + (data.respuesta || 'No hay respuesta');
            history.lastChild.textContent = botText;
            conversation.push({role:'assistant', content:data.respuesta || ''});
          } catch(e){
            history.lastChild.textContent = 'Bot: Error de conexión';
          } finally {
            send.disabled=false;
            message.focus();
          }
        }

        send.addEventListener('click', sendMessage);
        message.addEventListener('keydown', e => { if(e.key==='Enter') sendMessage(); });
      </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = chat_service.respond(request)
        return response
    except ValidationError as e:
        logger.error(f"Error de validación: {e}")
        raise HTTPException(status_code=400, detail="Datos de entrada inválidos")
    except Exception as e:
        logger.error(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
