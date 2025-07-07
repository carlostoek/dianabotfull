
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base
from config import DATABASE_URL

# --- Motor de Base de Datos Asíncrono ---
# Se utiliza `create_async_engine` para establecer la conexión con la base de datos
# de una manera que sea compatible con asyncio.
# `echo=True` es útil para depuración, ya que imprime las consultas SQL que se ejecutan.
# En producción, es recomendable desactivarlo.
async_engine = create_async_engine(DATABASE_URL, echo=True)

# --- Fábrica de Sesiones Asíncronas ---
# `async_sessionmaker` crea una "fábrica" que produce nuevas sesiones de base de datos
# cuando se le llama. Estas sesiones son el principal punto de entrada para
# interactuar con la base de datos (consultar, insertar, actualizar, eliminar).
# `expire_on_commit=False` previene que los objetos se "desconecten" de la sesión
# después de un commit, lo cual es útil en ciertos patrones de uso con asyncio.
async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)

async def create_tables():
    """
    Función asíncrona para crear todas las tablas definidas en los modelos.
    
    Se conecta al motor de la base de datos y utiliza los metadatos de `Base`
    para emitir las sentencias `CREATE TABLE` necesarias.
    Esta función se llama una vez al iniciar el bot para asegurar que el esquema
    de la base de datos esté listo.
    """
    async with async_engine.begin() as conn:
        # `conn.run_sync` ejecuta una función síncrona (como `Base.metadata.create_all`)
        # dentro del contexto asíncrono de la conexión.
        await conn.run_sync(Base.metadata.create_all)
