import requests
import json
from datetime import datetime
import main 

def obtener_datos_open_meteo(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=precipitation,weather_code&timezone=America%2FSao_Paulo"
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        return respuesta.json()
    except Exception as e:
        print(f"❌ Error al consultar Open-Meteo: {e}")
        return None

def decodificar_alerta_wmo(weather_code, precipitacion):
    if weather_code in [95, 96, 99]:
        return 4, "ALERTA ROJA: Tormenta severa o granizo detectado."
    elif weather_code in [65, 82] or precipitacion > 10.0:
        return 3, "ALERTA NARANJA: Lluvia muy fuerte, posible anegamiento."
    elif weather_code in [61, 63, 80, 81] or precipitacion >= 2.0:
        return 2, "ALERTA AMARILLA: Lluvia moderada continua."
    elif weather_code in [51, 53, 55, 56, 57] or precipitacion > 0:
        return 1, "Llovizna o precipitación débil."
    else:
        return 0, "CIELO DESPEJADO: Condiciones hídricas normales."

def demo_alerta_corrientes():
    print("📡 Consultando datos meteorológicos en tiempo real vía Open-Meteo...")
    
    barrios_gps = {
        "Cambá Cuá": {"lat": -27.4623, "lon": -58.8415},
        "17 de Agosto": {"lat": -27.4981, "lon": -58.7903},
        "Molina Punta": {"lat": -27.4258, "lon": -58.7911},
        "Centro": {"lat": -27.4666, "lon": -58.8344}
    }

    resultados = {}
    barrios_en_alerta = []
    nivel_maximo_detectado = 0
    mensaje_alerta_principal = ""

    for nombre_barrio, coords in barrios_gps.items():
        datos = obtener_datos_open_meteo(coords["lat"], coords["lon"])
        
        if datos and "current" in datos:
            clima_actual = datos["current"]
            weather_code = clima_actual.get("weather_code", 0)
            precipitacion = clima_actual.get("precipitation", 0.0)
            
            nivel, alerta = decodificar_alerta_wmo(weather_code, precipitacion)
            
            print(f"   📍 {nombre_barrio}: Código {weather_code}, Lluvia: {precipitacion}mm -> {alerta}")
            
            resultados[nombre_barrio] = {
                "nivel": nivel,
                "alerta": alerta,
                "weather_code": weather_code,
                "precipitacion_mm": precipitacion
            }
            
            if nivel >= 2:
                barrios_en_alerta.append(nombre_barrio)
                if nivel > nivel_maximo_detectado:
                    nivel_maximo_detectado = nivel
                    mensaje_alerta_principal = alerta

    # 🔧 MODO PRUEBA
    if nivel_maximo_detectado < 2:
        print("\n🌤️ Condiciones normales. (Forzando simulacro para probar el sistema SAPH...)")
        barrios_en_alerta = ["17 de Agosto", "Molina Punta"]
        nivel_maximo_detectado = 4
        mensaje_alerta_principal = "ALERTA ROJA (SIMULACRO): Tormenta severa inminente detectada."

    # Guardado del JSON (ahora incluye los datos del simulacro si se activó)
    datos_json = {
        "timestamp": datetime.now().isoformat(),
        "fuente": "Open-Meteo API",
        "nivel_general": nivel_maximo_detectado,
        "mensaje_general": mensaje_alerta_principal if mensaje_alerta_principal else "Condiciones normales",
        "analisis_barrios": resultados
    }
    
    salida_json = json.dumps(datos_json, indent=4, ensure_ascii=False)
    print("\n📦 Respuesta estructurada (JSON):")
    print(salida_json)
    
    with open("ultima_alerta.json", "w", encoding="utf-8") as f:
        f.write(salida_json)

    # Integración con el Bot SAPH
    mapa_niveles = {0: "Despejado", 1: "Verde", 2: "Amarilla", 3: "Naranja", 4: "Roja"}
    
    if barrios_en_alerta:
        payload_bot = {
            "intencion": "alerta_meteorologica",
            "entidades": {
                "barrios_afectados": barrios_en_alerta, 
                "nivel_alerta": mapa_niveles.get(nivel_maximo_detectado, "Roja"),
                "mensaje": mensaje_alerta_principal
            }
        }
        print(f"\n🚀 Disparando broadcast a través del bot para el nivel {nivel_maximo_detectado}...")
        # main.procesar_datos_llm(0, payload_bot)

    return datos_json

if __name__ == '__main__':
    demo_alerta_corrientes()