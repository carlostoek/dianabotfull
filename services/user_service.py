
from sqlalchemy.future import select
from database.database import async_session
from database.models import User

async def get_or_create_user(telegram_id: int, first_name: str, last_name: str = None, username: str = None) -> User:
    """
    Obtiene un usuario de la base de datos si existe; de lo contrario, lo crea.

    Esta función es clave para registrar a todos los que interactúan con el bot
    o se unen a los canales.
    """
    async with async_session() as session:
        # Busca al usuario por su ID de Telegram.
        result = await session.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalars().first()

        if user:
            # Si el usuario existe, actualiza su información por si ha cambiado.
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.is_banned = False  # Si vuelve a unirse, se le quita el baneo.
        else:
            # Si no existe, crea una nueva instancia de usuario.
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
            session.add(user)
        
        await session.commit()
        return user

async def ban_user(telegram_id: int) -> User:
    """
    Marca a un usuario como baneado en la base de datos.

    Esto no lo expulsa de Telegram, sino que es una marca interna para
    saber que el usuario abandonó el canal.
    """
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalars().first()

        if user:
            user.is_banned = True
            await session.commit()
        
        return user
