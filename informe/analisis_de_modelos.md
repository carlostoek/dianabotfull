# Análisis y Definición de Modelos para DianaBot

## Resumen Ejecutivo

Este informe detalla la arquitectura de datos para el sistema **DianaBot**. Tras analizar el código fuente y la documentación, se ha determinado que el sistema es un bot de Telegram con una narrativa interactiva y sistemas de gamificación.

- **Modelos Identificados:** Se han identificado **6 modelos de base de datos principales** que son cruciales para la funcionalidad descrita en el `diseñotecnico.md`. Actualmente, solo 1 (`User`) está parcialmente implementado en la base de datos.
- **Principales Desafíos:** La mayor discrepancia es entre la lógica de negocio (que opera con datos en memoria, como en `MissionService`) y la falta de persistencia en la base de datos. El sistema no puede recordar el progreso del usuario entre reinicios, lo cual es crítico.
- **Recomendaciones Generales:**
    1.  **Implementar todos los modelos definidos** en SQLAlchemy.
    2.  **Adoptar `Alembic`** para gestionar las migraciones de la base de datos de forma sistemática.
    3.  **Refactorizar los servicios** para que utilicen los modelos de base de datos en lugar de diccionarios en memoria.
    4.  **Crear un patrón de Repositorio** para abstraer el acceso a datos y desacoplar la lógica de negocio de SQLAlchemy.

---

## 1. Análisis del Código Actual

- **Patrones de Datos:** El código utiliza Pydantic para la validación y serialización de datos (`src/models/`) y SQLAlchemy para el mapeo objeto-relacional (`src/database/models.py`). Sin embargo, no están sincronizados. El modelo `User` de Pydantic es más completo que su contraparte de SQLAlchemy.
- **Redundancias e Inconsistencias:** La lógica de `MissionService` simula el progreso de las misiones en un diccionario de Python (`_user_mission_status`). Esto es inconsistente con la necesidad de persistencia de datos de un usuario. Cada reinicio del bot borra todo el progreso.
- **Relaciones:** No hay relaciones formales definidas a nivel de base de datos, aunque la lógica de la aplicación implica que un usuario puede tener misiones completadas, logros y un progreso en la historia.

---

## 2. Identificación de Entidades

| Nombre del Modelo | Propósito y Responsabilidad | Atributos Principales | Relaciones |
| :--- | :--- | :--- | :--- |
| **User** | Almacena la información básica y el estado del usuario. | `id`, `username`, `role`, `points`, `vip_expires_at` | 1:N con `UserProgress`, 1:N con `UserMission`, 1:N con `UserAchievement` |
| **Mission** | Define una misión disponible en el sistema. | `id`, `name`, `description`, `reward_points` | 1:N con `UserMission` |
| **UserMission** | Tabla de enlace que registra la finalización de una misión por un usuario. | `user_id`, `mission_id`, `completed_at` | N:1 con `User`, N:1 con `Mission` |
| **Achievement** | Define un logro a largo plazo. | `id`, `name`, `description` | 1:N con `UserAchievement` |
| **UserAchievement** | Tabla de enlace que registra la obtención de un logro por un usuario. | `user_id`, `achievement_id`, `unlocked_at` | N:1 con `User`, N:1 con `Achievement` |
| **UserProgress** | Almacena el estado narrativo y de arquetipo del usuario. | `user_id`, `current_story_node`, `unlocked_fragments`, `archetype` | 1:1 con `User` |

---

## 3. Definición de Modelos

A continuación se presentan los modelos de SQLAlchemy propuestos.

### Estructura de los Modelos

```python
# Propuesta para src/database/models.py
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, JSON,
                        create_engine)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, comment="Telegram User ID")
    username = Column(String, nullable=True)
    role = Column(String, default='free', nullable=False)
    points = Column(Integer, default=0, nullable=False)
    vip_expires_at = Column(DateTime, nullable=True)
    
    # Relaciones
    progress = relationship("UserProgress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    missions = relationship("UserMission", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    current_story_node = Column(String, nullable=True)
    unlocked_fragments = Column(JSON, default=list, nullable=False)
    archetype = Column(String, nullable=True, comment="Arquetipo dominante del usuario")
    
    # Relación
    user = relationship("User", back_populates="progress")

class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, comment="Identificador único, ej: 'daily_login'")
    description = Column(String, nullable=False)
    reward_points = Column(Integer, nullable=False)
    
    # Relación
    users = relationship("UserMission", back_populates="mission")

class UserMission(Base):
    __tablename__ = 'user_missions'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    mission_id = Column(Integer, ForeignKey('missions.id'), primary_key=True)
    completed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, primary_key=True)
    
    # Relaciones
    user = relationship("User", back_populates="missions")
    mission = relationship("Mission", back_populates="users")

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    
    # Relación
    users = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), primary_key=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")

```

### Justificación y Consideraciones

