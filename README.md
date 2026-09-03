# SAPH - Sistema de Alerta Temprana de Inundaciones 🌧️

SAPH es un bot de Telegram diseñado para alertar a los ciudadanos de Corrientes (y otras ciudades) sobre posibles inundaciones y condiciones meteorológicas severas, segmentadas por barrio. Además, permite a los usuarios enviar reportes ciudadanos sobre problemas en su zona (calles inundadas, árboles caídos, etc.).

## 🚀 Características

- **Registro de usuarios por barrio:** Los usuarios se registran mediante un menú numerado para recibir notificaciones específicas de su zona.
- **Alertas Meteorológicas Segmentadas:** Integración con la API de Open-Meteo para obtener datos meteorológicos y precipitación en tiempo real de diferentes coordenadas.
- **Código de Colores y Emojis:** Las alertas se clasifican en 5 niveles (de Despejado a Roja) usando emojis visuales (🔵, 🟢, 🟡, 🟠, 🔴) dependiendo de la gravedad.
- **Broadcast de Notificaciones:** Script especializado para leer un archivo JSON con los datos del clima y notificar instantáneamente a los usuarios de los barrios afectados.
- **Reportes Ciudadanos:** Los usuarios pueden reportar incidentes en la vía pública (anegamientos, granizo, etc.), los cuales quedan registrados en la base de datos de la administración.

## 📋 Requisitos Previos

Asegúrate de tener instalado **Python 3.8+** en tu sistema.

## 🛠️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/ReyesKevinJ/SAPH.git
   cd SAPH
   ```

2. **Instalar las dependencias:**
   Se recomienda usar un entorno virtual. Ejecuta:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar las variables de entorno:**
   Copia el archivo de ejemplo y crea tu propio `.env`:
   ```bash
   cp .env.example .env
   ```
   Abre el archivo `.env` y configura tus claves:
   ```env
   TELEGRAM_TOKEN=tu_token_aqui_obtenido_de_BotFather
   ADMIN_IDS=123456789,987654321
   ```

## 🎮 Guía de Uso

Para comenzar a interactuar con el bot en Telegram, búscalo por su usuario: **[@SAPH_Meteorologico_Bot](https://t.me/SAPH_Meteorologico_Bot)** y envíale el comando `/start`.

El sistema consta de múltiples módulos que funcionan en conjunto:

### 1. Iniciar el Bot de Telegram
Este script levanta el bot para que escuche comandos de los usuarios (`/start`, `/reportar`, `/estado`).
```bash
python main.py
```

### 2. Generar Datos Meteorológicos
Consulta la API de Open-Meteo y evalúa las condiciones climáticas de cada barrio. El resultado se guarda en un archivo llamado `ultima_alerta.json`.
```bash
python alerta_corrientes.py
```

### 3. Enviar Alertas a los Usuarios
Lee el archivo `ultima_alerta.json` generado en el paso anterior y envía mensajes push por Telegram a todos los usuarios, añadiendo el emoji y nivel correspondiente a su barrio.
```bash
python enviar_alertas_json.py
```

### 4. Administrar la Base de Datos
Puedes visualizar los usuarios registrados y los reportes almacenados en SQLite utilizando el script de lectura:
```bash
python leer_db.py
```

## 🧪 Pruebas (Tests)

El proyecto incluye tests unitarios para validar tanto el flujo de guardado y reporte (`test_main.py`) como la lógica de envío segmentado de alertas (`test_envio_alertas.py`).

Para correr todos los tests, usa:
```bash
python -m unittest discover tests
```

## 📂 Estructura del Proyecto

- `main.py` - Script principal y manejador (handlers) del Bot de Telegram.
- `alerta_corrientes.py` - Cliente de la API de clima (Open-Meteo) y generador de JSON.
- `enviar_alertas_json.py` - Script de envío (Broadcast) de notificaciones segmentadas.
- `db_manager.py` - Gestor de la base de datos SQLite (`alertas.db`).
- `leer_db.py` - Herramienta de consola para leer registros de la DB.
- `tests/` - Carpeta que contiene las pruebas unitarias.
- `ultima_alerta.json` - Archivo caché generado con el estado hídrico de los barrios.

## ☁️ Despliegue en la Nube (Gratis)

El bot está preparado para ser alojado de forma 100% gratuita en **Render** como un Web Service continuo.

1. **En Render:** Crea un "Web Service", conecta este repositorio y asegúrate de configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Environment Variables:** Añade `TELEGRAM_TOKEN` y `ADMIN_IDS`.
2. **En UptimeRobot:** Para evitar que el plan gratuito de Render entre en hibernación, crea un monitor HTTP(s) que haga ping cada 10 minutos a la URL pública asignada por Render (ej. `https://tu-app.onrender.com`). El bot incorpora un servidor web oculto para responder automáticamente a estos pings.
