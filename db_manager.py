import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_PATH = "alertas.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            chat_id INTEGER PRIMARY KEY,
            nombre TEXT,
            barrio TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            tipo_problema TEXT,
            barrio TEXT,
            FOREIGN KEY (chat_id) REFERENCES Usuarios (chat_id)
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Base de datos y tablas inicializadas correctamente (Usuarios y Reportes).")

def guardar_usuario(chat_id, nombre, barrio):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO Usuarios (chat_id, nombre, barrio) VALUES (?, ?, ?)",
        (chat_id, nombre, barrio),
    )
    conn.commit()
    conn.close()
    logger.info(f"Usuario guardado/actualizado en DB: {chat_id} - {nombre} ({barrio})")

def obtener_usuario(chat_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT chat_id, nombre, barrio FROM Usuarios WHERE chat_id = ?", (chat_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return {"chat_id": row[0], "nombre": row[1], "barrio": row[2]}

def obtener_barrio(chat_id):
    """Mantenida por retrocompatibilidad temporal de main.py"""
    usuario = obtener_usuario(chat_id)
    return usuario["barrio"] if usuario else None

def obtener_chat_ids_por_barrio(barrio):
    conn = get_conn()
    cur = conn.cursor()
    # Búsqueda insensible a mayúsculas/minúsculas para el barrio
    cur.execute("SELECT chat_id FROM Usuarios WHERE LOWER(barrio) = LOWER(?)", (barrio,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

def guardar_reporte(chat_id, tipo_problema, barrio):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Reportes (chat_id, tipo_problema, barrio) VALUES (?, ?, ?)",
        (chat_id, tipo_problema, barrio),
    )
    conn.commit()
    conn.close()
    logger.info(f"Reporte guardado en DB: chat_id={chat_id}, tipo={tipo_problema}, barrio={barrio}")
