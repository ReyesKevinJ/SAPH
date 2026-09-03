import os
import sqlite3
import logging
import telebot
from telebot import types
from dotenv import load_dotenv

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
DB_PATH = "alertas.db"

bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            chat_id INTEGER PRIMARY KEY,
            nombre TEXT,
            barrio TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Base de datos inicializada correctamente.")

def get_conn():
    return sqlite3.connect(DB_PATH)

def guardar_usuario(chat_id, nombre, barrio):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO Usuarios (chat_id, nombre, barrio) VALUES (?, ?, ?)",
        (chat_id, nombre, barrio),
    )
    conn.commit()
    conn.close()
    logger.info(f"Usuario guardado/actualizado: {chat_id} - {nombre} ({barrio})")

def obtener_barrio(chat_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT barrio FROM Usuarios WHERE chat_id = ?", (chat_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def obtener_chat_ids_por_barrio(barrio):
    conn = get_conn()
    cur = conn.cursor()
    # Búsqueda insensible a mayúsculas/minúsculas para el barrio
    cur.execute("SELECT chat_id FROM Usuarios WHERE LOWER(barrio) = LOWER(?)", (barrio,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

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
        
    guardar_usuario(message.chat.id, nombre, barrio)
    bot.send_message(
        message.chat.id,
        f"Registro completo. Nombre: {nombre} | Barrio: {barrio}.",
    )

@bot.message_handler(commands=["estado"])
def cmd_estado(message):
    barrio = obtener_barrio(message.chat.id)
    if barrio is None:
        bot.send_message(message.chat.id, "No estás registrado. Usá /start primero.")
        return
    
    # Respuesta requerida por los requisitos funcionales ("Niveles hídricos normales")
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
    chat_ids = obtener_chat_ids_por_barrio(barrio)

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
    init_db()
    logger.info("Iniciando bot...")
    bot.infinity_polling()
