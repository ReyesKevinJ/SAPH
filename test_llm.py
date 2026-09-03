import main

chat_id_prueba = 1308284715 # Tu ID real de Telegram (Tobias)

# 1. Probar un registro simulado desde un LLM
json_registro = {
    "intencion": "registro",
    "entidades": {
        "nombre": "Tobias",
        "barrio": "17 de agosto"
    }
}
print("Simulando LLM - Registro...")
main.procesar_datos_llm(chat_id_prueba, json_registro)

# 2. Probar un reporte simulado desde un LLM
json_reporte = {
    "intencion": "reporte",
    "entidades": {
        "tipo_problema": "Calle inundada",
        # Al no mandar barrio, debería tomar el del registro
    }
}
print("\nSimulando LLM - Reporte...")
main.procesar_datos_llm(chat_id_prueba, json_reporte)

# 3. Probar alerta automática proveniente del radar del SMN (Todos los niveles)
niveles_prueba = [
    ("Despejado", "Cielo claro, sin novedades."),
    ("Verde", "Ligera nubosidad, todo normal."),
    ("Amarilla", "Lluvias moderadas, sin riesgo inmediato."),
    ("Naranja", "Lluvias fuertes, posible anegamiento."),
    ("Roja", "Peligro inminente, precaución máxima.")
]

for nivel, msj in niveles_prueba:
    json_alerta_smn = {
        "intencion": "alerta_meteorologica",
        "entidades": {
            "barrios_afectados": ["17 de agosto"],
            "nivel_alerta": nivel,
            "mensaje": msj
        }
    }
    print(f"\nSimulando Radar SMN - Nivel {nivel}...")
    main.procesar_datos_llm(chat_id_prueba, json_alerta_smn)

print("\n¡Pruebas enviadas! Si tu bot está corriendo, también deberías haber recibido los mensajes de respuesta en Telegram.")
