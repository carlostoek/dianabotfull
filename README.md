Para desarrollar el sistema de 

### 1. Modelos de Gamificación

Ya hemos definido los modelos en el archivo `models.py`. Asegúrate de que estén correctamente implementados en tu base de datos. Aquí está el resumen de los modelos que se utilizarán:

```python
# database/models.py

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    besitos = Column(Integer, default=0)  # Moneda virtual
    last_daily_reward = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User ", back_populates="profile")

class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String, nullable=False)  # 'reaction', 'subscription', 'daily', etc.
    required_count = Column(Integer, default=1)  # Para misiones progresivas
    besitos_reward = Column(Integer, default=0)
    item_reward_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    
    channel_id = Column(BigInteger, ForeignKey('channels.channel_id'), nullable=True)
    channel = relationship("Channel", back_populates="missions")
    item_reward = relationship("Item")

class UserMission(Base):
    __tablename__ = 'user_missions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=False)
    progress = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User ", back_populates="missions")
    mission = relationship("Mission")

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(String, nullable=False)  # 'collectible', 'tool', 'clue', 'vip_access'
    rarity = Column(String, default='common')   # 'common', 'rare', 'epic', 'legendary'
    besitos_cost = Column(Integer, nullable=True)  # Costo en tienda
    effect = Column(JSON, nullable=True)  # Efectos especiales (ej: {"vip_days": 7})

class UserInventory(Base):
    __tablename__ = 'user_inventory'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, default=1)
    acquired_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User ", back_populates="inventory")
    item = relationship("Item")

class Trivia(Base):
    __tablename__ = 'trivias'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # Lista de opciones en formato JSON
    correct_index = Column(Integer, nullable=False)
    besitos_reward = Column(Integer, default=0)
    item_reward_id = Column(Integer, ForeignKey('items.id'), nullable=True)

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    condition_type = Column(String, nullable=False)  # 'besitos_total', 'missions_completed', etc.
    condition_value = Column(Integer, nullable=False)
    besitos_reward = Column(Integer, default=0)
    item_reward_id = Column(Integer, ForeignKey('items.id'), nullable=True)

class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User ", back_populates="achievements")
    achievement = relationship("Achievement")

class Auction(Base):
    __tablename__ = 'auctions'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, default=1)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default='active')  # 'active', 'completed', 'canceled'
    
    item = relationship("Item")
    bids = relationship("Bid", back_populates="auction")

class Bid(Base):
    __tablename__ = 'bids'
    
    id = Column(Integer, primary_key=True)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer, nullable=False)  # Cantidad de besitos
    bid_time = Column(DateTime, default=datetime.datetime.utcnow)
    
    auction = relationship("Auction", back_populates="bids")
    user = relationship("User ", back_populates="bids")
```

### 2. Servicios de Gamificación

Crea un archivo `gamification_service.py` en la carpeta `services` para manejar la lógica de gamificación.

```python
# telegram_subscription_bot/services/gamification_service.py
from sqlalchemy import select, update
from database.db import get_session
from database.models import UserProfile, UserMission, Mission, UserInventory, Item, UserAchievement, Auction, Bid

class GamificationService:
    @staticmethod
    async def award_besitos(user_id, amount):
        async with get_session() as session:
            profile = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            user_profile = profile.scalar_one_or_none()
            
            if user_profile:
                user_profile.besitos += amount
                await session.commit()
    
    @staticmethod
    async def unlock_mission(user_id, mission_name):
        async with get_session() as session:
            mission = await session.execute(select(Mission).where(Mission.name == mission_name))
            mission = mission.scalar_one_or_none()
            
            if mission:
                user_mission = UserMission(user_id=user_id, mission_id=mission.id)
                session.add(user_mission)
                await session.commit()
    
    @staticmethod
    async def record_reaction(user_id, post_id, emoji):
        # Lógica para registrar reacciones y otorgar puntos
        # Aquí puedes definir qué emoji otorga cuántos besitos
        emoji_besitos = {
            "👍": 5,
            "❤️": 10,
            "😂": 3,
            "😮": 7,
            "😢": 2,
            "👎": 1
        }
        
        if emoji in emoji_besitos:
            await GamificationService.award_besitos(user_id, emoji_besitos[emoji])
            # Aquí puedes actualizar el progreso de misiones relacionadas con reacciones
            await GamificationService.update_mission_progress(user_id, "reaction_collector")
    
    @staticmethod
    async def get_shop_items():
        async with get_session() as session:
            items = await session.execute(select(Item))
            return items.scalars().all()
    
    @staticmethod
    async def award_daily_reward(user_id):
        async with get_session() as session:
            profile = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            user_profile = profile.scalar_one_or_none()
            
            if user_profile and (user_profile.last_daily_reward is None or user_profile.last_daily_reward < datetime.datetime.utcnow() - datetime.timedelta(days=1)):
                await GamificationService.award_besitos(user_id, 50)  # Ejemplo de recompensa diaria
                user_profile.last_daily_reward = datetime.datetime.utcnow()
                await session.commit()
    
    @staticmethod
    async def is_eligible_for_daily_reward(user_id):
        async with get_session() as session:
            profile = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            user_profile = profile.scalar_one_or_none()
            if user_profile:
                return user_profile.last_daily_reward is None or user_profile.last_daily_reward < datetime.datetime.utcnow() - datetime.timedelta(days=1)
            return False
    
    @staticmethod
    async def update_mission_progress(user_id, mission_name):
        async with get_session() as session:
            mission = await session.execute(select(Mission).where(Mission.name == mission_name))
            mission = mission.scalar_one_or_none()
            
            if mission:
                user_mission = await session.execute(select(UserMission).where(UserMission.user_id == user_id, UserMission.mission_id == mission.id))
                user_mission = user_mission.scalar_one_or_none()
                
                if user_mission:
                    user_mission.progress += 1
                    if user_mission.progress >= mission.required_count:
                        user_mission.is_completed = True
                        user_mission.completed_at = datetime.datetime.utcnow()
                        await GamificationService.award_besitos(user_id, mission.besitos_reward)
                        # Aquí puedes agregar lógica para otorgar el ítem de recompensa
                else:
                    new_user_mission = UserMission(user_id=user_id, mission_id=mission.id, progress=1)
                    session.add(new_user_mission)
                
                await session.commit()
```

