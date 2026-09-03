import os
import json
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Eres el motor de IA del bot SAPH (Sistema de Alerta y Prevención Hídrica).
Tu único propósito es recibir el mensaje de un usuario y extraer la información en un estricto formato JSON. No respondas con texto libre.

Las intenciones posibles son:
1. "registro": Si el usuario se presenta, da su nombre y su barrio para recibir alertas.
2. "reporte": Si el usuario está reportando un problema (inundación, árbol caído, corte de luz, etc).
3. "desconocida": Si el mensaje es incomprensible, es un saludo genérico sin información o no aplica a ninguna de las otras.

Reglas:
- Debes inferir el nombre del usuario y el barrio si están presentes (el barrio siempre es en Corrientes Capital o Resistencia).
- Si es un reporte, extrae una descripción muy breve del "tipo_problema".

FORMATO DE SALIDA (sólo devuelve JSON, sin backticks ni markdown):
Si es un registro:
{
  "intencion": "registro",
  "entidades": {
    "nombre": "Juan",
    "barrio": "La Boca"
  }
}

Si es un reporte:
{
  "intencion": "reporte",
  "entidades": {
    "tipo_problema": "Árbol caído y calle inundada",
    "barrio": "La Boca" // opcional, si lo menciona
  }
}

Si es desconocida:
{
  "intencion": "desconocida",
  "entidades": {}
}
"""

def interpretar_texto(texto: str) -> dict:
    """
    Envía el texto del usuario a OpenRouter (Gemini Flash) y retorna un diccionario con el JSON parseado.
    """
    if not OPENROUTER_API_KEY:
        logger.error("No se encontró OPENROUTER_API_KEY en las variables de entorno.")
        return {"intencion": "desconocida", "entidades": {}}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://saph.bot", # Según requerimientos de OpenRouter
        "X-Title": "SAPH Bot",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texto}
        ],
        "temperature": 0.0 # Temperatura cero para respuestas consistentes en JSON
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Extraer el texto de la respuesta
        content = data["choices"][0]["message"]["content"]
        
        # A veces el LLM agrega backticks ```json ... ```, vamos a limpiarlo por las dudas
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content.strip())
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red comunicándose con OpenRouter: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error parseando la respuesta del LLM. Error: {e}, Respuesta: {content if 'content' in locals() else 'None'}")
        
    return {"intencion": "desconocida", "entidades": {}}
