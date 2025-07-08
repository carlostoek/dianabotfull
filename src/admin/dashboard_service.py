# src/admin/dashboard_service.py
import logging
from src.services.user_service import UserService
from src.services.points_service import PointsService
from src.services.achievements_service import AchievementsService

logger = logging.getLogger(__name__)

class DashboardService:
    """
    Proporciona métricas clave sobre el estado de la aplicación para el panel de administración.
    """
    def __init__(self, user_service: UserService, points_service: PointsService, achievements_service: AchievementsService):
        self._user_service = user_service
        self._points_service = points_service
        self._achievements_service = achievements_service

    def get_metrics(self) -> dict:
        """
        Recopila y devuelve un diccionario con las métricas actuales del sistema.
        """
        logger.info("Recopilando métricas del sistema...")
        
        # Accedemos a los datos internos de los servicios para la simulación.
        # En un sistema real, esto podría consultar vistas de base de datos o cachés.
        total_users = len(self._user_service._users_db)
        total_points = sum(self._points_service._user_points.values())
        
        unlocked_achievements_count = sum(
            len(achievements) for achievements in self._achievements_service._user_unlocked_achievements.values()
        )

        metrics = {
            "total_users": total_users,
            "total_points_distributed": total_points,
            "total_achievements_unlocked": unlocked_achievements_count,
            "vip_users": len(self._user_service._vip_expirations)
        }
        
        return metrics
