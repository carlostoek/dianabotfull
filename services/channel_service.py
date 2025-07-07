
import datetime
from sqlalchemy.future import select

from database.database import async_session
from database.models import Channel, JoinRequest

async def get_channel_by_id(channel_id: int) -> Channel | None:
    """
    Obtiene la configuración de un canal por su ID de Telegram.
    """
    async with async_session() as session:
        result = await session.execute(select(Channel).filter(Channel.channel_id == channel_id))
        return result.scalars().first()

async def get_channel_by_name(name: str) -> Channel | None:
    """
    Obtiene la configuración de un canal por su nombre.
    """
    async with async_session() as session:
        result = await session.execute(select(Channel).filter(Channel.name == name))
        return result.scalars().first()

async def create_or_update_channel(
    name: str, 
    channel_id: int, 
    access_type: str = 'free', 
    join_delay_minutes: int = 0
) -> Channel:
    """
    Crea o actualiza la configuración de un canal.
    """
    async with async_session() as session:
        channel = await get_channel_by_name(name)
        if channel:
            channel.channel_id = channel_id
            channel.access_type = access_type
            channel.join_delay_minutes = join_delay_minutes
        else:
            channel = Channel(
                name=name,
                channel_id=channel_id,
                access_type=access_type,
                join_delay_minutes=join_delay_minutes
            )
            session.add(channel)
        await session.commit()
        return channel

async def create_join_request(user_id: int, chat_id: int, delay_minutes: int) -> JoinRequest:
    """
    Crea una nueva solicitud de unión pendiente en la base de datos.
    """
    async with async_session() as session:
        accept_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=delay_minutes)
        new_request = JoinRequest(
            user_id=user_id,
            chat_id=chat_id,
            accept_date=accept_date
        )
        session.add(new_request)
        await session.commit()
        return new_request

async def get_pending_join_requests() -> list[JoinRequest]:
    """
    Obtiene todas las solicitudes de unión pendientes que ya deberían ser aceptadas.
    """
    async with async_session() as session:
        result = await session.execute(
            select(JoinRequest).filter(
                JoinRequest.is_processed == False,
                JoinRequest.accept_date <= datetime.datetime.utcnow()
            )
        )
        return result.scalars().all()

async def mark_join_request_processed(request_id: int, accepted: bool) -> None:
    """
    Marca una solicitud de unión como procesada y si fue aceptada o no.
    """
    async with async_session() as session:
        request = await session.get(JoinRequest, request_id)
        if request:
            request.is_processed = True
            request.is_accepted = accepted
            await session.commit()
