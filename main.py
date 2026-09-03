import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv
import db_manager
import llm_client

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

        elif intencion == "alerta_meteorologica":
            barrios_afectados = entidades.get("barrios_afectados", [])
            nivel_alerta = entidades.get("nivel_alerta", "Naranja")
            detalle = entidades.get("mensaje", "Anomalías hídricas detectadas por radar.")
            
            nivel_lower = nivel_alerta.lower()
            
            # Configurar emojis, título y precauciones según nivel
            if nivel_lower == "despejado":
                emoji = "🔵"
                titulo = "REPORTE METEOROLÓGICO"
                pie = "Condiciones óptimas. No se requieren precauciones especiales."
            elif nivel_lower == "verde":
                emoji = "🟢"
                titulo = "REPORTE METEOROLÓGICO"
                pie = "Condiciones normales. Mantente informado."
            elif nivel_lower == "amarilla":
                emoji = "🟡"
                titulo = "ALERTA METEOROLÓGICA"
                pie = "Prestá atención a posibles cambios en el clima."
            elif nivel_lower == "naranja":
                emoji = "🟠"
                titulo = "ALERTA METEOROLÓGICA"
                pie = "Extremá precauciones y seguí las indicaciones oficiales."
            else: # Roja
                emoji = "🔴"
                titulo = "ALERTA METEOROLÓGICA SEVERA"
                pie = "Peligro inminente. Buscá refugio y seguí las indicaciones oficiales."
            
            # Notificación silenciosa si el nivel es bajo
            silencioso = True if nivel_lower in ["despejado", "verde", "amarilla"] else False
            
            total_enviados = 0
            for barrio in barrios_afectados:
                chat_ids = db_manager.obtener_chat_ids_por_barrio(barrio)
                if not chat_ids:
                    continue
                    
                texto_alerta = f"{emoji} {titulo} {nivel_alerta.upper()} - {barrio}\n{detalle}\n{pie}"
                
                for chat_id in chat_ids:
                    try:
                        bot.send_message(chat_id, texto_alerta, disable_notification=silencioso)
                        total_enviados += 1
                    except Exception as e:
                        logger.error(f"Error enviando alerta SMN al chat {chat_id}: {e}")
                        
            logger.info(f"Alerta SMN ({nivel_alerta}) enviada a {total_enviados} usuarios de los barrios: {barrios_afectados} (Silencioso: {silencioso})")

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
    tipo_problema = message.text.strip() if message.text else ""
    if not tipo_problema:
        bot.send_message(message.chat.id, "El reporte no puede estar vacío. Intentá nuevamente usando /reportar.")
        return

    # Usamos la base de datos existente para guardar el reporte
    usuario = db_manager.obtener_usuario(message.chat.id)
    barrio = usuario["barrio"]
    
    db_manager.guardar_reporte(message.chat.id, tipo_problema, barrio)
    
    bot.send_message(
        message.chat.id,
        f"✅ Reporte recibido: '{tipo_problema}' en {barrio}. ¡Gracias por informar!"
    )
    logger.info(f"Reporte ciudadano guardado: chat_id={message.chat.id}, tipo={tipo_problema}, barrio={barrio}")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def manejar_lenguaje_natural(message):
    bot.send_chat_action(message.chat.id, 'typing')
    logger.info(f"Mensaje natural recibido de {message.chat.id}: {message.text}")
    
    # Enviar texto al LLM (OpenRouter)
    json_data = llm_client.interpretar_texto(message.text)
    
    if json_data.get("intencion") == "desconocida":
        bot.send_message(message.chat.id, "Disculpá, no entendí tu mensaje. Podés usar /start para registrarte o describirme un reporte de problemas en tu barrio.")
        return
        
    # Procesar el JSON estructurado con la función existente
    procesar_datos_llm(message.chat.id, json_data)

if __name__ == "__main__":
    db_manager.init_db()
    logger.info("Iniciando bot...")
    bot.infinity_polling()
