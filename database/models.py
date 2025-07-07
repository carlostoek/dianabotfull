
from sqlalchemy import (
    create_engine, Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey, Float
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import datetime

# --- Base Declarativa ---
# La base que usarán todos nuestros modelos ORM.
Base = declarative_base()

# --- Modelos de la Aplicación ---

class User(Base):
    """
    Representa a un usuario del bot en la base de datos.

    Almacena información básica de Telegram y el estado del usuario en el sistema.
    """
    __tablename__ = 'users'

    # --- Columnas ---
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # --- Relaciones ---
    # Un usuario puede tener una suscripción activa.
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, first_name='{self.first_name}')>"

class Subscription(Base):
    """
    Representa la suscripción de un usuario al canal VIP.

    Controla el estado, la duración y la vigencia de la membresía de un usuario.
    """
    __tablename__ = 'subscriptions'

    # --- Columnas ---
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # --- Relaciones ---
    # Cada suscripción pertenece a un único usuario.
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, end_date={self.end_date}, is_active={self.is_active})>"

class Channel(Base):
    """
    Almacena la configuración de los canales gestionados por el bot.

    Permite al administrador configurar los IDs de los canales directamente
    desde la base de datos o un panel, en lugar de hardcodearlos.
    """
    __tablename__ = 'channels'

    # --- Columnas ---
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Ej: "free_channel", "vip_channel"
    channel_id = Column(BigInteger, unique=True, nullable=False)
    access_type = Column(String, default='free') # Tipos: 'free', 'request', 'restricted'
    join_delay_minutes = Column(Integer, default=0) # Delay en minutos para solicitudes de unión (solo para 'request')

    def __repr__(self):
        return f"<Channel(name='{self.name}', channel_id={self.channel_id})>"

class Tariff(Base):
    """
    Representa una tarifa de suscripción configurable por el administrador.

    Define la duración, el precio y el nombre de un plan de suscripción
    que se puede ofrecer a los usuarios.
    """
    __tablename__ = 'tariffs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    duration_days = Column(Integer, nullable=False)  # Duración en días
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

    tokens = relationship("InviteToken", back_populates="tariff")

    def __repr__(self):
        return f"<Tariff(name='{self.name}', duration_days={self.duration_days}, price={self.price})>"

class InviteToken(Base):
    """
    Representa un token de invitación de un solo uso para acceder al canal VIP.

    Cada token está asociado a una tarifa y tiene una fecha de expiración.
    Se utiliza para generar los enlaces de invitación personalizados.
    """
    __tablename__ = 'invite_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)
    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=False)
    
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    tariff = relationship("Tariff", back_populates="tokens")

    def __repr__(self):
        return f"<InviteToken(token='{self.token}', tariff_id={self.tariff_id}, is_used={self.is_used})>"

class JoinRequest(Base):
    """
    Representa una solicitud pendiente de unión a un canal.

    Utilizado para gestionar el delay configurable antes de aceptar
    automáticamente a un usuario en un canal.
    """
    __tablename__ = 'join_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False) # Telegram ID del usuario
    chat_id = Column(BigInteger, nullable=False) # ID del canal al que solicita unirse
    request_date = Column(DateTime, default=datetime.datetime.utcnow)
    accept_date = Column(DateTime, nullable=True) # Fecha en la que debe ser aceptado
    is_accepted = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<JoinRequest(user_id={self.user_id}, chat_id={self.chat_id}, accept_date={self.accept_date})>"

class Post(Base):
    """
    Representa una publicación que el bot enviará a un canal.

    Puede incluir texto, medios, botones inline, reacciones y ser programada.
    """
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)  # ID del canal de Telegram
    message_text = Column(String, nullable=True)
    media_type = Column(String, nullable=True)  # 'photo', 'video', 'document', 'sticker', 'animation'
    media_file_id = Column(String, nullable=True) # file_id de Telegram
    is_protected = Column(Boolean, default=False) # Si el mensaje no puede ser reenviado
    scheduled_time = Column(DateTime, nullable=True) # Para publicaciones programadas
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    buttons = relationship("PostButton", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("PostReaction", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, channel_id={self.channel_id}, scheduled_time={self.scheduled_time}, is_sent={self.is_sent})>"

class PostButton(Base):
    """
    Representa un botón inline asociado a una publicación.
    """
    __tablename__ = 'post_buttons'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    text = Column(String, nullable=False)
    url = Column(String, nullable=True)
    callback_data = Column(String, nullable=True)
    row_order = Column(Integer, nullable=False) # Orden de la fila del botón
    button_order = Column(Integer, nullable=False) # Orden del botón dentro de la fila

    post = relationship("Post", back_populates="buttons")

    def __repr__(self):
        return f"<PostButton(id={self.id}, text='{self.text}', post_id={self.post_id})>"

class PostReaction(Base):
    """
    Representa una reacción personalizada asociada a una publicación.
    """
    __tablename__ = 'post_reactions'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    emoji = Column(String, nullable=False) # Emoji de la reacción

    post = relationship("Post", back_populates="reactions")

    def __repr__(self):
        return f"<PostReaction(id={self.id}, emoji='{self.emoji}', post_id={self.post_id})>"

# --- Nota sobre la Creación de Tablas ---
# La creación de las tablas en la base de datos se gestionará de forma asíncrona
# en el script principal (main.py) al iniciar el bot para asegurar que existan
# antes de que el bot empiece a procesar actualizaciones.
