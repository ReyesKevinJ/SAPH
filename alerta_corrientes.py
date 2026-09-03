import requests
from io import BytesIO
from PIL import Image
import json  

def demo_alerta_corrientes():
    # 1. Configuración del radar
    radar_id = "RMA4"
    alcance = "240" 
    
    url_json = f"https://ws1.smn.gob.ar/v1/images/radar/{radar_id}_{alcance}"
    
    # Tu token (asegurate de que siga siendo válido, o copialo de nuevo si pasaron 2 hs)
    token_smn = "JWT eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ3ZWIiLCJzY29wZXMiOiJST0xFX1VTRVJfRk9SRUNBU1QsUk9MRV9VU0VSX0dFT1JFRixST0xFX1VTRVJfSElTVE9SWSxST0xFX1VTRVJfSU1BR0VTLFJPTEVfVVNFUl9NQVAsUk9MRV9VU0VSX01FU1NBR0VTLFJPTEVfVVNFUl9SQU5LSU5HLFJPTEVfVVNFUl9TVEFUSVNUSUNTLFJPTEVfVVNFUl9XQVJOSU5HLFJPTEVfVVNFUl9XRUFUSEVSIiwiaWF0IjoxNzg4NDQ1MzI4LCJleHAiOjE3ODg0NDg5Mjh9.7I8n0wNOFfk36HuzO3LfAVKCJi2XlcrPY4RGhvoFDyY"

    # Tu cookie de Cloudflare
    cookie_smn = "has_js=1; cf_clearance=k66uCsnCbT1A7GlU3wmOeL0rG6PXwxai9uTuYznagqw-1788444707-1.2.1.1-a_aaAx9QLSwQXyPQZ6zSwALWOpMzgLYkwpNzKOZkU4kNCtbOEeu7VeAoLsAkrfa22K9g2hIh6gwZFBwj6orblJ8WAuIpXtqSyyKCQIwGqxcSd3B_QPKPiWwvgSy50sz.W9GqWcB1BrMR1uLKJiPp3hag0BhPoM_NRzoQIjPBD9hWxDwI1RiJy4UsHD9a_oXcKBnBLbTkUMVJaPSKlKSw2UwksXVf2xOuqJD5Mnx0EWGHOBv2lXAxyzkjgYtDBxZud.5cQRukxwO23rW7sQJgmOKsJ36f05hfeOBUwxq3KSYLLMVh9KQjMIKnp0BXJVKqUbec8D_XPrKEK32qGHo2zRfwp0AqOjQcsfmH7zEyg6TRciVHUyEmwlp1ulISb83FmmfLX9dM6w.ibBs.MUxh88mjgcBGh1gWG_bie_kYu2Wu1BW1gpk7fMVYqsOZKuuectD3yP1Q04ekieGCyapRMw"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Cookie": cookie_smn,
        "Authorization": token_smn
    }

    print(f"📡 1. Consultando catálogo del radar {radar_id} en ws1.smn.gob.ar...")
    try:
        req_json = requests.get(url_json, headers=headers, timeout=10)
        req_json.raise_for_status()
        frames = req_json.json()
        
        # --- NUEVA LÓGICA DE EXTRACCIÓN ---
        # Extraemos la lista de la clave 'list'.
        if 'list' in frames and len(frames['list']) > 0:
            # Tomamos el primer elemento (índice 0), que suele ser el más reciente
            nombre_archivo = frames['list'][0]
            print(f"✅ Última captura detectada: {nombre_archivo}")
        else:
            print("❌ No se encontró la lista de imágenes o está vacía.")
            return
        
    except Exception as e:
        print(f"❌ Error al consultar la API: {e}")
        return

