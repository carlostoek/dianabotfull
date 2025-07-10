# -*- coding: utf-8 -*-
"""
Configuración inicial de la base de datos con SQLAlchemy.

Define el motor, la base declarativa y la fábrica de sesiones.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Se usa una base de datos en memoria para este ejemplo.
# En una aplicación real, esto sería una URL de conexión a una BD persistente.
SQLALCHEMY_DATABASE_URL = "sqlite:///./dianabot.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_session():
    """Generador para obtener una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
