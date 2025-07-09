# src/database/seeds.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Mission, Achievement
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

async def seed_initial_data(session: AsyncSession):
    missions = [
        {'name': 'Daily Login', 'description': 'Inicia sesión cada día para ganar puntos.', 'reward_points': 10},
        {'name': 'Primer Mensaje', 'description': 'Envía tu primer mensaje al bot.', 'reward_points': 5},
    ]

    achievements = [
        {'name': 'Madrugador', 'description': 'Inicia sesión por primera vez.'},
        {'name': 'Explorador', 'description': 'Descubre una función oculta.'},
    ]

    for mission_data in missions:
        stmt = insert(Mission).values(**mission_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['name'],
            set_=dict(description=stmt.excluded.description, reward_points=stmt.excluded.reward_points)
        )
        await session.execute(stmt)

    for achievement_data in achievements:
        stmt = insert(Achievement).values(**achievement_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['name'],
            set_=dict(description=stmt.excluded.description)
        )
        await session.execute(stmt)

    await session.commit()
