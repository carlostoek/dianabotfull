# src/database/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base  # Cambio clave aquí

Base = declarative_base()  # Ahora usa la nueva ubicación

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    points = Column(Integer, default=0)
    role = Column(String, default='free')
    vip_expires_at = Column(DateTime)