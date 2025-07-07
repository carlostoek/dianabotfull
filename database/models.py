
from sqlalchemy import (
    create_engine, Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey
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

    def __repr__(self):
        return f"<Channel(name='{self.name}', channel_id={self.channel_id})>"

# --- Nota sobre la Creación de Tablas ---
# La creación de las tablas en la base de datos se gestionará de forma asíncrona
# en el script principal (main.py) al iniciar el bot para asegurar que existan
# antes de que el bot empiece a procesar actualizaciones.
