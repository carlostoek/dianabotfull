import pytest
from unittest.mock import MagicMock, patch
import datetime

# Set up paths for test environment
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from services.mission_service import MissionService
from telegram_bot.handlers.mission_handler import mission_command_handler, claim_mission_callback_handler
from telegram_bot.menus.mission_menu import create_mission_layout

# A mock missions file for consistent testing
TEST_MISSIONS_PATH = 'data/missions.json' # Assuming the main missions file is fine for testing

@pytest.fixture
def mock_update():
    """Creates a mock Telegram Update object."""
    update = MagicMock()
    update.effective_user.id = 123
    update.effective_user.username = 'testuser'
    return update

@pytest.fixture
def mock_context():
    """Creates a mock Telegram CallbackContext object."""
    context = MagicMock()
    context.bot = MagicMock()
    return context

@pytest.fixture
def mission_service():
    """Provides a clean MissionService instance for each test."""
    # Using the actual missions file, assuming it's present.
    # For more isolated tests, a temporary file could be created.
    return MissionService(missions_path=TEST_MISSIONS_PATH)

def test_mission_command_flow(mission_service, mock_update, mock_context):
    """
    Tests the full flow of a user requesting a mission with the /mision command.
    """
    # Patch the service instance used by the handler
    with patch('telegram_bot.handlers.mission_handler.mission_service', mission_service):
        # 1. User sends /mision
        mission_command_handler(mock_update, mock_context)

        # 2. Verify the service was called to get a mission
        mission = mission_service.get_daily_mission(mock_update.effective_user.id)
        assert mission is not None
        assert mission['id'] is not None

        # 3. Verify that a message was sent back with a keyboard
        text, keyboard = create_mission_layout(mission)
        mock_update.message.reply_text.assert_called_once()
        
        # Check that the text and keyboard match what the menu would generate
        call_args = mock_update.message.reply_text.call_args
        assert call_args[0][0] == text
        assert call_args[1]['reply_markup'] is not None
        assert "Reclamar Recompensa" in str(call_args[1]['reply_markup'].inline_keyboard)

def test_claim_mission_callback_flow(mission_service, mock_update, mock_context):
    """
    Tests the full flow of a user claiming a mission reward via a callback.
    """
    with patch('telegram_bot.handlers.mission_handler.mission_service', mission_service):
        # 1. First, assign a mission to the user
        mission = mission_service.get_daily_mission(mock_update.effective_user.id)
        assert mission is not None
        assert not mission['completed']

        # 2. Simulate the user clicking the "Claim" button
        callback_data = f"claim_mission_{mission['id']}"
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.from_user.id = mock_update.effective_user.id
        mock_update.callback_query.data = callback_data
        
        # 3. Patch the placeholder function for adding rewards
        with patch('telegram_bot.handlers.mission_handler._add_besitos_to_user') as mock_add_besitos:
            claim_mission_callback_handler(mock_update, mock_context)

            # 4. Verify the reward was given
            mock_add_besitos.assert_called_once_with(mock_update.effective_user.id, mission['reward'])

        # 5. Verify the message was edited to show completion
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "¡Felicidades!" in call_args[0][0]
        assert "✅ Completada" in call_args[0][0]

        # 6. Verify the mission is now marked as completed in the service
        updated_mission = mission_service.get_daily_mission(mock_update.effective_user.id)
        assert updated_mission['completed']

def test_claim_already_completed_mission(mission_service, mock_update, mock_context):
    """
    Tests that a user cannot claim a mission twice on the same day.
    """
    with patch('telegram_bot.handlers.mission_handler.mission_service', mission_service):
        # 1. Assign and complete a mission
        mission = mission_service.get_daily_mission(mock_update.effective_user.id)
        mission_service.complete_mission(mock_update.effective_user.id, mission['id'])
        assert mission_service.get_daily_mission(mock_update.effective_user.id)['completed']

        # 2. Simulate the user clicking the button again
        callback_data = f"claim_mission_{mission['id']}"
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.from_user.id = mock_update.effective_user.id
        mock_update.callback_query.data = callback_data

        claim_mission_callback_handler(mock_update, mock_context)

        # 3. Verify the message indicates the mission cannot be claimed
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "no se puede reclamar" in call_args[0][0]
