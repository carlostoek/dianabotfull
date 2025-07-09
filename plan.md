# Plan de Implementación de Funcionalidades en @dianabotfull

Este documento detalla las funciones identificadas en el proyecto @Botmaestro2 y una hoja de ruta progresiva para su implementación en el sistema @dianabotfull.

## Funciones de @Botmaestro2 Categorizadas

### 1: Administración de Canales

*   **Configuración de Canales:**
    *   Configurar reacciones y puntos para canales VIP y Gratuitos (`admin_config_reactions`, `process_reactions_input`, `process_points_input`, `save_reaction_buttons_callback`).
    *   Añadir y gestionar IDs de canales VIP/Gratuitos (`channels_menu`, `prompt_add_channel`, `receive_vip_channel`, `receive_free_channel`).
    *   Configurar tiempo de espera para solicitudes de unión al canal gratuito (`set_wait_time_menu`, `set_wait_time`).
    *   Eliminar un canal configurado (`remove_channel`).
    *   Gestión integral del canal gratuito (solicitudes de unión, publicación de contenido, limpieza) (`configure_free_channel`, `process_free_channel_id`, `set_wait_time_menu`, `set_wait_time_value`, `create_invite_link`, `send_to_free_channel_menu`, `process_post_text`, `add_media_prompt`, `process_media_files`, `continue_without_media`, `confirm_and_send_post`, `process_pending_now`, `cleanup_old_requests`).
    *   Enviar mensajes con botones interactivos a canales (`send_interactive_post`).
    *   Gestionar y actualizar reacciones en publicaciones de canales (`register_reaction`, `get_reaction_counts`, `update_reaction_markup`).
    *   Gestionar configuraciones de canales (IDs, botones de reacción, puntos de reacción) (`ConfigService`).
    *   Servicios de canales (añadir/listar/eliminar canales, configurar reacciones) (`ChannelService`).
    *   Servicios específicos del canal gratuito (`FreeChannelService`).
    *   Tareas programadas para solicitudes de canal y limpieza (`channel_request_scheduler`, `run_channel_request_check`, `free_channel_cleanup_scheduler`, `run_free_channel_cleanup`).

*   **Gestión de Suscripciones y Usuarios:**
    *   Generar tokens VIP (`admin_generate_token_cmd`, `generate_token_callback`, `vip_generate_token`, `vip_create_token`, `vip_invalidate_token`).
    *   Gestionar suscriptores VIP (añadir días, expulsar, ver perfil, editar expiración) (`manage_subs`, `vip_add_days`, `vip_kick`, `vip_profile`, `vip_edit`, `process_add_days`, `process_edit_date`).
    *   Gestionar tarifas de suscripción VIP (`config_tarifas`, `tariff_options`, `start_edit_tariff`, `edit_tariff_duration`, `edit_tariff_price`, `finish_edit_tariff`, `start_new_tarifa`, `tariff_duration_selected`, `tariff_price`, `tariff_name`, `delete_tariff`).
    *   Manejar enlaces profundos para activación de tokens (`start_with_token`).
    *   Servicios de suscripción (crear/obtener/extender/revocar suscripciones) (`SubscriptionService`).
    *   Servicios de tokens (crear/activar/invalidar tokens) (`TokenService`).
    *   Configuración y configuración multi-tenant (`TenantService`).
    *   Gestión de usuarios (`UserService`).

### 2: Gamificación

*   **Puntos y Niveles:**
    *   Gestión de puntos (añadir/deducir, obtener, top usuarios) (`PointService`).
    *   Otorgar puntos por actividades (mensajes, reacciones, encuestas, check-in diario) (`award_message`, `award_reaction`, `award_poll`, `daily_checkin`).
    *   Gestión de niveles (obtener nivel, verificar subida de nivel, crear/actualizar/eliminar niveles) (`LevelService`).
    *   Gestión de usuarios y sus puntos por parte del administrador (`admin_manage_users`, `admin_users_page`, `admin_user_add`, `admin_user_deduct`, `process_points_amount`, `admin_view_user`, `admin_search_user`, `process_search_user`).
    *   Gestión de niveles por parte del administrador (`admin_content_levels`, `admin_levels_view`, `admin_level_add`, `level_add_number`, `level_add_name`, `level_add_points`, `level_add_reward`, `confirm_create_level`, `admin_level_edit`, `start_edit_level`, `edit_level_number`, `edit_level_name`, `edit_level_points`, `edit_level_reward`, `finish_edit_level`, `admin_level_delete`, `confirm_del_level`, `delete_level`).
    *   Mostrar el nivel actual del usuario (`show_user_level`).
    *   Información sobre cómo ganar puntos (`gain_points`).

