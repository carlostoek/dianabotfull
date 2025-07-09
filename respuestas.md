Total de preguntas: 20
Preguntas respondidas: 15
Preguntas no respondidas: 5

---

### 1. Estructura y Contenido Narrativo

**Archivo story.json:**

*   **¿Ya existe el archivo story.json? Si es así, necesito ver su estructura**
    ✅ Respuesta: No existe aún, pero el formato ideal es muy cercano al ejemplo propuesto. Debe contemplar:
    ```json
    {
      "scene_id": {
        "text": "Texto principal de la escena (puede incluir markdown o tags especiales)",
        "visual": "Identificador o referencia visual si la escena tiene arte asignado",
        "choices": [
          {
            "id": "choice_1",
            "text": "Texto que verá el usuario como botón o elección",
            "next_scene": "scene_2",
            "impact": {
              "diana_state": "vulnerable",
              "resonance_change": +3,
              "archetype_unlock": ["perséfone"]
            }
          }
        ],
        "auto_trigger": false,
        "meta": {
          "level": 1,
          "is_checkpoint": true,
          "available_after": null
        }
      }
    }
    ```

**Contenido del Nivel 1:**

*   **¿Cuántas escenas tiene el Nivel 1?**
    ✅ Respuesta: El Nivel 1 tiene 4 escenas principales más 2 bifurcaciones según el tipo de respuesta del usuario (rápida o reflexiva), totalizando 6 nodos narrativos.

*   **¿Cuál es la narrativa específica que se debe presentar?**
    ✅ Respuesta: El Nivel 1 es la introducción al universo emocional de Diana. Se presenta como un umbral simbólico donde el usuario cruza hacia un espacio de intimidad ambigua. Diana introduce el concepto de espejo emocional, y Lucien actúa como sombra interpretativa. La narrativa activa el primer reflejo del deseo y desencadena el sistema de pistas. Este nivel define el tono de la experiencia: no se trata de avanzar, sino de resonar.

*   **¿Qué decisiones puede tomar el usuario y cómo afectan a Diana?**
    ✅ Respuesta:
    Primera decisión: reaccionar o no a un mensaje inicial. Afecta si Diana se abre o permanece enigmática.
    Segunda decisión: responder de forma rápida o reflexiva. Afecta el estado emocional que adopta Diana (provocadora vs. vulnerable) y el tipo de pista que se entrega.
    Las decisiones no solo afectan el “next_scene”, sino también modifican el resonance_score, desbloquean arquetipos, y determinan cómo Diana interpretará futuras pausas o silencios del usuario.

### 2. Modelos de Datos Existentes

**Modelo UserProgress:**

*   **¿Cómo está definido el campo diana_state? (¿Es un string, enum, JSON?)**
    ✅ Respuesta: Es un `String`.

*   **¿Qué tipo de dato es resonance_score? (¿Integer, Float?)**
    ✅ Respuesta: Es un `Float`.

*   **¿Hay otros campos relacionados con el progreso narrativo?**
    ✅ Respuesta: Sí, además de `diana_state` y `resonance_score`, el modelo `UserProgress` incluye: `current_story_node` (String), `unlocked_fragments` (JSON), `dominant_archetype` (String), `secondary_archetypes` (JSON), `significant_interactions` (JSON), y `last_interaction_at` (DateTime).

**Otros modelos relevantes:**

*   **¿Existe un modelo para guardar el progreso de la historia (ej. StoryProgress)?**
    ✅ Respuesta: No existe un modelo `StoryProgress` separado. El modelo `UserProgress` se encarga de guardar el progreso narrativo de cada usuario.

*   **¿Hay un modelo para las decisiones del usuario?**
    ✅ Respuesta: No hay un modelo explícito para las decisiones del usuario. Es probable que se registren implícitamente a través de los campos de `UserProgress` como `significant_interactions` o el avance en `current_story_node`.

### 3. Sistema de Estados de Diana

**Estados posibles:**

*   **¿Cuáles son los posibles valores de diana_state?**
    ✅ Respuesta:
    Los valores definidos de diana_state incluyen:
    "enigmática"
    "vulnerable"
    "provocadora"
    "analítica"
    "silenciosa"
    "perséfone"
    "afrodita"
    "atenea"
    "hécate"
    Estos últimos cuatro representan arquetipos activos, mientras que los primeros cinco son estados emocionales temporales.

*   **¿Cómo se transiciona entre estados?**
    ✅ Respuesta:
    Mediante una matriz de transición basada en:
    Resonancia emocional acumulada (resonance_score)
    Tipo de interacción (afectiva, reflexiva, lógica)
    Ritmo del usuario (frecuencia de mensajes, pausas, reacciones)
    Decisiones pasadas y micro-marcadores del estilo de respuesta
    Cada elección de escena tiene impactos definidos en impact.diana_state, y puede forzar transiciones o sostener un estado.

