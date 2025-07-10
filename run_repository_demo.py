# -*- coding: utf-8 -*-
"""
Script para demostrar el uso de UserMissionRepository y crear la tabla en la BD.
"""
import os
from src.database.database_setup import engine, Base
from src.database.user_mission_repository import UserMissionRepository
from src.models.user_mission_progress import UserMissionProgress

def setup_database():
    """Crea las tablas de la base de datos."""
    print("Creando tabla para UserMissionProgress si no existe...")
    Base.metadata.create_all(bind=engine)
    print("Tabla lista.")

def demonstrate_repository():
    """Ejecuta una demostración de los métodos del repositorio."""
    USER_ID = 123
    MISSION_ID = "daily_001"

    print(f"\n--- Demostración para el usuario {USER_ID} y misión '{MISSION_ID}' ---")

    # 1. Iniciar una misión
    print("\n1. Iniciando misión...")
    UserMissionRepository.start_mission(USER_ID, MISSION_ID)

    # 2. Obtener el progreso
    progress = UserMissionRepository.get_mission_progress(USER_ID, MISSION_ID)
    print(f"   Progreso actual: {progress.progress}%, Estado: {progress.status}")

    # 3. Actualizar el progreso
    print("\n2. Actualizando progreso al 25.0%...")
    UserMissionRepository.update_progress(USER_ID, MISSION_ID, 25.0)
    progress = UserMissionRepository.get_mission_progress(USER_ID, MISSION_ID)
    print(f"   Progreso actual: {progress.progress}%, Estado: {progress.status}")

    # 4. Intentar actualizar con un valor > 100
    print("\n3. Actualizando progreso a 150.0% (debería ser limitado a 100)...")
    UserMissionRepository.update_progress(USER_ID, MISSION_ID, 150.0)
    progress = UserMissionRepository.get_mission_progress(USER_ID, MISSION_ID)
    print(f"   Progreso actual: {progress.progress}%")

    # 5. Completar la misión
    print("\n4. Completando la misión...")
    UserMissionRepository.complete_mission(USER_ID, MISSION_ID)
    progress = UserMissionRepository.get_mission_progress(USER_ID, MISSION_ID)
    print(f"   Progreso final: {progress.progress}%, Estado: {progress.status}, Completada en: {progress.completed_at}")

    # 6. Obtener todas las misiones del usuario
    print("\n5. Obteniendo todas las misiones del usuario...")
    all_missions = UserMissionRepository.get_user_missions(USER_ID)
    print(f"   Encontradas {len(all_missions)} misiones para el usuario {USER_ID}.")
    for m in all_missions:
        print(f"   - Misión: {m.mission_id}, Estado: {m.status}")
        
    # 7. Iniciar y fallar otra misión
    MISSION_ID_2 = "weekly_challenge"
    print(f"\n6. Iniciando y fallando la misión '{MISSION_ID_2}'...")
    UserMissionRepository.start_mission(USER_ID, MISSION_ID_2)
    UserMissionRepository.fail_mission(USER_ID, MISSION_ID_2)
    progress2 = UserMissionRepository.get_mission_progress(USER_ID, MISSION_ID_2)
    print(f"   Estado de la misión '{MISSION_ID_2}': {progress2.status}")


if __name__ == "__main__":
    # Limpiar la base de datos de demostración si existe
    if os.path.exists("dianabot.db"):
        os.remove("dianabot.db")
        print("Base de datos anterior eliminada.")
        
    setup_database()
    demonstrate_repository()
