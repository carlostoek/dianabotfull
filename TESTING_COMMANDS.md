# Comandos de Testing para la Beta de Dianabotfull

Aquí se listan los comandos principales para ejecutar las pruebas y verificar el funcionamiento de la aplicación en esta fase beta.

## 1. Ejecutar todos los tests (Unitarios e Integración)

Este comando ejecutará todos los tests definidos en el directorio `tests/`, incluyendo los unitarios y de integración, y generará un reporte de cobertura de código.

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## 2. Ejecutar tests unitarios específicos

Para ejecutar solo los tests unitarios de un servicio específico (por ejemplo, `StoryService`):

```bash
python -m pytest tests/unit/test_story_service.py -v
```

## 3. Ejecutar tests de integración específicos

Para ejecutar solo los tests de integración del flujo completo:

```bash
python -m pytest tests/integration/test_full_flow.py -v
```

## 4. Iniciar la aplicación (para pruebas manuales)

Para iniciar el bot de Telegram y probarlo manualmente (asegúrate de tener las variables de entorno configuradas, especialmente `TELEGRAM_BOT_TOKEN`):

```bash
python main.py
```

## 5. Comandos de Telegram Implementados

Los siguientes comandos y acciones están actualmente implementados en el bot:

*   `/start`: Inicia la conversación con el bot, crea o recupera el perfil del usuario y verifica la misión de inicio de sesión diario.
*   `Pausar (botón en línea)`: Este botón, que aparece durante la narrativa, permite pausar la historia. (Implementado como un `callback_data` `pause_story`).