*   **¿Hay una matriz de transición o reglas específicas?**
    ✅ Respuesta:
    Sí. Diana cambia de estado si:
    El usuario muestra repetidas pausas largas → cambia a “silenciosa”.
    El usuario revela emociones o empatía → cambia a “vulnerable”.
    El usuario responde con lógica o introspección → cambia a “analítica”.
    El usuario responde con deseo directo o impulsividad → cambia a “provocadora”.
    Además, al detectar un patrón dominante, el sistema activa un arquetipo correspondiente. Esto se registra como active_archetype para modular futuras respuestas.

### 4. Integración con el Bot Existente

**Estructura actual:**

*   **¿Dónde están ubicados los handlers actuales?**
    ✅ Respuesta: Los handlers actuales están ubicados en el directorio `src/telegram_bot/handlers/`.

*   **¿Se está usando FSM (Finite State Machine) de aiogram?**
    ✅ Respuesta: No se encontró evidencia de uso directo de `FSMContext` o `State` de `aiogram` en los handlers existentes.

*   **¿Hay un sistema de comandos ya establecido para iniciar la historia?**
    ✅ Respuesta: Sí, el comando `/start` es el punto de entrada principal para los usuarios, manejado en `src/telegram_bot/handlers/start.py`.

**Flujo de usuario esperado:**

*   **¿Cómo inicia el usuario la experiencia narrativa? (¿comando específico?)**
    ❌ No respondida: Aunque el comando `/start` es el punto de entrada, no se especifica si es el único o cómo se inicia la experiencia narrativa *después* del inicio de sesión.

*   **¿Se puede pausar y retomar la historia?**
    ❌ No respondida: No hay información en el código revisado sobre la capacidad de pausar y retomar la historia.

*   **¿Qué pasa si el usuario abandona a mitad de una escena?**
    ❌ No respondida: No hay información en el código revisado sobre el manejo de usuarios que abandonan una escena.

### 5. Requisitos de Testing

**Framework de testing:**

*   **¿Qué framework de testing se está usando? (pytest, unittest, etc.)**
    ✅ Respuesta: Se está utilizando `pytest` con `pytest-asyncio` para pruebas asíncronas y `pytest-cov` para la cobertura de código.

*   **¿Hay fixtures o utilidades de testing ya creadas?**
    ✅ Respuesta: Sí, en `tests/conftest.py` se definen fixtures como `mock_db` e `integration_hub` para simular la base de datos y el bus de eventos.

*   **¿Existe una base de datos de testing separada?**
    ✅ Respuesta: Sí, se utiliza una base de datos simulada (`MockDatabase`) para los tests, lo que implica que no se interactúa directamente con una base de datos real durante las pruebas unitarias/de integración.

**Cobertura esperada:**

*   **¿Qué nivel de cobertura de código se espera?**
    ❌ No respondida: No hay información explícita en el código o scripts de testing sobre un nivel de cobertura de código esperado.

*   **¿Hay escenarios específicos que deben ser probados?**
    ❌ No respondida: No hay información explícita en el código o scripts de testing sobre escenarios específicos que deban ser probados, más allá de lo que se pueda inferir de los tests existentes.

### 6. Configuración y Variables de Entorno

**Variables actuales:**

*   **¿Qué variables de entorno ya están definidas?**
    ✅ Respuesta: Las variables de entorno definidas son `DATABASE_URL` y `TELEGRAM_BOT_TOKEN`.

*   **¿Hay alguna configuración específica para la narrativa?**
    ✅ Respuesta: No se observa ninguna configuración específica para la narrativa en el archivo `.env.example`.

### 7. Dependencias y Librerías

**Librerías instaladas:**

*   **Contenido actual de requirements.txt**
    ✅ Respuesta:
    ```
    asyncpg
    python-dotenv
    pydantic
    pydantic-settings
    schedule
    aiogram[all]
    sqlalchemy
    alembic
    aiosqlite
    ```

*   **¿Se está usando alguna librería específica para manejo de estados o narrativa?**
    ✅ Respuesta: No se observa ninguna librería específica para manejo de estados o narrativa más allá de `aiogram` y `SQLAlchemy`.

### 8. Estilo y Formato de Mensajes

*   **Formato de respuestas:**
    ❌ No respondida: No hay información en el código revisado sobre un estilo establecido para los mensajes del bot.

*   **¿Se usan emojis específicos?**
    ❌ No respondida: No hay información en el código revisado sobre el uso de emojis específicos.

*   **¿Hay plantillas de mensajes?**
    ❌ No respondida: No hay información en el código revisado sobre la existencia de plantillas de mensajes.
