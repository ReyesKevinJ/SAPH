import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv
import db_manager

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

def procesar_datos_llm(chat_id, json_data):
    """
    Pista de aterrizaje para datos estructurados provenientes de un LLM.
    json_data esperado: {"intencion": "registro"|"reporte", "entidades": {...}}
    """
    try:
        intencion = json_data.get("intencion")
        entidades = json_data.get("entidades", {})

        if intencion == "registro":
            nombre = entidades["nombre"]
            barrio = entidades["barrio"]
            db_manager.guardar_usuario(chat_id, nombre, barrio)
            bot.send_message(
                chat_id,
                f"Registro completo. Nombre: {nombre} | Barrio: {barrio}.",
            )
            logger.info(f"Usuario registrado via LLM: chat_id={chat_id}, barrio={barrio}")

        elif intencion == "reporte":
            usuario = db_manager.obtener_usuario(chat_id)
            if usuario is None:
                bot.send_message(chat_id, "Necesitás registrarte primero con /start.")
                logger.warning(f"Reporte rechazado, usuario no registrado: chat_id={chat_id}")
                return

            tipo_problema = entidades["tipo_problema"]
            barrio = entidades.get("barrio", usuario["barrio"])
            db_manager.guardar_reporte(chat_id, tipo_problema, barrio)
            bot.send_message(
                chat_id,
                f"Reporte recibido: {tipo_problema} en {barrio}. Gracias por informar.",
            )
            logger.info(f"Reporte guardado via LLM: chat_id={chat_id}, tipo={tipo_problema}, barrio={barrio}")

        else:
            bot.send_message(chat_id, "No pude interpretar tu mensaje. Intentá de nuevo.")
            logger.warning(f"Intención desconocida: chat_id={chat_id}, json_data={json_data}")

    except KeyError as e:
        bot.send_message(chat_id, "Faltan datos para procesar tu solicitud.")
        logger.error(f"KeyError procesando LLM data: chat_id={chat_id}, error={e}, json_data={json_data}")
    except Exception as e:
        bot.send_message(chat_id, "Ocurrió un error interno. Intentá más tarde.")
        logger.error(f"Error inesperado: chat_id={chat_id}, error={e}, json_data={json_data}")

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
        
    msg = bot.send_message(message.chat.id, "¿En qué barrio vivís?")
    bot.register_next_step_handler(msg, procesar_barrio, nombre)

def procesar_barrio(message, nombre):
    barrio = message.text.strip() if message.text else ""
    if not barrio:
        msg = bot.send_message(message.chat.id, "El barrio no puede estar vacío. Por favor, ¿en qué barrio vivís?")
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

if __name__ == "__main__":
    db_manager.init_db()
    logger.info("Iniciando bot...")
    bot.infinity_polling()
