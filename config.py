
import os

# Cargar variables de entorno (solo para desarrollo local, Railway las inyecta directamente)
# from dotenv import load_dotenv
# load_dotenv()

# --- Configuración del Bot ---
# Token de Telegram. ¡NUNCA lo subas a un repositorio público!
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# --- Configuración de la Base de Datos ---
# URL de conexión a la base de datos.
# Para SQLite asíncrono, el formato es: "sqlite+aiosqlite:///nombre_de_la_base.db"
DATABASE_URL = "sqlite+aiosqlite:///dianabot.db"

# --- Configuración de Canales ---
# IDs de los canales. El bot debe ser administrador en ambos.
# Se recomienda usar variables de entorno para mantener la flexibilidad.
FREE_CHANNEL_ID = int(os.getenv("FREE_CHANNEL_ID")) if os.getenv("FREE_CHANNEL_ID") else None
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID")) if os.getenv("VIP_CHANNEL_ID") else None

# Delay en minutos antes de aceptar automáticamente una solicitud de unión al canal gratuito.
# Durante este tiempo, el bot enviará mensajes de promoción de redes sociales.
FREE_CHANNEL_JOIN_DELAY_MINUTES = int(os.getenv("FREE_CHANNEL_JOIN_DELAY_MINUTES", 5)) # 5 minutos por defecto

# --- Otras Configuraciones ---
# Lista de IDs de los administradores del bot.
# Pueden ejecutar comandos especiales y acceder a paneles de administración.
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "12345678").split(',')]
