import logging

import pyodbc
import pytest

from event_persistence_consumer.database import (
    Database,
    delete_database,
    get_connection,
)
from event_persistence_consumer.settings import settings

logger = logging.getLogger(__name__)


@pytest.fixture
def master_connection(request: pytest.FixtureRequest):
    connection = get_connection(
        settings.mssql_server,
        settings.mssql_master_database,
        settings.mssql_username,
        settings.mssql_password,
    )

    def cleanup():
        logger.debug(
            f"Cleaning up database connection to {settings.mssql_master_database}"
        )
        delete_database(connection, settings.mssql_database)
        connection.close()

    request.addfinalizer(cleanup)
    return connection


@pytest.fixture
def database(request: pytest.FixtureRequest, master_connection: pyodbc.Connection):
    _database = Database(
        settings.mssql_server,
        settings.mssql_database,
        settings.mssql_master_database,
        settings.mssql_username,
        settings.mssql_password,
    )

    def cleanup():
        logger.debug(f"Cleaning up database connection to {settings.mssql_database}")
        _database.close()

        # Force close all connections before dropping
        master_connection.autocommit = True
        with master_connection.cursor() as cursor:
            cursor.execute(f"""
                ALTER DATABASE {settings.mssql_database}
                SET SINGLE_USER
                WITH ROLLBACK IMMEDIATE;
            """)
        master_connection.autocommit = False
        delete_database(master_connection, settings.mssql_database)

    request.addfinalizer(cleanup)
    return _database
