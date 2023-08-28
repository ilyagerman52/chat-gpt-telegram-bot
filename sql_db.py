from enum import Enum
from dataclasses import dataclass
import sqlite3
import datetime
import time

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


class UserStatus(Enum):
    """
    Class for user status.
    """
    ADMIN = 0
    USER = 1
    BLOCKED = 2
    VIP = 3
    CUSTOM = 4  # maybe it will be added later


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
    username: str
    parse_mode: str or None
    status: UserStatus
    key: str or None


class Database:
    def __init__(self):
        self.users_table_path = "users.sql"
        self.chat_tables = "chats/"
        users = sqlite3.connect(self.users_table_path)
        users.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INT,
                username TEXT,
                status INT,
                parse_mode TEXT,
                key_ TEXT,
                table_name TEXT
            )
        """)
        users.commit()

    def add_profile(self, profile: Profile):
        """
        Create new line in main table for new user. Fill all fields according to parameter `profile`.

        :param profile: information about user
        :type profile: Profile
        :return: 0 if success else 1
        :rtype: int
        """
        users = sqlite3.connect(self.users_table_path)
        table_time = str(datetime.datetime.now())
        users.cursor()
        users.execute(f"""SELECT ({profile.user_id}, 
                                  {profile.username},
                                  {profile.status},
                                  {profile.parse_mode},
                                  {profile.key})
                           INSERT INTO users""")
        users.commit()
        new_profile_history = sqlite3.connect(f'profiles/{profile.user_id}.sql')
        new_profile_history.cursor()
        table_name = str(profile.user_id) + table_time
        new_profile_history.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
                role INT,
                text TEXT,
                datetime TEXT
            )
        """)

    def update_profile(self, user_id: int, field: Field, value: str or None) -> int:
        """
        Update profile by user id. In main table for user updates value of one field.

        :param user_id: id of user, which profile must be updated
        :type user_id: int
        :param field: the field of profile, that must be updated
        :type field: Field
        :param value: new value of field, that must be updated
        :type value: str or None
        :return: 0 if success else 1
        :rtype: int
        """
        raise NotImplementedError()


def get_profile(user_id: int) -> Profile:
    """
    Load profile by user id and return it.

    :param user_id: id of user
    :type user_id: int
    :return: profile of user with id = user_id
    :rtype: Profile
    """
    raise NotImplementedError()


def add_message_chat(user_id: int, msg: ChatMessage) -> int:
    """
    Add message to chat history for user by id.

    :param user_id: id of user whose chat history must be updated
    :type user_id: int
    :param msg: message content
    :type msg: ChatMessage
    :return: 0 if success else 1
    :rtype: int
    """
    history_table_name =
    raise NotImplementedError()


def get_chat_history(user_id: int) -> list:
    """
    Load chat history saved in database by user id.

    :param user_id: id of user whose chat history must be loaded
    :return: chat history
    :rtype: list[ChatMessage]
    """
    raise NotImplementedError()


def clear_chat_history(user_id: int) -> int:
    """
    Clear chat history for user by his id.

    :param user_id: id of user
    :type user_id: int
    :return: 0 if success else 1
    :rtype: int
    """
    raise NotImplementedError()
