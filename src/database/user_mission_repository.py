# -*- coding: utf-8 -*-
"""
Repositorio para gestionar el estado de las misiones de los usuarios en la BD.
"""
import logging
import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from src.database.database_setup import SessionLocal
from src.models.user_mission_progress import UserMissionProgress

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UserMissionRepository:
    """
    Clase de repositorio para manejar las operaciones CRUD de UserMissionProgress.
    
    Utiliza métodos estáticos para interactuar con la base de datos a través de
    sesiones de SQLAlchemy.
    """

    @staticmethod
    def _get_progress_entry(session: Session, user_id: int, mission_id: str) -> Optional[UserMissionProgress]:
        """
        Método auxiliar para obtener una entrada de progreso de misión específica.

        Args:
            session (Session): La sesión de base de datos activa.
            user_id (int): El ID del usuario.
            mission_id (str): El ID de la misión.

        Returns:
            Optional[UserMissionProgress]: El objeto de progreso si se encuentra, de lo contrario None.
        """
        return session.query(UserMissionProgress).filter_by(user_id=user_id, mission_id=mission_id).first()

    @staticmethod
    def get_user_missions(user_id: int) -> List[UserMissionProgress]:
        """
        Obtiene todas las misiones asociadas a un usuario.

        Args:
            user_id (int): El ID del usuario.

        Returns:
            List[UserMissionProgress]: Una lista de los registros de progreso de misiones del usuario.
        """
        with SessionLocal() as session:
            missions = session.query(UserMissionProgress).filter_by(user_id=user_id).all()
            logging.info(f"Consultadas {len(missions)} misiones para el usuario {user_id}.")
            return missions

    @staticmethod
    def get_mission_progress(user_id: int, mission_id: str) -> Optional[UserMissionProgress]:
        """
        Obtiene el progreso de una misión específica para un usuario.

        Args:
            user_id (int): El ID del usuario.
            mission_id (str): El ID de la misión.

        Returns:
            Optional[UserMissionProgress]: El registro de progreso si existe.
        """
        with SessionLocal() as session:
            progress = UserMissionRepository._get_progress_entry(session, user_id, mission_id)
            if progress:
                logging.info(f"Consultado progreso para usuario {user_id}, misión '{mission_id}'.")
            else:
                logging.warning(f"No se encontró progreso para usuario {user_id}, misión '{mission_id}'.")
            return progress

    @staticmethod
    def start_mission(user_id: int, mission_id: str) -> UserMissionProgress:
        """
        Inicia una nueva misión para un usuario, creando un registro de progreso.

        Si la misión ya existe, no hace nada y devuelve la entrada existente.

        Args:
            user_id (int): El ID del usuario.
            mission_id (str): El ID de la misión a iniciar.
        
        Returns:
            UserMissionProgress: La entrada de progreso nueva o existente.
        """
        with SessionLocal() as session:
            existing_progress = UserMissionRepository._get_progress_entry(session, user_id, mission_id)
            if existing_progress:
                logging.warning(f"El usuario {user_id} ya ha iniciado la misión '{mission_id}'.")
                return existing_progress

            new_progress = UserMissionProgress(
                user_id=user_id,
                mission_id=mission_id,
                status="in_progress",
                progress=0.0,
                started_at=datetime.datetime.utcnow()
            )
            session.add(new_progress)
            session.commit()
            logging.info(f"Usuario {user_id} ha iniciado la misión '{mission_id}'.")
            return new_progress

    @staticmethod
    def update_progress(user_id: int, mission_id: str, progress: float) -> None:
        """
        Actualiza el porcentaje de progreso de una misión.

        El progreso se limita a un máximo de 100.0.

        Args:
            user_id (int): El ID del usuario.
            mission_id (str): El ID de la misión.
            progress (float): El nuevo porcentaje de progreso.

        Raises:
            ValueError: Si no se encuentra la misión para el usuario.
        """
        with SessionLocal() as session:
            mission_progress = UserMissionRepository._get_progress_entry(session, user_id, mission_id)
            if not mission_progress:
                raise ValueError(f"No se encontró la misión '{mission_id}' para el usuario {user_id}.")
            
            # Limitar el progreso a 100.0
            mission_progress.progress = min(progress, 100.0)
            
            session.commit()
            logging.info(f"Progreso de la misión '{mission_id}' para el usuario {user_id} actualizado a {mission_progress.progress}%.")

    @staticmethod
    def complete_mission(user_id: int, mission_id: str) -> None:
        """
        Marca una misión como completada.

        Args:
            user_id (int): El ID del usuario.
            mission_id (str): El ID de la misión.

        Raises:
            ValueError: Si no se encuentra la misión para el usuario.
        """
        with SessionLocal() as session:
            mission_progress = UserMissionRepository._get_progress_entry(session, user_id, mission_id)
            if not mission_progress:
                raise ValueError(f"No se encontró la misión '{mission_id}' para el usuario {user_id}.")
            
            mission_progress.status = "completed"
            mission_progress.progress = 100.0
            mission_progress.completed_at = datetime.datetime.utcnow()
            
            session.commit()
            logging.info(f"Misión '{mission_id}' completada por el usuario {user_id}.")

    @staticmethod
    def fail_mission(user_id: int, mission_id: str) -> None:
        """
        Marca una misión como fallida.

        Args:
            user_id (int): El ID del usuario.
            mission_id (str): El ID de la misión.

        Raises:
            ValueError: Si no se encuentra la misión para el usuario.
        """
        with SessionLocal() as session:
            mission_progress = UserMissionRepository._get_progress_entry(session, user_id, mission_id)
            if not mission_progress:
                raise ValueError(f"No se encontró la misión '{mission_id}' para el usuario {user_id}.")
            
            mission_progress.status = "failed"
            mission_progress.completed_at = datetime.datetime.utcnow() # Se usa completed_at para registrar cuándo terminó.
            
            session.commit()
            logging.info(f"Misión '{mission_id}' fallida para el usuario {user_id}.")