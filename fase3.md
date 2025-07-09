Perfecto, con esta información puedo desarrollar la Fase 3. Basándome en las respuestas, aquí está mi plan de implementación:

## **Plan de Implementación - Fase 3**

### **1. Estructura de Archivos a Crear**

```
src/
├── services/
│   ├── story_service.py
│   └── persona_service.py
├── telegram_bot/
│   ├── handlers/
│   │   └── story_handler.py
│   └── states/
│       └── story_states.py
├── data/
│   └── story.json
└── utils/
    └── story_formatter.py

tests/
├── integration/
│   └── test_full_flow.py
└── unit/
    ├── test_story_service.py
    └── test_persona_service.py
```

### **2. Implementación Propuesta**

#### **A. Story Service (Tarea 3.1)**

```python
# src/services/story_service.py
import json
from typing import Dict, Optional, List
from pathlib import Path

class StoryService:
    def __init__(self, story_file_path: str = "src/data/story.json"):
        self.story_data = self._load_story_json(story_file_path)
        self.current_sessions = {}  # user_id -> current_scene_id
    
    def _load_story_json(self, file_path: str) -> Dict:
        """Carga el archivo story.json"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def get_scene(self, scene_id: str) -> Optional[Dict]:
        """Obtiene una escena específica"""
        return self.story_data.get(scene_id)
    
    async def start_story(self, user_id: int, level: int = 1) -> Dict:
        """Inicia la historia para un usuario"""
        start_scene_id = f"level_{level}_intro"
        self.current_sessions[user_id] = start_scene_id
        return await self.get_scene(start_scene_id)
    
    async def process_choice(self, user_id: int, choice_id: str) -> Dict:
        """Procesa la elección del usuario y retorna la siguiente escena"""
        current_scene_id = self.current_sessions.get(user_id)
        if not current_scene_id:
            raise ValueError("No hay sesión activa para este usuario")
        
        current_scene = await self.get_scene(current_scene_id)
        
        # Buscar la elección seleccionada
        for choice in current_scene.get('choices', []):
            if choice['id'] == choice_id:
                next_scene_id = choice['next_scene']
                self.current_sessions[user_id] = next_scene_id
                
                return {
                    'next_scene': await self.get_scene(next_scene_id),
                    'impact': choice.get('impact', {}),
                    'choice_made': choice
                }
        
        raise ValueError(f"Elección {choice_id} no válida para la escena {current_scene_id}")
```

#### **B. Persona Service (Tarea 3.2)**

```python
# src/services/persona_service.py
from typing import Dict, List, Optional
from src.database.repository import UserProgressRepository

class PersonaService:
    # Matriz de transición de estados
    STATE_TRANSITIONS = {
        "enigmática": {
            "empatía": "vulnerable",
            "lógica": "analítica",
            "deseo": "provocadora",
            "silencio_prolongado": "silenciosa"
        },
        "vulnerable": {
            "protección": "enigmática",
            "conexión": "perséfone",
            "rechazo": "silenciosa"
        },
        # ... más transiciones
    }
    
    def __init__(self, user_progress_repo: UserProgressRepository):
        self.repo = user_progress_repo
    
    async def update_diana_state(self, user_id: int, choice_impact: Dict):
        """Actualiza el estado de Diana basado en la elección del usuario"""
        user_progress = await self.repo.get_by_user_id(user_id)
        
        if not user_progress:
            raise ValueError(f"No se encontró progreso para el usuario {user_id}")
        
        # Actualizar resonance_score
        resonance_change = choice_impact.get('resonance_change', 0)
        new_resonance = user_progress.resonance_score + resonance_change
        new_resonance = max(0.0, min(100.0, new_resonance))  # Limitar entre 0 y 100
        
        # Determinar nuevo estado
        new_state = choice_impact.get('diana_state')
        if not new_state:
            # Usar matriz de transición si no hay estado forzado
            new_state = self._calculate_state_transition(
                user_progress.diana_state,
                choice_impact.get('interaction_type', 'neutral')
            )
        
        # Actualizar arquetipos si es necesario
        archetype_unlock = choice_impact.get('archetype_unlock', [])
        
        # Actualizar en la base de datos
        await self.repo.update_progress(
            user_id=user_id,
            diana_state=new_state,
            resonance_score=new_resonance,
            archetype_unlock=archetype_unlock
        )
        
        return {
            'new_state': new_state,
            'resonance_score': new_resonance,
            'unlocked_archetypes': archetype_unlock
        }
    
    def _calculate_state_transition(self, current_state: str, interaction_type: str) -> str:
        """Calcula la transición de estado basada en la interacción"""
        transitions = self.STATE_TRANSITIONS.get(current_state, {})
        return transitions.get(interaction_type, current_state)
```

