import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv
import db_manager
import time
import threading
import json
import alerta_corrientes

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración mediante variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN", "TU_TOKEN_AQUI")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",") if x.strip()]

bot = telebot.TeleBot(TOKEN)



@bot.message_handler(commands=["start"])
def cmd_start(message):
    msg = bot.send_message(
        message.chat.id,
        "Bienvenido al Sistema de Alerta Temprana de Inundaciones.\n¿Cuál es tu nombre?",
    )
    bot.register_next_step_handler(msg, procesar_nombre)

def procesar_nombre(message):
    nombre = message.text.strip() if message.text else ""
    if not nombre:
        msg = bot.send_message(message.chat.id, "El nombre no puede estar vacío. Por favor, ¿cuál es tu nombre?")
        bot.register_next_step_handler(msg, procesar_nombre)
        return
        
    opciones = (
        "¿En qué barrio vivís? (Elegí el número)\n"
        "1. Cambá Cuá\n"
        "2. 17 de Agosto\n"
        "3. Molina Punta\n"
        "4. Centro"
    )
    msg = bot.send_message(message.chat.id, opciones)
    bot.register_next_step_handler(msg, procesar_barrio, nombre)

def procesar_barrio(message, nombre):
    opcion = message.text.strip() if message.text else ""
    
    barrios = {
        "1": "Cambá Cuá",
        "2": "17 de Agosto",
        "3": "Molina Punta",
        "4": "Centro"
    }
    
    barrio = barrios.get(opcion)
    
    if not barrio:
        msg = bot.send_message(
            message.chat.id, 
            "Opción no válida. Por favor, ingresá el número de tu barrio:\n"
            "1. Cambá Cuá\n"
            "2. 17 de Agosto\n"
            "3. Molina Punta\n"
            "4. Centro"
        )
        bot.register_next_step_handler(msg, procesar_barrio, nombre)
        return
        
    db_manager.guardar_usuario(message.chat.id, nombre, barrio)
    bot.send_message(
        message.chat.id,
        f"Registro completo. Nombre: {nombre} | Barrio: {barrio}.",
    )

@bot.message_handler(commands=["estado"])
def cmd_estado(message):
    barrio = db_manager.obtener_barrio(message.chat.id)
    if barrio is None:
        bot.send_message(message.chat.id, "No estás registrado. Usá /start primero.")
        return
    
    # Respuesta requerida por los requisitos funcionales
    bot.send_message(
        message.chat.id,
        "Niveles hídricos normales",
    )

@bot.message_handler(commands=["disparar_alerta"])
def cmd_disparar_alerta(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "No autorizado.")
        logger.warning(f"Intento de acceso no autorizado a disparar_alerta por {message.from_user.id}")
        return

    partes = message.text.split(maxsplit=1)
    if len(partes) < 2:
        bot.send_message(message.chat.id, "Uso: /disparar_alerta [nombre_del_barrio]")
        return

    barrio = partes[1].strip()
    chat_ids = db_manager.obtener_chat_ids_por_barrio(barrio)

    if not chat_ids:
        bot.send_message(message.chat.id, f"No hay usuarios registrados en {barrio}.")
        return

    texto_alerta = (
        f"🚨 ALERTA NARANJA - {barrio}\n"
        "Se detectó un incremento en los niveles hídricos en tu zona. "
        "Extremá precauciones y seguí las indicaciones de Defensa Civil."
    )

    enviados = 0
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, texto_alerta)
            enviados += 1
        except Exception as e:
            logger.error(f"Error enviando alerta al chat {chat_id}: {e}")
            continue

    bot.send_message(message.chat.id, f"Alerta enviada a {enviados}/{len(chat_ids)} usuarios de {barrio}.")
    logger.info(f"Alerta enviada para el barrio {barrio} a {enviados} usuarios.")
@bot.message_handler(commands=["reportar"])
def cmd_reportar(message):
    usuario = db_manager.obtener_usuario(message.chat.id)
    if usuario is None:
        bot.send_message(message.chat.id, "Necesitás registrarte primero con /start.")
        return

    msg = bot.send_message(
        message.chat.id,
        "Por favor, describí brevemente el problema (ej: Calle inundada, Árbol caído, Granizo):"
    )
    # Pasamos el barrio registrado como argumento extra al siguiente paso
    bot.register_next_step_handler(msg, procesar_tipo_problema, usuario["barrio"])

