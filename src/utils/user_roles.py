# src/utils/user_roles.py
"""
A module for managing user roles in-memory.

This module provides a simple, non-persistent way to assign and retrieve user roles.
It is designed to be easily replaced with a more robust database-backed system
in the future without changing the function signatures.
"""
from typing import Dict

# In-memory database to store user roles.
# Key: user_id (int), Value: role (str)
USER_ROLES: Dict[int, str] = {}

def assign_role(user_id: int) -> None:
    """
    Assigns a default role to a user if they don't already have one.

    This function checks if the user already exists in the role mapping.
    If not, it assigns them the 'free_user' role.

    Args:
        user_id: The unique identifier for the user.
    """
    if user_id not in USER_ROLES:
        USER_ROLES[user_id] = "free_user"

def get_role(user_id: int) -> str:
    """
    Retrieves the role for a given user.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user's current role as a string, or 'free_user' if not found.
    """
    return USER_ROLES.get(user_id, "free_user")