*   **Misiones y Desafíos:**
    *   Gestión de misiones y desafíos (obtener/completar/crear misiones, actualizar progreso) (`MissionService`).
    *   Mostrar misiones disponibles a los usuarios (`show_available_missions`).
    *   Gestión de misiones por parte del administrador (`admin_content_missions`, `admin_start_create_mission`, `admin_process_mission_name`, `admin_process_mission_description`, `admin_select_mission_type`, `admin_process_target`, `admin_process_reward`, `admin_process_duration`, `admin_toggle_mission_menu`, `toggle_mission_status`, `admin_view_active_missions`, `admin_delete_mission_menu`, `admin_confirm_delete_mission`, `admin_delete_mission`).
    *   Interacción del usuario con misiones (`handle_mission_details_callback`, `handle_complete_mission_callback`).
    *   Funcionalidad de check-in diario (`handle_daily_checkin`).

*   **Recompensas:**
    *   Gestión de recompensas (obtener/reclamar/crear/actualizar/eliminar recompensas) (`RewardService`).
    *   Interacción del usuario con recompensas (`rewards_command`, `handle_claim_reward_callback`).
    *   Gestión de recompensas por parte del administrador (`admin_content_rewards`, `admin_reward_add`, `process_reward_name`, `process_reward_points`, `process_reward_description`, `process_reward_type`, `admin_reward_view`, `admin_reward_delete`, `confirm_delete_reward`, `delete_reward`, `admin_reward_edit`, `start_edit_reward`, `edit_reward_name`, `edit_reward_points`, `edit_reward_description`, `edit_reward_type`, `finish_edit_reward`).

*   **Insignias y Logros:**
    *   Gestión de logros (verificar/otorgar logros) (`AchievementService`).
    *   Gestión de insignias (crear/listar/eliminar/otorgar insignias) (`BadgeService`).
    *   Asignar insignias manualmente a usuarios (`vip_manual_badge`, `process_manual_badge_user`, `assign_manual_badge`).
    *   Gestión de insignias por parte del administrador (`admin_content_badges`, `admin_create_badge`, `badge_name_step`, `badge_description_step`, `badge_requirement_step`, `badge_emoji_step`, `admin_view_badges`, `admin_delete_badge`, `select_badge`, `confirm_delete_badge`).
    *   Mostrar insignias del usuario (`vip_badges`).

*   **Subastas:**
    *   Lógica central de subastas (crear/gestionar/pujar/finalizar/cancelar subastas) (`AuctionService`).
    *   Gestión de subastas por parte del administrador (`admin_auction_main`, `start_create_auction`, `process_auction_name`, `process_auction_description`, `process_auction_prize`, `process_auction_initial_price`, `process_auction_duration`, `confirm_create_auction`, `list_active_auctions`, `list_pending_auctions`, `manage_auction`, `confirm_end_auction`, `end_auction`, `confirm_cancel_auction`, `cancel_auction`, `auction_statistics`).
    *   Interacción del usuario con subastas (`auction_main_menu`, `view_active_auctions`, `view_auction_details`, `start_place_bid`, `quick_bid`, `custom_bid_amount`, `process_custom_bid`, `confirm_bid`, `cancel_bid`, `view_my_auctions`, `view_auction_history`, `toggle_notifications`).
    *   Tareas programadas para monitoreo de subastas (`auction_monitor_scheduler`, `run_auction_monitor_check`).

*   **Minijuegos:**
    *   Lógica de minijuegos (ruleta, desafíos de reacción) (`MinigameService`).
    *   Manejadores de minijuegos (ruleta, dados, trivia) (`play_roulette`, `start_reaction_challenge`, `play_dice`, `send_trivia`, `trivia_answer`).
    *   Gestión de minijuegos por parte del administrador (`admin_content_minigames`, `toggle_minigames`).
    *   Manejadores de trivia (`show_trivia_menu`, `start_trivia`, `send_next_question`, `handle_answer`).
    *   Gestión de trivia por parte del administrador (`admin_trivia_menu`, `list_trivias`, `create_trivia`, `trivia_title_received`, `total_questions_received`, `question_text_received`, `question_type_received`, `options_received`, `correct_answer_received`, `points_received`, `unlock_content_received`, `confirm_creation`).
    *   Servicio de trivia (`TriviaService`).

*   **Eventos y Sorteos:**
    *   Gestión de eventos (crear/listar/finalizar eventos) (`EventService`).
    *   Gestión de sorteos (crear/añadir entradas/listar/finalizar sorteos) (`RaffleService`).
    *   Gestión de eventos y sorteos por parte del administrador (`admin_events_main`, `event_menu`, `raffle_menu`, `start_create_event`, `process_event_name`, `process_event_description`, `finish_event_create`, `list_events`, `choose_event_end`, `finish_event`, `start_create_raffle`, `raffle_name`, `raffle_desc`, `raffle_finish`, `list_raffles`, `choose_raffle_end`, `finish_raffle`).