- **Normalización:** Se utilizan tablas de enlace (`UserMission`, `UserAchievement`) para crear relaciones N:N entre usuarios y misiones/logros, evitando la duplicación de datos. Esto sigue la Tercera Forma Normal (3NF).
- **Integridad:** El uso de `ForeignKey` asegura la integridad referencial a nivel de base de datos. Si un usuario es eliminado, `cascade="all, delete-orphan"` eliminará sus registros asociados.
- **Tipos de Datos:** Se utiliza `JSON` en `UserProgress` para `unlocked_fragments`, ofreciendo flexibilidad para almacenar una lista de identificadores de fragmentos de historia.

---

## 4. Consideraciones Técnicas

- **ORM a utilizar:** **SQLAlchemy** ya está en el proyecto y es una excelente elección. Se debe continuar con él.
- **Patrones de diseño:** Se recomienda introducir un **Patrón Repositorio**. Cada modelo tendría su repositorio (ej. `UserRepository`) que manejaría la lógica de acceso a datos (sesiones, commits, rollbacks). Esto aislaría los servicios de la implementación de la base de datos.
- **Índices recomendados:** Se deben añadir índices a todas las claves foráneas (`user_id`, `mission_id`, etc.) y a campos utilizados en búsquedas frecuentes como `missions.name`.
    ```python
    # Ejemplo en el modelo Mission
    name = Column(String, unique=True, nullable=False, index=True)
    ```
- **Migraciones necesarias:** Es **crítico** integrar **Alembic**. Sin él, cualquier cambio en los modelos requerirá una gestión manual de la base de datos, lo cual es propenso a errores.

---

## 5. Arquitectura de Datos

- **Diagrama de Relaciones (Textual):**
    - `User` (1) <--> (1) `UserProgress`
    - `User` (1) <--> (N) `UserMission` (N) <--> (1) `Mission`
    - `User` (1) <--> (N) `UserAchievement` (N) <--> (1) `Achievement`
- **Jerarquía y Dependencias:**
    - `User` es el modelo central.
    - `Mission` y `Achievement` son modelos maestros que definen el contenido.
    - `UserMission`, `UserAchievement` y `UserProgress` dependen de `User` y almacenan datos específicos de la actividad del usuario.
- **Flujo de Datos Principal (Ejemplo: Completar Misión):**
    1. El `handler` de Telegram recibe un evento (ej. un mensaje).
    2. Llama a `MissionService.complete_mission('send_message')`.
    3. `MissionService` consulta la tabla `missions` para obtener el ID de la misión.
    4. Luego, inserta un nuevo registro en la tabla `user_missions` con el `user_id`, `mission_id` y la fecha.
    5. Si la inserción es exitosa, publica un evento `mission_completed`.
    6. Un listener (ej. `PointsService`) consume el evento y actualiza el campo `points` en la tabla `users`.

---

## 6. Plan de Implementación

1.  **Configurar Alembic:**
    - `pip install alembic`
    - `alembic init migrations`
    - Configurar `alembic.ini` y `env.py` para que apunten a la base de datos y a los modelos de `Base`.
2.  **Actualizar Modelos:** Reemplazar el contenido de `src/database/models.py` con el código propuesto en la sección 3.
3.  **Crear Migración Inicial:**
    - `alembic revision --autogenerate -m "Crear estructura inicial de modelos"`
    - Revisar el script de migración generado para asegurar que es correcto.
    - `alembic upgrade head` para aplicar los cambios a la base de datos.
4.  **Refactorizar Servicios:**
    - Modificar `MissionService` para que use `Session` de SQLAlchemy para consultar y escribir en las tablas `missions` y `user_missions`. Eliminar los diccionarios en memoria.
    - Crear los servicios faltantes (`AchievementService`, `StoryService`) que operen sobre los nuevos modelos.
5.  **Implementar Repositorios (Opcional pero recomendado):**
    - Crear una clase base `Repository` y luego implementaciones concretas como `UserRepository`.
6.  **Pruebas:**
    - Escribir pruebas de integración que utilicen una base de datos de prueba para verificar que los servicios interactúan correctamente con la base de datos (ej. que al completar una misión se crea el registro en `user_missions` y se suman los puntos en `users`).

---

## 7. Recomendaciones Adicionales

- **Mejores Prácticas:** Utilizar Pydantic para definir los esquemas de la API (lo que entra y sale de los servicios) y SQLAlchemy para la representación de la base de datos. Un repositorio puede encargarse de la traducción entre ambos.
- **Escalabilidad:** La arquitectura propuesta es escalable. La base de datos relacional manejará grandes volúmenes de datos de manera eficiente, especialmente con los índices adecuados.
- **Mantenibilidad:** La separación de responsabilidades (Servicios, Repositorios, Modelos) y el uso de Alembic mejorarán drásticamente la mantenibilidad del código a largo plazo.
