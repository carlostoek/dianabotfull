# src/security/anti_abuse_system.py

import time
from collections import defaultdict

class AntiAbuseSystem:
    """
    Detecta y mitiga patrones de abuso como el spam o flooding.
    """
    def __init__(self, interactions_limit: int = 20, cooldown_period: int = 60):
        self.interactions_limit = interactions_limit  # Límite de interacciones por minuto
        self.cooldown_period = cooldown_period  # Segundos de cooldown
        self.user_interactions = defaultdict(list)
        self.user_cooldowns = {}

    def detect_patterns(self, user_id: int) -> bool:
        """
        Detecta si un usuario está excediendo el límite de interacciones.
        
        Args:
            user_id (int): El ID del usuario.
            
        Returns:
            bool: True si se detecta abuso, False en caso contrario.
        """
        current_time = time.time()
        
        # Limpiar timestamps viejos
        self.user_interactions[user_id] = [
            t for t in self.user_interactions[user_id] if current_time - t < 60
        ]
        
        # Añadir timestamp actual
        self.user_interactions[user_id].append(current_time)
        
        # Verificar si se ha excedido el límite
        if len(self.user_interactions[user_id]) > self.interactions_limit:
            self.apply_cooldown(user_id)
            return True
            
        return False

    def apply_cooldown(self, user_id: int):
        """
        Aplica un período de cooldown a un usuario.
        
        Args:
            user_id (int): El ID del usuario.
        """
        cooldown_end_time = time.time() + self.cooldown_period
        self.user_cooldowns[user_id] = cooldown_end_time
        print(f"User {user_id} ha sido puesto en cooldown por {self.cooldown_period} segundos.")

    def is_in_cooldown(self, user_id: int) -> bool:
        """
        Verifica si un usuario está actualmente en cooldown.
        
        Args:
            user_id (int): El ID del usuario.
            
        Returns:
            bool: True si el usuario está en cooldown, False en caso contrario.
        """
        if user_id in self.user_cooldowns:
            if time.time() < self.user_cooldowns[user_id]:
                return True
            else:
                # El cooldown ha expirado
                del self.user_cooldowns[user_id]
        return False

anti_abuse_system = AntiAbuseSystem()