# 2. Construcción de URL y descarga
    url_imagen = f"https://estaticos.smn.gob.ar/vmsr/radar/{nombre_archivo}"
    print(f"📥 2. Descargando reflectividad: {url_imagen}")
    
    # Clonamos de manera exacta los headers de tu navegador Brave/Chrome
    headers_img = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.smn.gob.ar/",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "Cookie": cookie_smn
    }

    try:
        req_img = requests.get(url_imagen, headers=headers_img, timeout=15)
        req_img.raise_for_status()
        imagen = Image.open(BytesIO(req_img.content))
        print("✅ Imagen de radar descargada correctamente.")
    except Exception as e:
        print(f"❌ Error al descargar la imagen PNG: {e}")
        print("🔧 [TEST] Usando imagen simulada (Cielo Despejado) para continuar la prueba de integración...")
        # Creamos una imagen simulada con el color base oscuro (r=24, g=27, b=33) del radar vacío
        imagen = Image.new('RGB', (1000, 1000), color=(24, 27, 33))

    # 3. Análisis de píxeles (Ciudad de Corrientes)
    ancho, alto = imagen.size
    centro_x, centro_y = ancho // 2, alto // 2
    
    offset_este_px = int(ancho * 0.04) 
    x_corrientes = centro_x + offset_este_px
    y_corrientes = centro_y
    
    pixel_rgb = imagen.convert("RGB").getpixel((x_corrientes, y_corrientes))
    print(f"\n🔍 3. Analizando coordenadas de Corrientes Capital (Píxel {x_corrientes}, {y_corrientes}):")
    print(f"   🎨 Color detectado (R, G, B): {pixel_rgb}")

    # 4. Decodificación de niveles de alerta
    r, g, b = pixel_rgb
    
    # Asignamos un código numérico de severidad para el JSON (0 a 4)
    if r > 200 and g < 100 and b < 200:
        alerta = "ALERTA ROJA: Tormenta severa o granizo inminente."
        nivel = 4
    elif r > 200 and g > 150:
        alerta = "ALERTA NARANJA: Lluvia muy fuerte, posible anegamiento."
        nivel = 3
    elif g > 150 and r < 100:
        alerta = "ALERTA AMARILLA: Lluvia moderada continua."
        nivel = 2
    elif b > 150 and r < 100:
        alerta = "Llovizna o ecos parásitos débiles."
        nivel = 1
    else:
        alerta = "CIELO DESPEJADO: No se detectan ecos de precipitación significativos."
        nivel = 0

    print(f"\n🚨 DIAGNÓSTICO EN TIEMPO REAL: {alerta}")

    # 5. Generar y mostrar el JSON
    # Extraemos la fecha/hora del nombre del archivo (ej: 20260903_143057)
    timestamp_str = nombre_archivo.split('_')[-1].replace('Z.png', '')

    datos_json = {
        "ciudad": "Corrientes Capital",
        "radar": radar_id,
        "timestamp_utc": timestamp_str,
        "analisis": {
            "pixel_x": x_corrientes,
            "pixel_y": y_corrientes,
            "color_rgb": {"r": r, "g": g, "b": b}
        },
        "alerta": {
            "nivel": nivel,
            "mensaje": alerta
        }
    }

    # Convertimos el diccionario a un string JSON formateado
    salida_json = json.dumps(datos_json, indent=4, ensure_ascii=False)
    
    print("\n Respuesta estructurada (JSON):")
    print(salida_json)

    # Opcional: Guardar el JSON en un archivo
    with open("ultima_alerta.json", "w", encoding="utf-8") as f:
        f.write(salida_json)

    import main
    
    # 6. Integración con el Bot (SAPH)
    # Mapeo de niveles numéricos a texto para el bot
    mapa_niveles = {0: "Despejado", 1: "Verde", 2: "Amarilla", 3: "Naranja", 4: "Roja"}
    
    print("\n🤖 Integrando con el Bot SAPH...")
    # Para probar la alerta en el Hackathon, si el nivel es 0 (Despejado), forzamos una alerta de prueba.
    es_prueba = False
    if nivel < 2:
        print("   (Como el cielo está despejado, simularemos una tormenta para poder probar el bot)")
        nivel = 4
        alerta = "ALERTA ROJA (SIMULACRO): Tormenta severa inminente detectada."
        es_prueba = True
        
    if nivel >= 2:
        payload_bot = {
            "intencion": "alerta_meteorologica",
            "entidades": {
                # Se asume "17 de agosto" por ser el barrio que usamos de prueba en Corrientes Capital
                "barrios_afectados": ["17 de agosto"], 
                "nivel_alerta": mapa_niveles.get(nivel, "Roja"),
                "mensaje": alerta
            }
        }
        print(f"🚀 Disparando broadcast a través del bot para el nivel {nivel}...")
        main.procesar_datos_llm(0, payload_bot)  # chat_id no importa en un broadcast
    else:
        print("🌤️ Condiciones normales. No se requiere enviar alerta.")

    return datos_json

if __name__ == '__main__':
    demo_alerta_corrientes()