### 3: Narrativa

*   **Pistas y Lore:**
    *   Interfaz de usuario para la mochila narrativa (`mostrar_mochila_narrativa`, `mostrar_mochila_vacia`, `mostrar_categoria`, `ver_pista_detallada`, `mostrar_contenido_pista`, `volver_mochila`, `mostrar_estadisticas`, `mostrar_sugerencias_diana`).
    *   Desbloquear piezas narrativas (`desbloquear_pista_narrativa`, `desbloquear_pista`).
    *   Lógica para combinar pistas narrativas (`iniciar_combinacion_interactiva`, `seleccionar_pista_combinacion`, `procesar_combinacion_seleccionada`, `mostrar_exito_combinacion`, `mostrar_fallo_combinacion`, `verificar_combinaciones_disponibles`).
    *   Mostrar piezas de lore a los usuarios (`show_lore_backpack`, `show_lore_piece`).
    *   Gestión de piezas de lore por parte del administrador (`admin_manage_hints`, `admin_content_lore_pieces`, `lore_piece_page`, `lore_piece_view_details`, `lore_piece_delete_warning`, `lore_piece_confirm_delete`, `lore_piece_toggle_active`, `lore_piece_create_start`, `process_lore_code_name`, `process_lore_title`, `process_lore_description`, `process_lore_category`, `process_main_story`, `choose_content_type`, `save_text_content`, `_lore_piece_summary`, `lore_piece_edit`, `edit_lore_title_start`, `edit_lore_title`, `edit_lore_description_start`, `edit_lore_description`, `edit_lore_category_start`, `edit_lore_category`, `edit_lore_main_start`, `edit_lore_main`, `edit_lore_type_start`, `edit_lore_type`, `edit_lore_text_content`, `edit_lore_file_content`, `save_file_content`).
    *   Servicio de piezas de lore (`LorePieceService`).
    *   Otorgar fragmentos narrativos basados en puntos/misiones (`on_points_earned`, `on_mission_completed` en `RewardGateway`).
    *   Enviar notificaciones específicas de narrativa (`send_narrative_notification`).
    *   Manejar la combinación de pistas (versión basada en comandos) (`iniciar_combinacion`, `procesar_combinacion`).

## Hoja de Ruta para la Implementación en @dianabotfull

La implementación se realizará de manera progresiva, priorizando las funcionalidades base y expandiendo sobre ellas.

**Consideraciones Previas:**
*   Asegurar que el entorno de desarrollo de `@dianabotfull` esté configurado y sea funcional.
*   Familiarizarse con la estructura de `@dianabotfull` (módulos, servicios, handlers).
*   Establecer un sistema de control de versiones (Git) y trabajar en ramas separadas para cada fase/módulo.

**Fase 1: Gamificación Core y Narrativa Básica**

*   **Objetivo:** Establecer el ciclo fundamental de gamificación (puntos, niveles, misiones básicas) y la integración central de elementos narrativos (piezas de lore).
*   **Pasos:**
    1.  **Actualización de Modelos de Base de Datos:**
        *   Definir todos los modelos necesarios en `src/database/models.py` (LorePiece, UserLorePiece, HintCombination, UserStats, Mission, UserMissionEntry, Achievement, UserAchievement, Reward, UserReward, Level, VipSubscription, Event, Raffle, RaffleEntry, Badge, UserBadge, Auction, Bid, AuctionParticipant, MiniGamePlay, Trivia, TriviaQuestion, TriviaAttempt, TriviaUserAnswer, ConfigEntry, BotConfig, Channel, PendingChannelRequest, SubscriptionPlan, SubscriptionToken, Token, Tariff, ButtonReaction).
        *   Ejecutar migraciones o scripts de inicialización de DB para crear las tablas correspondientes.
    2.  **Servicios de Gamificación Básica:**
        *   Implementar `PointService` (añadir/deducir puntos, `award_message`, `award_reaction`, `award_poll`, `daily_checkin`).
        *   Implementar `LevelService` (obtener nivel, verificar subida de nivel, crear/actualizar/eliminar niveles).
        *   Implementar `MissionService` (obtener/completar/crear misiones, actualizar progreso).
    3.  **Servicios de Narrativa Básica:**
        *   Implementar `LorePieceService` (crear/obtener/actualizar/eliminar piezas de lore).
    4.  **Integración de Handlers y UI Básica:**
        *   Actualizar `handlers/main_menu.py` para incluir botones básicos de gamificación y narrativa (`Mochila`, `Billetera`, `Misiones`).
        *   Implementar `show_available_missions` en `handlers/missions_handler.py`.
        *   Implementar `show_lore_backpack` y `show_lore_piece` en `handlers/lore_handlers.py`.
        *   Implementar las funciones principales de la mochila narrativa en `backpack.py` (`mostrar_mochila_narrativa`, `mostrar_mochila_vacia`, `mostrar_categoria`, `ver_pista_detallada`, `mostrar_contenido_pista`, `volver_mochila`, `mostrar_estadisticas`, `mostrar_sugerencias_diana`).
        *   Implementar `desbloquear_pista` en `narrativa.py`.
        *   Implementar `send_narrative_notification` en `notificaciones.py`.
    5.  **Inicialización de Datos:**
        *   Actualizar `scripts/init_db.py` para inicializar las nuevas tablas y cargar datos por defecto (niveles, misiones básicas, algunas piezas de lore).

