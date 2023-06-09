from enum import Enum
from dataclasses import dataclass
import sqlite3
from datetime import datetime

from typing import List


class Field(Enum):
    """
    Enum class for fields of tables.

    It might be expanded with different others parameters.
    """
    USER_ID = 0
    USERNAME = 1
    PARSE_MODE = 2
    STATUS = 3
    KEY = 4
    NUMBER_OF_REQUESTS = 5  # maybe it must be in other place
    LAST_ACTIVITY = 6  # maybe it must be in other place


class ParseMode(Enum):
    """
    Class with ParseMode available values.
    """
    EMPTY = None
    HTML = "HTML"
    MARKDOWN = "Markdown"


class UserStatus(Enum):
    """
    Class for user status.
    """
    ADMIN = 0
    USER = 1


@dataclass
class ChatMessage:
    """
    Class for chat message.
    """
    role: str
    content: str
    dt: datetime


@dataclass
class Profile:
    """
    Class for profile of user.
    """
    user_id: int
    username: int
    parse_mode: ParseMode
    status: UserStatus
    key: str


def update_profile(user_id: int, field: Field, value: ParseMode) -> int:
    """
    Update profile by user id. In main table for user updates value of one field.

    :param user_id: id of user, which profile must be updated
    :type user_id: int
    :param field: the field of profile, that must be updated
    :type field: Field
    :param value: new value of field, that must be updated
    :type value: ParseMode
    :return: 0 if success else 1
    :rtype: int
    """
    raise NotImplementedError


def add_profile(profile: Profile) -> int:
    """
    Create new line in main table for new user. Fill all fields according to parameter `profile`.

    :param profile: information about user
    :type profile: Profile
    :return: 0 if success else 1
    :rtype: int
    """
    raise NotImplementedError


def get_profile(user_id: int) -> Profile:
    """
    Load profile by user id and return it.

    :param user_id: id of user
    :type user_id: int
    :return: profile of user with id = user_id
    :rtype: Profile
    """
    raise NotImplementedError


def add_message_chat(user_id: int, message: ChatMessage) -> int:
    """
    Add message to chat history for user by id.

    :param user_id: id of user whose chat history must be updated
    :type user_id: int
    :param message: message content
    :type message: ChatMessage
    :return: 0 if success else 1
    :rtype: int
    """
    raise NotImplementedError


def get_chat_history(user_id: int) -> list:
    """
    Load chat history saved in database by user id.

    :param user_id: id of user whose chat history must be loaded
    :return: chat history
    :rtype: list[ChatMessage]
    """
    raise NotImplementedError


def clear_chat_history(user_id: int) -> int:
    """
    Clear chat history for user by his id.

    :param user_id: id of user
    :type user_id: int
    :return: 0 if success else 1
    :rtype: int
    """
    raise NotImplementedError
