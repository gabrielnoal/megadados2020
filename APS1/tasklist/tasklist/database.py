# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
import json
import uuid

from functools import lru_cache

import mysql.connector as conn

from fastapi import Depends

from utils.utils import get_config_filename, get_app_secrets_filename, is_valid_uuid

from .models import Task, User


class DBSession:
    def __init__(self, connection: conn.MySQLConnection):
        self.connection = connection

    def read_tasks(self, completed: bool = None, user_uuid: uuid.UUID = None):
        query = 'SELECT BIN_TO_UUID(uuid), description, completed FROM tasks'
        if completed is not None:
            query += ' WHERE completed = '
            if completed:
                query += 'True'
            else:
                query += 'False'

        if is_valid_uuid(user_uuid):
            query += f' {"AND" if completed is not None else ""} WHERE user_uuid = UUID_TO_BIN(%s)'

        with self.connection.cursor() as cursor:
            cursor.execute(query, user_uuid)
            db_results = cursor.fetchall()

        return {
            uuid_: Task(
                description=field_description,
                completed=bool(field_completed),
            )
            for uuid_, field_description, field_completed in db_results
        }

    def create_task(self, item: Task):
        uuid_ = str(uuid.uuid4())

        query = 'INSERT INTO tasks (uuid, description, completed) VALUES (UUID_TO_BIN(%s), %s, %s)'
        variables = (
          uuid_,
          item.description,
          item.completed
          )

        with self.connection.cursor() as cursor:
            cursor.execute(query, variables)
        self.connection.commit()

        return uuid_

    def read_task(self, uuid_: uuid.UUID):
        if not self.__task_exists(uuid_):
            raise KeyError()

        query = "SELECT description, completed FROM tasks WHERE uuid = UUID_TO_BIN(%s)"
        variables = (str(uuid_), )

        with self.connection.cursor() as cursor:
            cursor.execute(query,variables)

            result = cursor.fetchone()

        return Task(description=result[0], completed=bool(result[1]))

    def replace_task(self, uuid_, item):
        if not self.__task_exists(uuid_):
            raise KeyError()

        query = " UPDATE tasks SET description=%s, completed=%s"
        if 'user_uuid' in item:
          query += 'user_uuid=UUID_TO_BIN(%s)'
        query += " WHERE uuid=UUID_TO_BIN(%s)"
        variables = (item.description, item.completed, str(uuid_), item.user_uuid)
    
        with self.connection.cursor() as cursor:
            cursor.execute(query,variables)
        self.connection.commit()

    def remove_task(self, uuid_):
        if not self.__task_exists(uuid_):
            raise KeyError()

        query = "DELETE FROM tasks WHERE uuid=UUID_TO_BIN(%s)"
        variables = (str(uuid_), )

        with self.connection.cursor() as cursor:
            cursor.execute(query, variables)
        self.connection.commit()

    def remove_all_tasks(self):
        query = 'DELETE FROM tasks'
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def __task_exists(self, uuid_: uuid.UUID):
        query ='SELECT EXISTS(SELECT 1 FROM tasks WHERE uuid=UUID_TO_BIN(%s))'
        variables = (str(uuid_), )
        with self.connection.cursor() as cursor:
            cursor.execute(query, variables)
            results = cursor.fetchone()
            found = bool(results[0])

        return found

    def create_user(self, item: User):
        user_uuid = str(uuid.uuid4())
        query = "INSERT INTO users VALUES (UUID_TO_BIN(%s), %s)"
        variables = (user_uuid, item.name)
        with self.connection.cursor() as cursor:
            cursor.execute(query, variables,)
        self.connection.commit()

        return user_uuid

    def delete_user(self, user_uuid):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE user_uuid=UUID_TO_BIN(%s)",
                (user_uuid),
            )
        self.connection.commit()

        return 200

    def update_user(self, name: str, user_uuid):
        query = "UPDATE users SET name=%s WHERE user_uuid=UUID_TO_BIN(%s)"
        variables = (name, user_uuid)

        with self.connection.cursor() as cursor:
            cursor.execute(query, variables)
        self.connection.commit()

        return 200

    def read_user(self, user_uuid):
        query = "SELECT name FROM users WHERE user_uuid=UUID_TO_BIN(%s)"
        variables = (user_uuid, )
        with self.connection.cursor() as cursor:
            cursor.execute(query, variables)
        self.connection.commit()
        result = cursor.fetchone()

        return User(name=result[0])


@lru_cache(None)
def get_credentials(
        config_file_name: str = Depends(get_config_filename),
        secrets_file_name: str = Depends(get_app_secrets_filename),
):
    with open(config_file_name, 'r') as file:
        config = json.load(file)
    with open(secrets_file_name, 'r') as file:
        secrets = json.load(file)
    return {
        'user': secrets['user'],
        'password': secrets['password'],
        'host': config['db_host'],
        'database': config['database'],
    }


def get_db(credentials: dict = Depends(get_credentials)):
    try:
        connection = conn.connect(**credentials)
        yield DBSession(connection)
    finally:
        connection.close()
