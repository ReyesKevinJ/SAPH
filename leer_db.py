import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('alertas.db')
cur = conn.cursor()

try:
    # --- Usuarios ---
    cur.execute("SELECT * FROM Usuarios")
    filas_usuarios = cur.fetchall()
    
    print("--- Registros en alertas.db (Usuarios) ---")
    if not filas_usuarios:
        print("La tabla Usuarios está vacía.")
    else:
        print(f"{'CHAT ID':<15} | {'NOMBRE':<20} | {'BARRIO'}")
        print("-" * 60)
        for fila in filas_usuarios:
            print(f"{fila[0]:<15} | {fila[1]:<20} | {fila[2]}")
            
    print("\n")
    
    # --- Reportes ---
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Reportes';")
    if cur.fetchone():
        cur.execute("SELECT * FROM Reportes")
        filas_reportes = cur.fetchall()
        
        print("--- Registros en alertas.db (Reportes) ---")
        if not filas_reportes:
            print("La tabla Reportes está vacía.")
        else:
            print(f"{'ID':<5} | {'CHAT ID':<15} | {'TIPO PROBLEMA':<25} | {'BARRIO'}")
            print("-" * 80)
            for fila in filas_reportes:
                print(f"{fila[0]:<5} | {fila[1]:<15} | {fila[2]:<25} | {fila[3]}")
    else:
        print("La tabla Reportes aún no existe.")
            
except Exception as e:
    print("Error al leer la base de datos:", e)
finally:
    conn.close()