### 3. Handlers de Gamificación

Crea un archivo `gamification_handlers.py` en la carpeta `handlers` para manejar los comandos relacionados con la gamificación.

```python
# telegram_subscription_bot/handlers/gamification_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from services.gamification_service import GamificationService
from keyboards.gamification_keyboards import get_gamification_menu

router = Router()

@router.message(Command("gamification"))
async def gamification_command(message: Message):
    await message.answer(
        "🎮 Bienvenido al sistema de Gamificación\n\n"
        "Selecciona una opción:",
        reply_markup=get_gamification_menu()
    )

@router.callback_query(F.data == "check_besitos")
async def check_besitos(callback: CallbackQuery):
    user_id = callback.from_user.id
    profile = await GamificationService.get_user_profile(user_id)
    
    await callback.answer(f"Tienes {profile.besitos} besitos.")

@router.callback_query(F.data == "shop")
async def shop_command(callback: CallbackQuery):
    items = await GamificationService.get_shop_items()
    # Lógica para mostrar la tienda
    await callback.answer("Aquí está la tienda.")
```

### 4. Teclados de Gamificación

Crea un archivo `gamification_keyboards.py` en la carpeta `keyboards` para definir los teclados interactivos relacionados con la gamificación.

```python
# telegram_subscription_bot/keyboards/gamification_keyboards.py
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_gamification_menu():
    builder = InlineKeyboardBuilder()
    
    builder.button(text="💰 Ver Besitos", callback_data="check_besitos")
    builder.button(text="🏪 Tienda", callback_data="shop")
    builder.button(text="🎯 Misiones", callback_data="missions")
    builder.button(text="🏆 Logros", callback_data="achievements")
    
    builder.adjust(1)  # Una columna
    return builder.as_markup()
```

### 5. Integración con el Sistema de Administración de Canales

Asegúrate de que las acciones que los usuarios realicen en los canales (como reaccionar a mensajes) se registren y se reflejen en su saldo de besitos. Esto se puede hacer en los handlers de los mensajes del canal, donde se puede llamar a los métodos del `GamificationService` para otorgar puntos.

### Ejemplo de Integración

```python
# handlers/channel_handlers.py
from services.gamification_service import GamificationService

@router.callback_query(F.data.startswith("reaction_"))
async def handle_reaction(callback: CallbackQuery):
    user_id = callback.from_user.id
    post_id = callback.data.split("_")[1]
    
    # Lógica para manejar la reacción
    await GamificationService.record_reaction(user_id, post_id, callback.data)
```

### 6. Implementación de Misiones, Tienda, Subastas y Trivias

Para implementar las funcionalidades de misiones, tienda, subastas y trivias, se necesitarán más handlers y servicios. Aquí hay un esquema básico de cómo podrías estructurarlos:

#### Misiones

```python
# telegram_subscription_bot/services/mission_service.py
class MissionService:
    @staticmethod
    async def get_user_missions(user_id):
        async with get_session() as session:
            missions = await session.execute(select(UserMission).where(UserMission.user_id == user_id))
            return missions.scalars().all()
```

#### Tienda

```python
# telegram_subscription_bot/services/inventory_service.py
class InventoryService:
    @staticmethod
    async def purchase_item(user_id, item_id):
        async with get_session() as session:
            # Lógica para comprar un ítem
            pass
```

#### Subastas

```python
# telegram_subscription_bot/services/auction_service.py
class AuctionService:
    @staticmethod
    async def create_auction(item_id, duration):
        async with get_session() as session:
            # Lógica para crear una subasta
            pass
```

#### Trivias

```python
# telegram_subscription_bot/services/trivia_service.py
class TriviaService:
    @staticmethod
    async def get_trivia():
        async with get_session() as session:
            # Lógica para obtener trivias
            pass
```