#### **C. Story Handler con FSM (Tarea 3.3)**

```python
# src/telegram_bot/states/story_states.py
from aiogram.fsm.state import State, StatesGroup

class StoryStates(StatesGroup):
    viewing_scene = State()
    waiting_choice = State()
    story_paused = State()

# src/telegram_bot/handlers/story_handler.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.services.story_service import StoryService
from src.services.persona_service import PersonaService
from src.telegram_bot.states.story_states import StoryStates

router = Router()

class StoryHandler:
    def __init__(self, story_service: StoryService, persona_service: PersonaService):
        self.story_service = story_service
        self.persona_service = persona_service
    
    async def start_story_command(self, message: Message, state: FSMContext):
        """Maneja el comando para iniciar la historia"""
        user_id = message.from_user.id
        
        # Iniciar la historia
        scene = await self.story_service.start_story(user_id)
        
        # Guardar estado
        await state.set_state(StoryStates.viewing_scene)
        await state.update_data(current_scene_id=scene['scene_id'])
        
        # Enviar escena
        await self._send_scene(message, scene)
    
    async def _send_scene(self, message: Message, scene: Dict):
        """Envía una escena al usuario con sus opciones"""
        text = scene['text']
        
        # Crear teclado con las opciones
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for choice in scene.get('choices', []):
            button = InlineKeyboardButton(
                text=choice['text'],
                callback_data=f"choice_{choice['id']}"
            )
            keyboard.inline_keyboard.append([button])
        
        # Añadir botón de pausa
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⏸ Pausar", callback_data="pause_story")
        ])
        
        await message.answer(text, reply_markup=keyboard)
        
    async def handle_choice(self, callback: CallbackQuery, state: FSMContext):
        """Maneja la elección del usuario"""
        user_id = callback.from_user.id
        choice_id = callback.data.replace("choice_", "")
        
        # Procesar elección
        result = await self.story_service.process_choice(user_id, choice_id)
        
        # Actualizar estado de Diana
        diana_update = await self.persona_service.update_diana_state(
            user_id, 
            result['impact']
        )
        
        # Enviar siguiente escena
        next_scene = result['next_scene']
        
        if next_scene:
            await callback.message.edit_text(
                f"✨ Diana ahora está {diana_update['new_state']}\n"
                f"🔮 Resonancia: {diana_update['resonance_score']:.1f}%"
            )
            await self._send_scene(callback.message, next_scene)
        else:
            # Fin del nivel
            await callback.message.edit_text(
                "🌙 Has completado el Nivel 1\n"
                f"Estado final de Diana: {diana_update['new_state']}\n"
                f"Resonancia alcanzada: {diana_update['resonance_score']:.1f}%"
            )
            await state.clear()
```

#### **D. Archivo story.json (Nivel 1)**

