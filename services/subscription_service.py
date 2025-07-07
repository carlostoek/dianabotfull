
import uuid
import datetime
from sqlalchemy.future import select

from database.database import async_session
from database.models import Tariff, InviteToken, Subscription, User

async def create_tariff(name: str, duration_days: int, price: float) -> Tariff:
    """
    Crea una nueva tarifa de suscripción en la base de datos.
    """
    async with async_session() as session:
        new_tariff = Tariff(
            name=name,
            duration_days=duration_days,
            price=price
        )
        session.add(new_tariff)
        await session.commit()
        return new_tariff

async def get_all_tariffs() -> list[Tariff]:
    """
    Obtiene todas las tarifas activas de la base de datos.
    """
    async with async_session() as session:
        result = await session.execute(select(Tariff).filter(Tariff.is_active == True))
        return result.scalars().all()

async def generate_invite_token(tariff_id: int, days_valid: int = 7) -> InviteToken:
    """
    Genera un nuevo token de invitación de un solo uso asociado a una tarifa.
    """
    async with async_session() as session:
        token_str = str(uuid.uuid4())
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)
        
        new_token = InviteToken(
            token=token_str,
            tariff_id=tariff_id,
            expires_at=expires_at
        )
        session.add(new_token)
        await session.commit()
        return new_token

async def validate_and_use_token(token_str: str, user: User) -> Subscription | None:
    """
    Valida un token, y si es correcto, crea una suscripción para el usuario.
    """
    async with async_session() as session:
        result = await session.execute(
            select(InviteToken).filter(
                InviteToken.token == token_str,
                InviteToken.is_used == False,
                InviteToken.expires_at > datetime.datetime.utcnow()
            )
        )
        token = result.scalars().first()

        if not token:
            return None  # Token inválido, expirado o ya usado

        # Marca el token como usado
        token.is_used = True

        # Crea la suscripción para el usuario
        tariff = await session.get(Tariff, token.tariff_id)
        end_date = datetime.datetime.utcnow() + datetime.timedelta(days=tariff.duration_days)

        new_subscription = Subscription(
            user_id=user.id,
            start_date=datetime.datetime.utcnow(),
            end_date=end_date,
            is_active=True
        )
        session.add(new_subscription)
        await session.commit()
        return new_subscription
