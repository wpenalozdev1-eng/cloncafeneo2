

import os
from pathlib import Path
import google.generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

# Configuramos la API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# El ContextLoader que carga todo (Inspirado en tu clase - Diapositiva 601)
class ContextLoader:
    def load_skill(self) -> str:
        path = Path("skills/asistente-tienda.md")
        # Si el archivo no existe, usamos unas reglas por defecto en lugar de fallar
        if not path.exists():
            return """
            Eres el asistente virtual de la cafetería Aroma & Código. 
            Solo debes responder preguntas sobre el menú, precios y promociones de la tienda.
            Si te preguntan de otros temas di que no puedes ayudar con eso.
            """
        return path.read_text(encoding='utf-8')

    def load_knowledge(self) -> str:
        # Buscamos archivos .md en la carpeta knowledge
        files = sorted(Path("knowledge").glob("*.md"))
        
        # Si la carpeta no existe o está vacía, usamos un menú por defecto
        if not files:
            return """
            ## Menú por defecto
            - Café Espresso: $2.00
            - Café Americano: $2.50
            - Capuchino: $3.50
            - Latte: $3.50
            - Galleta de avena: $1.50

            ## Promociones
            - Jueves 2x1 en capuchinos.
            """
            
        return "\n\n---\n\n".join(
            f.read_text('utf-8') for f in files
        )

    def load_full_context(self) -> str:
        skill = self.load_skill()
        knowledge = self.load_knowledge()
        return (
            f"{skill}\n\n"
            f"## Base de conocimiento:\n\n{knowledge}"
        )
# Función principal para chatear
def chat_cafeteria(pregunta_usuario: str) -> str:
    # 1. Cargamos las reglas y el menú
    loader = ContextLoader()
    prompt_completo = loader.load_full_context()
    
    # 2. Creamos el modelo con instrucciones del sistema
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=prompt_completo
    )
    
    try:
        # 3. Generamos la respuesta
        response = model.generate_content(
            pregunta_usuario,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        
        # Si Gemini no responde nada por seguridad o bloqueo, forzamos un texto
        if not response.text:
            return "Hola. No tengo una respuesta para eso según mis reglas actuales o el sistema me bloqueó la consulta. ¿Puedo ayudarte con el menú?"
            
        return response.text
        
    except Exception as e:
        return f"Error interno en la conexión con Gemini: {e}"

# Ejemplo de ejecución
if __name__ == "__main__":
    # Prueba 1: Pregunta válida
    print("Cliente: ¿Qué promociones tienen?")
    print(f"Bot: {chat_cafeteria('¿Qué promociones tienen?')}\n")
    
    # Prueba 2: Pregunta fuera de contexto (Infiltrado)
    print("Cliente: ¿Cómo hago un algoritmo de ordenamiento en Python?")
    print(f"Bot: {chat_cafeteria('¿Cómo hago un algoritmo de ordenamiento en Python?')}")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    