# Diagrama de Entidad-Relación (Schema)

Este documento describe la arquitectura de la base de datos de DianaBot en formato Mermaid.

```mermaid
erDiagram
    USER {
        Integer id PK "Telegram User ID"
        String username
        String role
        Integer points
        DateTime vip_expires_at
    }

    USER_PROGRESS {
        Integer user_id PK, FK
        String diana_state
        String dominant_archetype
        JSON secondary_archetypes
        Float resonance_score
        DateTime last_interaction_at
        String current_story_node
        JSON unlocked_fragments
    }

    MISSION {
        Integer id PK
        String name UK
        String description
        Integer reward_points
    }

    USER_MISSION {
        Integer user_id PK, FK
        Integer mission_id PK, FK
        DateTime completed_at PK
    }

    ACHIEVEMENT {
        Integer id PK
        String name UK
        String description
    }

    USER_ACHIEVEMENT {
        Integer user_id PK, FK
        Integer achievement_id PK, FK
        DateTime unlocked_at
    }

    USER ||--o{ USER_MISSION : has
    MISSION ||--o{ USER_MISSION : is_completed_in

    USER ||--o{ USER_ACHIEVEMENT : has
    ACHIEVEMENT ||--o{ USER_ACHIEVEMENT : is_unlocked_in

    USER ||--|| USER_PROGRESS : has_one
```

### Descripción de Relaciones

- **USER - USER_PROGRESS (Uno a Uno):** Cada usuario tiene un único registro de progreso que almacena su estado narrativo y de personalidad. La clave primaria de `USER_PROGRESS` es también una clave foránea a `USER`.

- **USER - USER_MISSION (Uno a Muchos):** Un usuario puede completar muchas misiones. `USER_MISSION` es la tabla intermedia que registra qué misión completó un usuario y cuándo.

- **MISSION - USER_MISSION (Uno a Muchos):** Una misión puede ser completada por muchos usuarios.

- **USER - USER_ACHIEVEMENT (Uno a Muchos):** Un usuario puede desbloquear muchos logros. `USER_ACHIEVEMENT` registra los logros de cada usuario.

- **ACHIEVEMENT - USER_ACHIEVEMENT (Uno a Muchos):** Un logro puede ser obtenido por muchos usuarios.
