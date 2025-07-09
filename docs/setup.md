# Guía de Configuración del Entorno

Este documento detalla los pasos para configurar el entorno de desarrollo de DianaBot.

## 1. Requisitos Previos

- Python 3.10+
- Git
- Una base de datos PostgreSQL en ejecución.

## 2. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd dianabotfull
```

## 3. Configurar Variables de Entorno

Copia el archivo de ejemplo `.env.example` a un nuevo archivo llamado `.env`.

```bash
cp .env.example .env
```

Edita el archivo `.env` y añade tus credenciales de base de datos y el token de tu bot de Telegram.

```
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST/DATABASE
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234567890
```

## 4. Crear Entorno Virtual e Instalar Dependencias

Estos comandos crearán un entorno virtual de Python, lo activarán e instalarán todas las dependencias necesarias.

```bash
python -m venv venv
source venv/bin/activate

# En Windows, usa:
# venv\Scripts\activate

pip install -r requirements.txt
```

## 5. Configurar y Ejecutar Migraciones de Base de Datos

El proyecto utiliza Alembic para gestionar el esquema de la base de datos. La configuración ya está hecha para leer la `DATABASE_URL` desde tu archivo `.env`.

Para verificar que la conexión funciona, puedes ejecutar:

```bash
# Asegúrate de que tu entorno virtual esté activado
venv/bin/alembic current
```

Si todo está correcto, no debería mostrar ningún error. Para aplicar el esquema inicial a tu base de datos, necesitarás generar y aplicar una migración (esto se cubrirá en la Fase 1 del desarrollo).

## 6. Estructura de Modelos

Los modelos de la base de datos están definidos en `src/database/models.py`. La configuración de Alembic en `migrations/env.py` ya está apuntando a estos modelos para la autogeneración de migraciones.

---

**Fase 0 Completada.** El entorno está listo para comenzar el desarrollo del núcleo de la aplicación.
