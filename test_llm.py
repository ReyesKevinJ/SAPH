import main

chat_id_prueba = 1308284715 # Tu ID real de Telegram (Tobias)

# 1. Probar un registro simulado desde un LLM
json_registro = {
    "intencion": "registro",
    "entidades": {
        "nombre": "Ana LLM",
        "barrio": "La Boca"
    }
}
print("Simulando LLM - Registro...")
main.procesar_datos_llm(chat_id_prueba, json_registro)

# 2. Probar un reporte simulado desde un LLM
json_reporte = {
    "intencion": "reporte",
    "entidades": {
        "tipo_problema": "Calle inundada",
        # Al no mandar barrio, debería tomar el del registro ("La Boca")
    }
}
print("\nSimulando LLM - Reporte...")
main.procesar_datos_llm(chat_id_prueba, json_reporte)

print("\n¡Pruebas enviadas! Si tu bot está corriendo, también deberías haber recibido los mensajes de respuesta en Telegram.")
