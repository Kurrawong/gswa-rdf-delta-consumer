import json
import logging
from contextlib import ContextDecorator, contextmanager
from typing import Iterator

import pyodbc

logger = logging.getLogger(__name__)


@contextmanager
def get_connection_manager(
    server: str, database: str, username: str, password: str
) -> Iterator[pyodbc.Connection]:
    """Get a db connection using a context manager."""
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = None
    try:
        connection = pyodbc.connect(connection_string)
        logger.debug(f"Connected to {database} on {server}")
        yield connection
    finally:
        if connection is not None:
            connection.close()
            logger.debug(f"Closed connection to {database} on {server}")


def get_connection(
    server: str, database: str, username: str, password: str
) -> pyodbc.Connection:
    """Get a db connection."""
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    logger.debug(f"Connected to {database} on {server}")
    return connection


def create_database_if_not_exists(connection: pyodbc.Connection, database: str) -> None:
    """Create a database if not exists.

    :param connection: The connection to the master database.
    :param database: The name of the database to create.
    """
    with connection.cursor() as cursor:
        connection.autocommit = True
        cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{database}')
            BEGIN
                CREATE DATABASE {database};
            END
        """)
        connection.autocommit = False


def get_databases(connection: pyodbc.Connection) -> list[str]:
    """Get a list of all databases."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name
            FROM sys.databases
        """)
        rows = cursor.fetchall()
        return [row.name for row in rows]


def delete_database(connection: pyodbc.Connection, database: str) -> None:
    """Delete a database if exists."""
    with connection.cursor() as cursor:
        connection.autocommit = True
        cursor.execute(f"""
            IF EXISTS (SELECT * FROM sys.databases WHERE name = '{database}')
            BEGIN
                DROP DATABASE {database};
            END
        """)
        connection.autocommit = False


def get_tables(connection: pyodbc.Connection) -> list[str]:
    """Get a list of all tables."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name
            FROM sys.tables
        """)
        rows = cursor.fetchall()
        return [row.name for row in rows]


def create_event_table_if_not_exists(connection: pyodbc.Connection) -> None:
    """Create the Event table if not exists."""
    with connection.cursor() as cursor:
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Event')
            BEGIN
                CREATE TABLE Event (
                    EventID BIGINT IDENTITY(1,1) PRIMARY KEY,
                    EventHeader NVARCHAR(4000),
                    EventBody NVARCHAR(MAX),
                    EventPublished BIT DEFAULT 'FALSE'
                )
            END
        """)


class EventTable:
    """The event table over a db connection."""

    def __init__(self, connection: pyodbc.Connection) -> None:
        self.connection = connection
        create_event_table_if_not_exists(self.connection)

    def insert(self, header: dict, body: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Event (EventHeader, EventBody)
                VALUES (?, ?)
            """,
                json.dumps(header),
                body,
            )

    def get(self, event_id: int) -> tuple[int, dict, str, bool]:
        """Get an event by id.

        :raises ValueError: If the event is not found.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EventID, EventHeader, EventBody, EventPublished
                FROM Event
                WHERE EventID = ?
            """,
                event_id,
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Event {event_id} not found")
            return (
                row.EventID,
                json.loads(row.EventHeader),
                row.EventBody,
                row.EventPublished,
            )

    def mark_as_published(self, event_id: int) -> None:
        """Mark an event as published."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE Event
                SET EventPublished = 'TRUE'
                WHERE EventID = ?
            """,
                event_id,
            )

    def get_unpublished_events(self) -> list[tuple[int, dict, str]]:
        """Get a list of all unpublished events sorted by EventID."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT EventID, EventHeader, EventBody
                FROM Event
                WHERE EventPublished = 'FALSE'
                ORDER BY EventID
            """)
            rows = cursor.fetchall()
            return [
                (row.EventID, json.loads(row.EventHeader), row.EventBody)
                for row in rows
            ]


class Database(ContextDecorator):
    """A MS SQL Server database abstraction over a connection.

    On instantiation, it will use the master connection to create the db if
    it does not exist.
    """

    def __init__(
        self,
        server: str,
        database: str,
        master_database: str,
        username: str,
        password: str,
    ) -> None:
        self.database = database

        with get_connection_manager(
            server, master_database, username, password
        ) as master_connection:
            create_database_if_not_exists(master_connection, database)

        self.connection = get_connection(server, database, username, password)

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()