def procesar_tipo_problema(message, barrio_registrado):
    tipo_problema = message.text.strip() if message.text else ""
    if not tipo_problema:
        bot.send_message(message.chat.id, "El reporte no puede estar vacío. Intentá nuevamente usando /reportar.")
        return

    # Preguntamos por el barrio, dando la opción de usar un atajo
    msg = bot.send_message(
        message.chat.id,
        f"¿En qué barrio ocurre esto?\n\n(Escribí el nombre del barrio, o respondé *ok* para usar tu barrio registrado: {barrio_registrado})",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, guardar_reporte_ciudadano, tipo_problema, barrio_registrado)

def guardar_reporte_ciudadano(message, tipo_problema, barrio_registrado):
    respuesta_barrio = message.text.strip() if message.text else ""
    
    # Si el usuario escribe "ok", usamos el de la BD. Si escribe otra cosa, usamos su texto.
    if respuesta_barrio.lower() == "ok" or respuesta_barrio == "":
        barrio_final = barrio_registrado
    else:
        barrio_final = respuesta_barrio
    
    # Guardamos en la base de datos usando la función existente
    db_manager.guardar_reporte(message.chat.id, tipo_problema, barrio_final)
    
    bot.send_message(
        message.chat.id,
        f"✅ Reporte recibido: '{tipo_problema}' en {barrio_final}. ¡Gracias por informar!"
    )
    logger.info(f"Reporte ciudadano guardado: chat_id={message.chat.id}, tipo={tipo_problema}, barrio={barrio_final}")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def fallback_default(message):
    bot.send_message(
        message.chat.id, 
        "Comando no reconocido. Podés usar /start para registrarte o /reportar para informar un problema en tu barrio."
    )

def chequeo_periodico_clima():
    """Se ejecuta en segundo plano para buscar alertas y avisar a los vecinos."""
    ultima_alerta_enviada = None
    
    while True:
        try:
            logger.info("🔄 Iniciando revisión automática del clima (Open-Meteo)...")
            
            # Ejecutamos el script que actualiza el JSON
            alerta_corrientes.demo_alerta_corrientes()
            
            # Leemos el resultado fresco
            if os.path.exists("ultima_alerta.json"):
                with open("ultima_alerta.json", "r", encoding="utf-8") as f:
                    datos = json.load(f)
                
                nivel = datos.get("nivel_general", 0)
                timestamp = datos.get("timestamp")
                
                # Si hay alerta (Nivel 2 o más) y es nueva (distinto timestamp)
                if nivel >= 2 and timestamp != ultima_alerta_enviada:
                    mensaje = datos.get("mensaje_general", "Alerta meteorológica detectada.")
                    analisis_barrios = datos.get("analisis_barrios", {})
                    
                    # Filtramos solo los barrios que realmente están en peligro
                    barrios_afectados = [b for b, info in analisis_barrios.items() if info["nivel"] >= 2]
                    
                    for barrio in barrios_afectados:
                        chat_ids = db_manager.obtener_chat_ids_por_barrio(barrio)
                        for chat_id in chat_ids:
                            try:
                                bot.send_message(
                                    chat_id, 
                                    f"🚨 ALERTA AUTOMÁTICA - {barrio}\n{mensaje}\nExtremá precauciones y seguí las indicaciones de Defensa Civil."
                                )
                            except Exception as e:
                                logger.error(f"Error enviando alerta a {chat_id}: {e}")
                    
                    # Registramos que esta alerta ya se envió para no spamear a la gente
                    ultima_alerta_enviada = timestamp
                    logger.info(f"✅ Alertas automáticas enviadas a: {barrios_afectados}")
                    
        except Exception as e:
            logger.error(f"❌ Error en el chequeo periódico: {e}")
        
        # Esperar 30 minutos (1800 segundos) antes del próximo escaneo. 
        # (Para probarlo ahora rápido, cambialo a 30 segundos)
        time.sleep(1800)

if __name__ == "__main__":
    db_manager.init_db()
    logger.info("Iniciando bot...")
    
    # Arrancamos el temporizador en segundo plano
    hilo_clima = threading.Thread(target=chequeo_periodico_clima, daemon=True)
    hilo_clima.start()
    
    # Arrancamos el bot de Telegram
    bot.infinity_polling()
