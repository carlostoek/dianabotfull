# run_seeds.py
import asyncio
from src.database.connection import get_db_session, init_db
from src.database.seeds import seed_initial_data

async def main():
    await init_db()
    session = await get_db_session()
    try:
        await seed_initial_data(session)
        print("Successfully seeded the database.")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
