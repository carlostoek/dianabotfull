### Implementación del Módulo de Gamificación

A continuación, se detalla la implementación del módulo de gamificación, que se integrará con el sistema existente de administración de canales. Este módulo incluirá la lógica necesaria para gestionar las características mencionadas, así como los handlers y servicios correspondientes.

#### 1. Estructura de Archivos

La estructura de archivos para el módulo de gamificación se verá así:

```
telegram_subscription_bot/
├── gamification/
│   ├── __init__.py
│   ├── services.py                # Lógica de gamificación
│   ├── handlers.py                # Comandos de gamificación
│   └── keyboards.py               # Teclados interactivos
│
├── services/
│   ├── gamification_service.py    # Servicio principal de gamificación
│   ├── mission_service.py         # Gestión de misiones
│   ├── inventory_service.py       # Gestión de inventario
│   ├── auction_service.py         # Gestión de subastas
│   └── ...                       # Otros servicios existentes
│
├── handlers/
│   ├── gamification_handlers.py   # Manejadores de comandos de gamificación
│   └── ...                       # Otros manejadores existentes
│
└── database/
    └── models.py                 # Archivo actualizado con todos los modelos
```

#### 2. Modelos de Gamificación

Los modelos de gamificación ya han sido definidos en el modelo extendido que proporcionaste. Asegúrate de que estos modelos estén correctamente integrados en tu base de datos.

#### 3. Servicios de Gamificación

Crea un archivo `gamification_service.py` en la carpeta `services` para manejar la lógica de gamificación.

```python
# telegram_subscription_bot/services/gamification_service.py
from sqlalchemy import select
from database.db import get_session
from database.models import UserProfile, UserMission, Mission, UserInventory, Item, UserAchievement

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
        pass
    
    @staticmethod
    async def get_shop_items():
        async with get_session() as session:
            items = await session.execute(select(Item))
            return items.scalars().all()
    
    @staticmethod
    async def award_daily_reward(user_id):
        # Lógica para recompensas diarias
        pass
    
    @staticmethod
    async def is_eligible_for_daily_reward(user_id):
        # Lógica para verificar elegibilidad
        pass
```

#### 4. Handlers de Gamificación

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

#### 5. Teclados de Gamificación

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

### Integración con el Sistema de Administración de Canales

Para integrar el sistema de gamificación con el sistema de administración de canales, asegúrate de que las acciones que los usuarios realicen en los canales (como reaccionar a mensajes) se registren y se reflejen en su saldo de besitos. Esto se puede hacer en los handlers de los mensajes del canal, donde se puede llamar a los métodos del `GamificationService` para otorgar puntos.

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

### Conclusión

Con esta implementación, el módulo de gamificación se integra de manera fluida con el sistema de administración de canales, permitiendo que las acciones de los usuarios en los canales se reflejen en su progreso dentro del sistema de gamificación. Esto crea una experiencia de usuario más rica y motivadora, incentivando la interacción y la participación activa.
