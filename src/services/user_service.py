import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from src.models.user import User, UserRole
from src.core.integration_hub import IntegrationHub

logger = logging.getLogger(__name__)

class UserService:
    """
    Gestiona la lógica de negocio de los usuarios.
    """
    def __init__(self, hub: IntegrationHub):
        self.hub = hub
        # Almacenes en memoria para simulación
        self._users_db: Dict[int, User] = {}
        self._vip_expirations: Dict[int, datetime] = {}
        
        # Inicializar con usuarios de prueba
        if not self._users_db:
            self._users_db[1] = User(id=1, username="test_user", points=500, role=UserRole.FREE)
            self._users_db[2] = User(id=2, username="story_chooser", points=100, role=UserRole.FREE)

    def get_user(self, user_id: int) -> Optional[User]:
        return self._users_db.get(user_id)

    def save_user(self, user: User):
        self._users_db[user.id] = user

    # --- Nuevos métodos para IntegrationHub ---
    def grant_temporary_vip(self, data: dict):
        """
        Handler para 'STORY_CHOICE_MADE'. Otorga VIP temporal por una decisión en la historia.
        """
        user_id = data.get("user_id")
        choice = data.get("choice")
        
        logger.info(f"[HUB] UserService: Procesando decisión '{choice}' para user '{user_id}'.")
        
        # Lógica de ejemplo: ciertas decisiones otorgan VIP
        if choice == "explore_cave":
            user = self.get_user(user_id)
            if user and user.role != UserRole.VIP:
                expiration_time = datetime.now() + timedelta(hours=1) # VIP por 1 hora
                self._vip_expirations[user_id] = expiration_time
                
                logger.info(f"[HUB] UserService: Otorgando VIP temporal a user '{user_id}' hasta {expiration_time.isoformat()}.")
                
                new_data = {
                    "user_id": user_id,
                    "status": "granted",
                    "expires_at": expiration_time.isoformat()
                }
                self.hub.route_event("VIP_STATUS_GRANTED", new_data)
            else:
                logger.info(f"[HUB] UserService: El usuario no es elegible para VIP temporal (ya es VIP o no existe).")
