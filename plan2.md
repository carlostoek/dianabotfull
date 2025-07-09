# Plan de Acción - Beta Funcional DianaBot

**Objetivo:** Desarrollar la primera versión beta funcional de DianaBot en un plazo de 3 semanas, integrando los componentes clave y asegurando la correcta implementación de los modelos de datos definidos.

**MVP (Producto Mínimo Viable) para la Beta:**
- Un bot que registra usuarios y persiste su información.
- Sistema de puntos funcional para una misión principal (ej. login diario).
- Flujo narrativo básico del "Nivel 1" donde el usuario puede leer fragmentos y tomar al menos una decisión.
- El estado de Diana (`diana_state`) cambia en respuesta a la primera decisión del usuario.
- Comandos básicos funcionales: `/start`, `/puntos`, `/misiones`.

---

## Fase 0: Análisis y Configuración del Entorno (Días 1-2)

**Objetivo:** Validar la arquitectura de datos y preparar el entorno de desarrollo para garantizar una base sólida.

- **Tareas:**
  - [ ] **Tarea 0.1:** Revisar y validar el documento `informe/analisis_de_modelos.md` para confirmar que los modelos cubren las necesidades de la beta.
  - [ ] **Tarea 0.2:** Crear un diagrama de entidad-relación (puede ser en formato Markdown/texto) basado en los modelos finales y guardarlo como `docs/schema.md`.
  - [ ] **Tarea 0.3:** Configurar el entorno virtual de Python y asegurar que todas las dependencias de `requirements.txt` estén instaladas.
  - [ ] **Tarea 0.4:** Instalar `alembic` y ejecutar `alembic init migrations` para crear la estructura de gestión de migraciones.
  - [ ] **Tarea 0.5:** Configurar `alembic.ini` y `migrations/env.py` para que se conecten a la base de datos y reconozcan los modelos de SQLAlchemy.

- **Entregables:**
  - Archivo `docs/schema.md` con el diagrama de la base de datos.
  - Directorio `migrations` configurado.
  - Entorno de desarrollo local funcional.
- **Criterios de Éxito:**
  - El equipo está de acuerdo con el esquema de la base de datos.
  - El comando `alembic current` se ejecuta sin errores.

---

## Fase 1: Implementación del Núcleo y Persistencia (Días 3-6)

**Objetivo:** Implementar la estructura de la base de datos y la lógica de acceso a datos, y poner en línea un bot básico que registre usuarios.

- **Tareas:**
  - [ ] **Tarea 1.1:** Transferir las clases de los modelos definidos al archivo `src/database/models.py`.
  - [ ] **Tarea 1.2:** Generar la migración inicial con `alembic revision --autogenerate -m "Crear estructura inicial de la base de datos"`.
  - [ ] **Tarea 1.3:** Aplicar la migración a la base de datos con `alembic upgrade head`.
  - [ ] **Tarea 1.4:** Implementar un patrón Repositorio básico en `src/database/repository.py` para abstraer las consultas a la base de datos. Empezar con `UserRepository`.
  - [ ] **Tarea 1.5:** Implementar el manejador del comando `/start` que utilice el `UserRepository` para crear un nuevo usuario y su `UserProgress` si no existen.

- **Dependencias:** Tareas de la Fase 0.
- **Entregables:**
  - `src/database/models.py` actualizado.
  - Primer script de migración en `migrations/versions/`.
  - `src/database/repository.py` con la implementación inicial.
  - Un bot funcional que responde a `/start` y persiste al usuario.
- **Criterios de Éxito:**
  - La base de datos física refleja los modelos de SQLAlchemy.
  - Al ejecutar `/start`, se crea una nueva fila en las tablas `users` y `user_progress`.

---

## Fase 2: Lógica de Gamificación y Servicios (Días 7-11)

**Objetivo:** Implementar las mecánicas de juego principales, como misiones y puntos.

- **Tareas:**
  - [ ] **Tarea 2.1:** Crear `MissionRepository` y `AchievementRepository`.
  - [ ] **Tarea 2.2:** Refactorizar `MissionService` para que utilice los repositorios en lugar de diccionarios en memoria.
  - [ ] **Tarea 2.3:** Implementar la lógica para una misión "daily_login". Se debe registrar en la tabla `user_missions`.
  - [ ] **Tarea 2.4:** Crear un `PointsService` que escuche eventos (ej. `mission_completed`) y actualice los puntos del usuario en la base de datos.
  - [ ] **Tarea 2.5:** Implementar los manejadores de comandos `/misiones` y `/puntos` para mostrar información desde la base de datos.
  - [ ] **Tarea 2.6:** Crear datos semilla (seeds) para las misiones y logros iniciales.

- **Dependencias:** Tareas de la Fase 1.
- **Entregables:**
  - Servicios (`MissionService`, `PointsService`) funcionales y conectados a la BD.
  - Comandos `/misiones` y `/puntos` operativos.
- **Criterios de Éxito:**
  - Un usuario recibe puntos automáticamente una vez al día.
  - Los puntos y misiones completadas se muestran correctamente al usuario.

---

## Fase 3: Integración de Narrativa y Pruebas (Días 12-15)

**Objetivo:** Implementar el flujo narrativo básico y asegurar que todos los componentes funcionen juntos correctamente.

- **Tareas:**
  - [ ] **Tarea 3.1:** Crear `StoryService` que cargue el contenido de `story.json` y lo sirva.
  - [ ] **Tarea 3.2:** Crear `PersonaService` que lea y actualice el `UserProgress` (específicamente `diana_state` y `resonance_score`).
  - [ ] **Tarea 3.3:** Implementar el manejador de historia principal que:
    - Presente al usuario el primer nodo de la historia.
    - Capture la respuesta del usuario.
    - Use `PersonaService` para actualizar el estado de Diana.
    - Avance al siguiente nodo de la historia.
  - [ ] **Tarea 3.4:** Escribir pruebas de integración para el flujo completo: `/start` -> completar misión -> recibir puntos -> iniciar historia -> tomar una decisión.
  - [ ] **Tarea 3.5:** Actualizar `README.md` con instrucciones sobre cómo ejecutar y probar la beta.
  - [ ] **Tarea 3.6:** Revisar y documentar las variables de entorno necesarias en `.env.example`.

- **Dependencias:** Tareas de la Fase 2.
- **Entregables:**
  - Flujo narrativo funcional para el Nivel 1.
  - Suite de pruebas de integración.
  - Documentación actualizada.
- **Criterios de Éxito:**
  - Un usuario puede completar el ciclo de juego definido en el MVP.
  - Las pruebas de integración pasan exitosamente.

---

## Plan de Contingencia y Flexibilidad

- **Si los modelos son insuficientes:** Durante la Fase 0, si se detectan carencias en los modelos, se asignará un día adicional para rediseñarlos y actualizar el informe antes de proceder. La implementación no comenzará hasta que el modelo de datos esté validado.
- **Si una tarea se retrasa:** El plan incluye un buffer implícito. Si la lógica de `PersonaService` resulta demasiado compleja para la beta, se simplificará para que solo modifique el `diana_state` basado en la elección directa del usuario, posponiendo el análisis de texto complejo.
- **Si faltan modelos esenciales:** El análisis de la Fase 0 debe identificar esto. Si se descubre más tarde, el proyecto se pausará para definir el modelo faltante, crear su migración y luego reanudar. La prioridad siempre será mantener la integridad de los datos.
