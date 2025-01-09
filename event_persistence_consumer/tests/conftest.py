import logging

import pyodbc
import pytest

from event_persistence_consumer.database import (
    Database,
    create_database_if_not_exists,
    create_event_table_if_not_exists,
    delete_database,
    enable_database_change_tracking,
    enable_table_change_tracking,
    get_connection,
)
from event_persistence_consumer.settings import settings

logger = logging.getLogger(__name__)

db_name = "rdf_delta"
master_connection_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=master;UID=sa;PWD=P@ssw0rd!;"


@pytest.fixture
def master_connection(request: pytest.FixtureRequest):
    connection = get_connection(master_connection_str)

    def cleanup():
        connection.close()

    request.addfinalizer(cleanup)
    return connection


@pytest.fixture
def database(request: pytest.FixtureRequest, master_connection: pyodbc.Connection):
    create_database_if_not_exists(master_connection, db_name)
    enable_database_change_tracking(master_connection, db_name)

    _database = Database(
        settings.sql_connection_string,
    )
    create_event_table_if_not_exists(_database.connection)
    enable_table_change_tracking(_database.connection, "Event")

    def cleanup():
        logger.debug(f"Cleaning up database connection to {db_name}")
        _database.close()

        # Force close all connections before dropping
        master_connection.autocommit = True
        with master_connection.cursor() as cursor:
            cursor.execute(f"""
                ALTER DATABASE {db_name}
                SET SINGLE_USER
                WITH ROLLBACK IMMEDIATE;
            """)
        master_connection.autocommit = False
        delete_database(master_connection, db_name)

    request.addfinalizer(cleanup)
    return _database
