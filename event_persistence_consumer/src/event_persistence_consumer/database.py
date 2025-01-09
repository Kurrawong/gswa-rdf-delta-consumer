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
    connection_str: str,
) -> pyodbc.Connection:
    """Get a db connection."""
    connection = pyodbc.connect(connection_str)
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


def enable_database_change_tracking(
    connection: pyodbc.Connection, database: str, retention_in_days: int = 2
) -> None:
    """Enable change tracking on the database."""
    with connection.cursor() as cursor:
        connection.autocommit = True
        cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.change_tracking_databases WHERE database_id = DB_ID('{database}'))
            BEGIN
                ALTER DATABASE {database}
                SET CHANGE_TRACKING = ON
                (CHANGE_RETENTION = {retention_in_days} DAYS, AUTO_CLEANUP = ON)
            END
        """)
        connection.autocommit = False


def enable_table_change_tracking(connection: pyodbc.Connection, table: str) -> None:
    """Enable change tracking on the table."""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            IF NOT EXISTS (SELECT * FROM sys.change_tracking_tables WHERE object_id = OBJECT_ID('{table}'))
            BEGIN
                ALTER TABLE {table}
                ENABLE CHANGE_TRACKING
                WITH (TRACK_COLUMNS_UPDATED = ON)
            END
        """)


class EventTable:
    """The event table over a db connection."""

    def __init__(self, connection: pyodbc.Connection) -> None:
        self.connection = connection

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

    def mark_as_unpublished(self, from_event_id: int) -> None:
        """Mark all events with an EventID greater than the given event ID as unpublished."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Event SET EventPublished = 'FALSE' WHERE EventID > ?",
                from_event_id,
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
    it does not exist. It will also enable change tracking on the database.
    """

    def __init__(
        self,
        connection_str: str,
    ) -> None:
        self.connection = get_connection(connection_str)

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()
