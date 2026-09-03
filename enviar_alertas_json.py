import json
import db_manager
from main import bot

def enviar_alertas_desde_json(json_path="ultima_alerta.json"):
    print("Iniciando simulación de envío de alertas segmentadas...")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception as e:
        print(f"Error leyendo el archivo JSON: {e}")
        return

    print(f"\nMensaje general: {datos.get('mensaje_general')}\n")
    
    for barrio, info in datos.get("analisis_barrios", {}).items():
        nivel = info.get("nivel", 0)
        alerta = info.get("alerta", "")
        
        emojis = {
            0: "🔵",
            1: "🟢",
            2: "🟡",
            3: "🟠",
            4: "🔴"
        }
        emoji = emojis.get(nivel, "⚠️")
        
        chat_ids = db_manager.obtener_chat_ids_por_barrio(barrio)
        if not chat_ids:
            print(f"[-] No hay usuarios registrados en {barrio}.")
            continue
            
        texto = (
            f"{emoji} ATENCIÓN - {barrio}\n"
            f"Nivel de Alerta: {nivel}\n"
            f"Situación: {alerta}"
        )
        
        enviados = 0
        for cid in chat_ids:
            try:
                bot.send_message(cid, texto)
                enviados += 1
            except Exception as e:
                print(f"Error enviando a {cid}: {e}")
        
        print(f"[+] Alerta (Nivel {nivel}) enviada a {enviados} usuarios en {barrio}.")
        print(f"    Texto: {alerta}\n")

if __name__ == "__main__":
    enviar_alertas_desde_json()
