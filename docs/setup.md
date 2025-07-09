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

## 5. Gestión del Esquema de la Base de Datos (Fase de Desarrollo)

En esta fase de desarrollo inicial, el esquema de la base de datos se gestiona directamente a través de SQLAlchemy. Cada vez que el bot se inicia, se intentará crear todas las tablas definidas en `src/database/models.py` si no existen. Esto es útil para un desarrollo rápido donde el esquema cambia constantemente y no hay datos que preservar.

**Importante:** Si realizas cambios en los modelos y necesitas que se reflejen en la base de datos, deberás asegurarte de que las tablas antiguas sean eliminadas antes de iniciar el bot. Esto se puede hacer manualmente o, si `init_db()` está configurado para `drop_all` temporalmente, se hará automáticamente.

Una vez que el esquema esté más estable y se necesite preservar datos, se integrará una herramienta de migración como Alembic.

## 6. Estructura de Modelos

Los modelos de la base de datos están definidos en `src/database/models.py`.

---

**Fase 0 Completada.** El entorno está listo para comenzar el desarrollo del núcleo de la aplicación.