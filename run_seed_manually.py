import asyncio
from dotenv import load_dotenv
import os
from src.database.connection import get_db_session, init_db
from src.database.seeds import seed_initial_data

# Cargar variables de entorno desde .env
load_dotenv()

async def main():
    print("Inicializando la base de datos...")
    await init_db() # Asegura que las tablas existan
    print("Base de datos inicializada.")

    print("Iniciando el proceso de siembra de datos...")
    async for session in get_db_session():
        try:
            await seed_initial_data(session)
            print("Datos sembrados exitosamente.")
        except Exception as e:
            print(f"Error al sembrar los datos: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(main())