**Fase 2: Gamificación Avanzada y Administración de Canales**

*   **Objetivo:** Mejorar la gamificación con características más complejas (recompensas, logros, subastas) e implementar una administración de canales robusta.
*   **Pasos:**
    1.  **Servicios de Gamificación Avanzada:**
        *   Implementar `RewardService` (gestión de recompensas).
        *   Implementar `AchievementService` (gestión de logros).
        *   Implementar `BadgeService` (gestión de insignias).
        *   Implementar `AuctionService` (lógica central de subastas).
        *   Implementar `MinigameService` (lógica de minijuegos).
        *   Implementar `TriviaService` (lógica de trivia).
        *   Implementar `EventService` (gestión de eventos).
        *   Implementar `RaffleService` (gestión de sorteos).
    2.  **Servicios de Administración y Suscripciones:**
        *   Implementar `ChannelService` (añadir/eliminar canales, configurar reacciones).
        *   Implementar `ConfigService` (gestión de configuraciones del bot).
        *   Implementar `FreeChannelService` (servicios específicos del canal gratuito).
        *   Implementar `TokenService` (gestión de tokens VIP).
        *   Implementar `SubscriptionService` (gestión de suscripciones VIP).
        *   Implementar `TenantService` (configuración multi-tenant).
    3.  **Manejadores de Administración:**
        *   Implementar todos los manejadores de administración en `handlers/admin/` para usuarios, misiones, recompensas, niveles, insignias, subastas, eventos, sorteos, minijuegos, trivia, configuración de canales y planes de suscripción.
    4.  **Manejadores de Usuario VIP y Canales:**
        *   Implementar manejadores específicos de VIP en `handlers/vip/` para características de gamificación (recompensas, misiones, subastas, perfil).
        *   Implementar `handle_join_request` y `handle_chat_member` en `handlers/channel_access.py`.
        *   Implementar `claim_daily_gift` en `handlers/daily_gift.py`.
        *   Implementar manejadores de minijuegos en `handlers/minigames.py`.
        *   Implementar `handle_reaction_callback` en `handlers/reaction_callback.py`.
        *   Implementar el flujo de configuración inicial para administradores en `handlers/setup.py`.
        *   Implementar `start_with_token` en `handlers/user/start_token.py`.
    5.  **Tareas Programadas:**
        *   Implementar todos los planificadores en `services/scheduler.py` (`channel_request_scheduler`, `vip_subscription_scheduler`, `auction_monitor_scheduler`, `free_channel_cleanup_scheduler`).

**Fase 3: Profundización Narrativa y Refinamiento**

*   **Objetivo:** Profundizar la experiencia narrativa con combinaciones de pistas e integrar el sistema de personajes.
*   **Pasos:**
    1.  **Lógica de Combinación de Pistas:**
        *   Refinar la lógica de combinación de pistas y el contexto narrativo en `backpack.py`.
        *   Asegurar la integración completa de `combinar_pistas.py` con el sistema narrativo.
    2.  **Refinamiento General:**
        *   Asegurar que `utils/menu_factory.py` genere correctamente todos los nuevos menús.
        *   Asegurar que `utils/menu_manager.py` proporcione una navegación fluida en todas las nuevas características.
        *   Asegurar que `utils/user_roles.py` gestione correctamente el acceso basado en roles para todas las funcionalidades.
        *   Asegurar el formato de texto adecuado en `utils/text_utils.py` y `utils/message_utils.py`.
        *   Asegurar que las notificaciones de administrador funcionen correctamente en `utils/notify_admins.py`.
        *   Asegurar que la paginación funcione para todas las listas en `utils/pagination.py`.

---
