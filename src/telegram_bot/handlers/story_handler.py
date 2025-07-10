import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from typing import Dict, Optional
from src.services.story_service import StoryService
from src.services.persona_service import PersonaService

logger = logging.getLogger(__name__)
router = Router()

class StoryHandler:
    """
    Handler for managing interactive story flow in the Telegram bot.
    
    This handler manages story progression, user choices, and the integration
    between story content and Diana's persona system.
    """
    
    def __init__(self, story_service: StoryService, persona_service: PersonaService):
        """
        Initialize the StoryHandler with required services.
        
        Args:
            story_service: Service for accessing story content
            persona_service: Service for managing Diana's persona
        """
        self.story_service = story_service
        self.persona_service = persona_service
    
    async def start_story(self, message: Message, context) -> None:
        """
        Start the interactive story from the beginning.
        
        Args:
            message: Telegram message that triggered the story start
            context: Bot context for managing state
        """
        user_id = message.from_user.id
        
        try:
            # Get the initial story node
            initial_node_id = self.story_service.get_initial_node()
            logger.info(f"Starting story for user {user_id} with node: {initial_node_id}")
            
            # Store current node in database (fictional function as specified)
            await update_current_node_in_db(user_id, initial_node_id)
            
            # Send the initial node
            await self._send_node(user_id, initial_node_id, context, message)
            
        except Exception as e:
            logger.error(f"Error starting story for user {user_id}: {e}")
            await message.answer(
                "❌ Hubo un error al iniciar la historia. Por favor, inténtalo de nuevo más tarde.",
                reply_markup=ReplyKeyboardRemove()
            )
    
    async def handle_choice(self, message: Message, context) -> None:
        """
        Handle a user's choice during story progression.
        
        Args:
            message: Telegram message containing the user's choice
            context: Bot context for managing state
        """
        user_id = message.from_user.id
        user_choice = message.text
        
        try:
            # Get current node from database (fictional function as specified)
            current_node_id = await get_current_node_from_db(user_id)
            
            if not current_node_id:
                await message.answer(
                    "❌ No hay una historia activa. Usa /historia para comenzar.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return
            
            # Get current node data
            current_node = self.story_service.get_node(current_node_id)
            if not current_node:
                logger.error(f"Current node {current_node_id} not found for user {user_id}")
                await message.answer(
                    "❌ Error en la historia. Iniciando desde el principio...",
                    reply_markup=ReplyKeyboardRemove()
                )
                await self.start_story(message, context)
                return
            
            # Find the matching choice
            selected_choice = None
            for choice in current_node.get('choices', []):
                if choice['text'] == user_choice:
                    selected_choice = choice
                    break
            
            if not selected_choice:
                # Invalid choice, show current node again
                await message.answer(
                    "❌ Opción no válida. Por favor, elige una de las opciones disponibles:"
                )
                await self._send_node(user_id, current_node_id, context, message)
                return
            
            # Apply choice effects to Diana's state
            effects = selected_choice.get('impact', {})
            if effects:
                await self.persona_service.apply_choice_effects(user_id, effects)
                logger.info(f"Applied effects {effects} for user {user_id}")
            
            # Get next node
            next_node_id = selected_choice.get('next_scene')
            if next_node_id:
                # Update current node in database
                await update_current_node_in_db(user_id, next_node_id)
                
                # Send next node
                await self._send_node(user_id, next_node_id, context, message)
            else:
                # Story ends here
                diana_state = await self.persona_service.get_diana_state(user_id)
                await message.answer(
                    f"🌙 Historia completada.\n\n"
                    f"Estado final de Diana: {diana_state}\n\n"
                    f"¡Gracias por jugar! Usa /historia para comenzar de nuevo.",
                    reply_markup=ReplyKeyboardRemove()
                )
                # Clear current node from database
                await update_current_node_in_db(user_id, None)
            
        except Exception as e:
            logger.error(f"Error handling choice for user {user_id}: {e}")
            await message.answer(
                "❌ Error procesando tu elección. Por favor, inténtalo de nuevo.",
                reply_markup=ReplyKeyboardRemove()
            )
    
    async def _send_node(self, user_id: int, node_id: str, context, message: Message) -> None:
        """
        Send a story node to the user with available choices.
        
        Args:
            user_id: ID of the user receiving the node
            node_id: ID of the story node to send
            context: Bot context for managing state
            message: Message object to respond to
        """
        try:
            # Get node data
            node = self.story_service.get_node(node_id)
            if not node:
                logger.error(f"Node {node_id} not found")
                await message.answer(
                    "❌ Error cargando el contenido de la historia.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return
            
            # Prepare the message text
            story_text = node['text']
            
            # Create keyboard with choices if available
            choices = node.get('choices', [])
            if choices:
                # Create reply keyboard with choice buttons
                keyboard_buttons = []
                for choice in choices:
                    button = KeyboardButton(text=choice['text'])
                    keyboard_buttons.append([button])
                
                # Add a "Pausar Historia" button
                keyboard_buttons.append([KeyboardButton(text="⏸ Pausar Historia")])
                
                keyboard = ReplyKeyboardMarkup(
                    keyboard=keyboard_buttons,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
                
                await message.answer(story_text, reply_markup=keyboard)
                logger.info(f"Sent node {node_id} with {len(choices)} choices to user {user_id}")
                
            else:
                # No choices - end of this path
                await message.answer(story_text, reply_markup=ReplyKeyboardRemove())
                logger.info(f"Sent final node {node_id} to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending node {node_id} to user {user_id}: {e}")
            await message.answer(
                "❌ Error mostrando el contenido de la historia.",
                reply_markup=ReplyKeyboardRemove()
            )

# Fictional database functions as specified in requirements
async def get_current_node_from_db(user_id: int) -> Optional[str]:
    """
    Fictional function to get current story node from database.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Current node ID if found, None otherwise
    """
    # This would typically query a database table for user's current story position
    # For now, this is a placeholder as specified in requirements
    logger.info(f"Getting current node from DB for user {user_id}")
    return None

async def update_current_node_in_db(user_id: int, node_id: Optional[str]) -> None:
    """
    Fictional function to update current story node in database.
    
    Args:
        user_id: ID of the user
        node_id: New current node ID, or None to clear
    """
    # This would typically update a database table with user's current story position
    # For now, this is a placeholder as specified in requirements
    logger.info(f"Updating current node in DB for user {user_id} to {node_id}")
