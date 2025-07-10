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