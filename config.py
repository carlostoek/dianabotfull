
import os

# Cargar variables de entorno desde un archivo .env para desarrollo local
from dotenv import load_dotenv
load_dotenv()

# --- Configuración del Bot ---
# Token de Telegram. ¡NUNCA lo subas a un repositorio público!
BOT_TOKEN = os.getenv("BOT_TOKEN", "Y7997978902:AAGEGQVfpGpiiLXaAP7oR81rbrAx2RBwONQ")

# --- Configuración de la Base de Datos ---
# URL de conexión a la base de datos.
# Para SQLite asíncrono, el formato es: "sqlite+aiosqlite:///nombre_de_la_base.db"
DATABASE_URL = "sqlite+aiosqlite:///dianabot.db"

# --- Configuración de Canales ---
# IDs de los canales. El bot debe ser administrador en ambos.
# Se recomienda usar variables de entorno para mantener la flexibilidad.
FREE_CHANNEL_ID = os.getenv("FREE_CHANNEL_ID", -1001234567890)  # Reemplazar con el ID real
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID", -1001234567891)    # Reemplazar con el ID real

# --- Otras Configuraciones ---
# Lista de IDs de los administradores del bot.
# Pueden ejecutar comandos especiales y acceder a paneles de administración.
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "12345678").split(',')]
