# Análisis y Definición de Modelos para DianaBot (Revisión 2)

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
| **UserAchievement**| Tabla de enlace que registra la obtención de un logro por un usuario. | `user_id`, `achievement_id`, `unlocked_at` | N:1 con `User`, N:1 con `Achievement` |
| **UserProgress** | Almacena el estado narrativo, de arquetipo y de personalidad de Diana para el usuario. | `user_id`, `diana_state`, `dominant_archetype`, `resonance_score`, `last_interaction_at` | 1:1 con `User` |

---

## 3. Definición de Modelos

A continuación se presentan los modelos de SQLAlchemy propuestos, **integrando la lógica del `diseñotecnico.md`**.

### Estructura de los Modelos

```python
# Propuesta para src/database/models.py
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, JSON,
                        create_engine, Float)
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
    
    # --- Campos para la Historia ---
    current_story_node = Column(String, nullable=True)
    unlocked_fragments = Column(JSON, default=list, nullable=False)
    
    # --- Campos para el Sistema de Personalidad (diseñotecnico.md) ---
    diana_state = Column(String, default='Enigmática', nullable=False, comment="Estado actual de Diana: Vulnerable, Enigmática, etc.")
    dominant_archetype = Column(String, nullable=True, comment="Arquetipo dominante del usuario: El Sensualista, etc.")
    secondary_archetypes = Column(JSON, default=list, nullable=False, comment="Otros arquetipos detectados")
    resonance_score = Column(Float, default=0.0, nullable=False, comment="Puntaje de resonancia emocional")
    significant_interactions = Column(JSON, default=list, nullable=False, comment="Registro de interacciones clave")
    last_interaction_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    user = relationship("User", back_populates="progress")

class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True, comment="Identificador único, ej: 'daily_login'")
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

- **Integración de Personalidad:** El modelo `UserProgress` ahora contiene campos clave del `diseñotecnico.md`. `diana_state` almacena el estado actual de la IA, `dominant_archetype` guarda el perfil del usuario, y `resonance_score` cuantifica la conexión emocional. Esto permite que el motor de respuesta consulte directamente la base de datos para adaptar el comportamiento de Diana.
- **Flexibilidad:** El uso de `JSON` para `secondary_archetypes` y `significant_interactions` proporciona la flexibilidad necesaria para almacenar listas de datos complejos sin necesidad de crear tablas adicionales, lo cual es adecuado para este tipo de metadatos.
- **Normalización:** Se mantienen las tablas de enlace (`UserMission`, `UserAchievement`) para relaciones N:N, asegurando una buena estructura de base de datos.

---

## 4. Consideraciones Técnicas

- **ORM a utilizar:** **SQLAlchemy** ya está en el proyecto y es una excelente elección. Se debe continuar con él.
- **Patrones de diseño:** Se recomienda introducir un **Patrón Repositorio**. Cada modelo tendría su repositorio (ej. `UserRepository`) que manejaría la lógica de acceso a datos (sesiones, commits, rollbacks). Esto aislaría los servicios de la implementación de la base de datos.
- **Índices recomendados:** Se deben añadir índices a todas las claves foráneas (`user_id`, `mission_id`, etc.) y a campos utilizados en búsquedas frecuentes como `missions.name`.
- **Migraciones necesarias:** Es **crítico** integrar **Alembic**. Sin él, cualquier cambio en los modelos requerirá una gestión manual de la base de datos, lo cual es propenso a errores.

---

## 5. Arquitectura de Datos

- **Diagrama de Relaciones (Textual):**
    - `User` (1) <--> (1) `UserProgress`
    - `User` (1) <--> (N) `UserMission` (N) <--> (1) `Mission`
    - `User` (1) <--> (N) `UserAchievement` (N) <--> (1) `Achievement`
- **Jerarquía y Dependencias:**
    - `User` es el modelo central.
    - `UserProgress` ahora contiene el "cerebro" del estado de la interacción de cada usuario.
- **Flujo de Datos Principal (Ejemplo: Respuesta de Diana):**
    1. El `handler` de Telegram recibe un mensaje del usuario.
    2. Llama a un nuevo servicio, `PersonaService`.
    3. `PersonaService` lee el `UserProgress` del usuario desde la base de datos.
    4. Analiza el mensaje entrante (longitud, palabras clave, etc.) y actualiza los campos `resonance_score`, `dominant_archetype` y `last_interaction_at`.
    5. Basado en estos datos y en el `diana_state` actual, selecciona una nueva respuesta y actualiza el `diana_state` si es necesario.
    6. Guarda los cambios en el registro `UserProgress`.
    7. Envía la respuesta seleccionada al usuario.

---

## 6. Plan de Implementación

1.  **Configurar Alembic:** (Si no se ha hecho) `pip install alembic`, `alembic init migrations`, y configurar.
2.  **Actualizar Modelos:** Reemplazar el contenido de `src/database/models.py` con el código propuesto en la sección 3.
3.  **Crear Migración:**
    - `alembic revision --autogenerate -m "Integrar modelos de personalidad y arquetipo"`
    - Revisar el script y aplicar con `alembic upgrade head`.
4.  **Crear/Refactorizar Servicios:**
    - Crear un `PersonaService` que implemente la lógica de `diseñotecnico.md`, interactuando con el modelo `UserProgress`.
    - Refactorizar los servicios existentes para que usen la sesión de la base de datos.
5.  **Pruebas:**
    - Añadir pruebas para el `PersonaService`, simulando diferentes entradas de usuario y verificando que el `diana_state` y el `archetype` se actualizan correctamente en la base de datos de prueba.

---

## 7. Recomendaciones Adicionales

- **Mejores Prácticas:** Utilizar Pydantic para definir los esquemas de la API y SQLAlchemy para la base de datos. Un repositorio puede traducir entre ambos.
- **Escalabilidad:** La arquitectura es escalable. El `UserProgress` centraliza los datos de estado, lo que facilita su consulta y actualización.
- **Mantenibilidad:** La nueva estructura es más mantenible porque alinea directamente la implementación de la base de datos con los conceptos del diseño técnico.