```json
{
  "level_1_intro": {
    "text": "🌙 *El Umbral*\n\nTe encuentras ante una puerta entreabierta. Del otro lado, una voz susurra:\n\n_\"¿Sabes qué es lo que realmente buscas cuando miras a través del espejo?\"_\n\nDiana te observa desde las sombras, esperando...",
    "visual": "threshold_door",
    "choices": [
      {
        "id": "react_quick",
        "text": "Responder rápidamente",
        "next_scene": "level_1_quick_path",
        "impact": {
          "diana_state": "provocadora",
          "resonance_change": 2,
          "interaction_type": "deseo"
        }
      },
      {
        "id": "react_thoughtful",
        "text": "Reflexionar antes de responder",
        "next_scene": "level_1_thoughtful_path",
        "impact": {
          "diana_state": "analítica",
          "resonance_change": 3,
          "interaction_type": "lógica"
        }
      }
    ],
    "meta": {
      "level": 1,
      "is_checkpoint": true
    }
  },
  "level_1_quick_path": {
    "text": "Diana sonríe, una curva apenas perceptible.\n\n_\"Impulsivo... Me gusta. Pero la impulsividad sin dirección es solo ruido.\"_\n\nSu figura se acerca, y sientes que el aire se vuelve más denso.\n\n_\"¿Qué harías si te dijera que puedo mostrarte exactamente lo que deseas... pero primero debes admitir qué es?\"_",
    "choices": [
      {
        "id": "admit_desire",
        "text": "Admitir mi deseo",
        "next_scene": "level_1_revelation",
        "impact": {
          "diana_state": "perséfone",
          "resonance_change": 5,
          "archetype_unlock": ["perséfone"]
        }
      },
      {
        "id": "deflect",
        "text": "Desviar la pregunta",
        "next_scene": "level_1_enigma",
        "impact": {
          "diana_state": "enigmática",
          "resonance_change": -1
        }
      }
    ]
  },
  "level_1_thoughtful_path": {
    "text": "El silencio se extiende. Diana inclina la cabeza, estudiándote.\n\n_\"Interesante... Mides cada palabra como si fueran monedas de oro.\"_\n\nLucien aparece desde las sombras: _\"La reflexión es el primer paso hacia la comprensión... o hacia la parálisis.\"_\n\n¿Qué eliges?",
    "choices": [
      {
        "id": "embrace_analysis",
        "text": "Analizar la situación",
        "next_scene": "level_1_wisdom",
        "impact": {
          "diana_state": "atenea",
          "resonance_change": 4,
          "archetype_unlock": ["atenea"]
        }
      },
      {
        "id": "trust_intuition",
        "text": "Confiar en mi intuición",
        "next_scene": "level_1_mystery",
        "impact": {
          "diana_state": "hécate",
          "resonance_change": 3,
          "archetype_unlock": ["hécate"]
        }
      }
    ]
  },
  "level_1_revelation": {
    "text": "🔥 *Primera Pista Desbloqueada*\n\nDiana se acerca tanto que puedes sentir su aliento.\n\n_\"El deseo confesado es el primer acto de valentía... o de rendición.\"_\n\nRecibes tu primera pista: *'Los espejos no mienten, pero tampoco dicen toda la verdad.'*",
    "choices": [],
    "meta": {
      "is_checkpoint": true,
      "reward": "first_clue"
    }
  },
  "level_1_enigma": {
    "text": "Diana retrocede, su forma volviéndose más difusa.\n\n_\"Predecible. El miedo a la vulnerabilidad es... decepcionante.\"_\n\nTu resonancia con Diana disminuye. Tendrás que trabajar más para recuperar su interés.",
    "choices": []
  },
  "level_1_wisdom": {
    "text": "🦉 *Sabiduría Reconocida*\n\n_\"Atenea estaría orgullosa. El análisis es una forma de deseo... el deseo de comprender.\"_\n\nRecibes una pista diferente: *'La lógica es solo otra forma de magia cuando se aplica al corazón humano.'*",
    "choices": [],
    "meta": {
      "reward": "wisdom_clue"
    }
  },
  "level_1_mystery": {
    "text": "🌙 *El Velo Se Levanta*\n\nDiana y Lucien intercambian una mirada cómplice.\n\n_\"La intuición... el lenguaje olvidado del alma. Hécate sonríe desde las sombras.\"_\n\nTu pista: *'Lo que no se puede explicar, a menudo es lo más real.'*",
    "choices": [],
    "meta": {
      "reward": "mystery_clue"
    }
  }
}
```

### **3. Pruebas de Integración (Tarea 3.4)**

```python
# tests/integration/test_full_flow.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio