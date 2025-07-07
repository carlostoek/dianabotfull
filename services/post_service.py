from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.database import async_session
from database.models import Post, PostButton, PostReaction
import datetime

async def create_post(
    channel_id: int,
    message_text: str = None,
    media_type: str = None,
    media_file_id: str = None,
    is_protected: bool = False,
    scheduled_time: datetime.datetime = None,
    buttons_data: list[dict] = None,
    reactions_data: list[str] = None
) -> Post:
    """
    Crea una nueva publicación en la base de datos.
    """
    async with async_session() as session:
        new_post = Post(
            channel_id=channel_id,
            message_text=message_text,
            media_type=media_type,
            media_file_id=media_file_id,
            is_protected=is_protected,
            scheduled_time=scheduled_time
        )
        session.add(new_post)
        await session.flush() # Para obtener el ID del post antes del commit

        if buttons_data:
            for btn_data in buttons_data:
                new_button = PostButton(
                    post_id=new_post.id,
                    text=btn_data['text'],
                    url=btn_data.get('url'),
                    callback_data=btn_data.get('callback_data'),
                    row_order=btn_data.get('row_order', 0),
                    button_order=btn_data.get('button_order', 0)
                )
                session.add(new_button)
        
        if reactions_data:
            for emoji in reactions_data:
                new_reaction = PostReaction(
                    post_id=new_post.id,
                    emoji=emoji
                )
                session.add(new_reaction)

        await session.commit()
        return new_post

async def get_post_by_id(post_id: int) -> Post | None:
    """
    Obtiene una publicación por su ID, incluyendo sus botones y reacciones.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Post)
            .options(selectinload(Post.buttons), selectinload(Post.reactions))
            .filter(Post.id == post_id)
        )
        return result.scalars().first()

async def get_scheduled_posts_to_send() -> list[Post]:
    """
    Obtiene todas las publicaciones programadas que deben ser enviadas ahora.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Post)
            .options(selectinload(Post.buttons), selectinload(Post.reactions))
            .filter(
                Post.is_sent == False,
                Post.scheduled_time <= datetime.datetime.utcnow()
            )
        )
        return result.scalars().all()

async def mark_post_as_sent(post_id: int) -> None:
    """
    Marca una publicación como enviada.
    """
    async with async_session() as session:
        post = await session.get(Post, post_id)
        if post:
            post.is_sent = True
            await session.commit()

async def delete_post(post_id: int) -> bool:
    """
    Elimina una publicación y sus elementos asociados (botones, reacciones).
    """
    async with async_session() as session:
        post = await session.get(Post, post_id)
        if post:
            await session.delete(post)
            await session.commit()
            return True
        return False

async def get_all_posts() -> list[Post]:
    """
    Obtiene todas las publicaciones de la base de datos.
    """
    async with async_session() as session:
        result = await session.execute(select(Post).options(selectinload(Post.buttons), selectinload(Post.reactions)))
        return result.scalars().all()

async def update_post(post_id: int, **kwargs) -> Post | None:
    """
    Actualiza los campos de una publicación existente.
    """
    async with async_session() as session:
        post = await session.get(Post, post_id)
        if post:
            for key, value in kwargs.items():
                setattr(post, key, value)
            await session.commit()
            return post
        return None