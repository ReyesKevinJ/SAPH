import llm_client

textos = [
    "Hola, me llamo Juan Carlos y soy del barrio San Gerónimo. Anotame a las alertas por favor.",
    "Che te aviso que acá en San Gerónimo se cayó un poste de luz y la calle está anegada.",
    "Hola, ¿cómo estás?",
    "Me quiero registrar, soy María de La Boca."
]

for t in textos:
    print(f"\nTexto: '{t}'")
    resultado = llm_client.interpretar_texto(t)
    print("Resultado JSON:", resultado)
