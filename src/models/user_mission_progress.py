# -*- coding: utf-8 -*-
"""
Define el modelo de la base de datos para el progreso de las misiones de usuario.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, PrimaryKeyConstraint
from src.database.database_setup import Base

class UserMissionProgress(Base):
    """
    Modelo SQLAlchemy para el seguimiento del progreso de un usuario en una misión.

    Attributes:
        user_id (int): Identificador del usuario.
        mission_id (str): Identificador de la misión.
        status (str): Estado actual de la misión ('pending', 'in_progress', 'completed', 'failed').
        progress (float): Porcentaje de progreso (0.0 a 100.0).
        started_at (datetime): Fecha y hora de inicio de la misión.
        completed_at (datetime, optional): Fecha y hora de finalización de la misión.
    """
    __tablename__ = "user_mission_progress"

    user_id = Column(Integer, nullable=False)
    mission_id = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    progress = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'mission_id'),
    )

    def __repr__(self):
        return (
            f"<UserMissionProgress(user_id={self.user_id}, mission_id='{self.mission_id}', "
            f"status='{self.status}', progress={self.progress})>"
        )
