import sqlite3
import typing as tp


class DataBase:
    def __init__(self, name: str, path: str) -> None:
        self._name = name
        self._path = path
        self._connection: sqlite3.Connection = self._connect()
        self.tables: dict[str, Table] = {}
        self.init_db()

    def init_db(self):
        self.tables['profiles'] = Table(
            'profiles',
            self,
            schema={
                'uid': 'int',
                'username': 'text',
                'first_name': 'text',
                'last_name': 'text',
                'full_name': 'text',
                'premium_flg': 'boolean',
            }
        )
        self.tables['history'] = Table(
            'history',
            self,
            schema={
                'uid': 'int',
                'content': 'text',
                'is_bot_response': 'boolean',
                'dttm': 'text',
                'message_id': 'int',
            }
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        return connection

    def _run(self, query: str) -> list[tp.Any]:
        cursor = self._connection.cursor()
        data = cursor.execute(query)
        self._connection.commit()
        return data.fetchall()

    @property
    def connection(self):
        return self._connection


class Table:
    def __init__(self, name: str, db: DataBase, schema: dict[str, str] | None = None) -> None:
        self._name = name
        self._db = db
        self._schema: dict[str, type] = schema if schema else {}
        self.create_table()

    def create_table(self):
        query = 'CREATE TABLE IF NOT EXISTS ' + self._name + ' (' + \
                ', '.join(map(lambda x: f"{x[0]} {x[1]}", self.schema.items())) + ')'
        self._run(query)

    def add_row(self, row):
        query = f"INSERT INTO {self.name} {tuple(row.keys())} values {tuple(row.values())}"
        self._run(query)

    def _run(self, query: str) -> tp.Any:
        connection = self.connection
        data = connection.cursor().execute(query)
        connection.commit()
        return data

    def get_data(self, condition="True", fields='*'):
        if isinstance(fields, list):
            fields = ", ".join(fields)
        query = f"""SELECT {fields} FROM {self.name} where {condition}"""
        return self._run(query)

    def delete_data(self, condition="False"):
        query = f"""DELETE FROM {self.name} where {condition}"""
        self._run(query)

    @property
    def schema(self):
        return self._schema

    @property
    def name(self):
        return self._name

    @property
    def connection(self):
        return self._db.connection
