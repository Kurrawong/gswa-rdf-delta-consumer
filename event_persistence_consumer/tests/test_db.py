import pytest

from event_persistence_consumer.database import (
    Database,
    EventTable,
    create_database_if_not_exists,
    get_databases,
    get_tables,
)
from event_persistence_consumer.settings import settings


def test_settings():
    assert settings.mssql_database == "rdf_delta"


def test_db_connection(master_connection):
    assert master_connection is not None


def test_create_database_if_not_exists(master_connection):
    databases = get_databases(master_connection)
    assert settings.mssql_database not in databases
    create_database_if_not_exists(master_connection, settings.mssql_database)
    databases = get_databases(master_connection)
    assert settings.mssql_database in databases


def test_database_class(database):
    # This connection is valid.
    get_tables(database.connection)


def test_event_table_class(database):
    EventTable(database.connection)
    tables = get_tables(database.connection)
    assert "Event" in tables


def test_event_table_insert(database):
    insert_header = {"foo": "bar"}
    insert_body = "baz"
    table = EventTable(database.connection)
    table.insert(insert_header, insert_body)

    event_id, event_header, event_body, event_published = table.get(1)
    assert event_id == 1
    assert event_header == insert_header
    assert event_body == insert_body
    assert event_published is False

    # Mark as published
    table.mark_as_published(1)
    event_id, event_header, event_body, event_published = table.get(1)
    assert event_published is True


def test_event_table_get_not_exist_row(database):
    table = EventTable(database.connection)
    with pytest.raises(ValueError):
        table.get(1)


def test_event_table_get_unpublished_events(database):
    table = EventTable(database.connection)
    table.insert({"foo": "bar"}, "baz")
    table.insert({"foo": "bar"}, "baz")
    table.insert({"foo": "bar"}, "baz")
    assert len(table.get_unpublished_events()) == 3

    table.mark_as_published(1)
    assert len(table.get_unpublished_events()) == 2


def test_database_context_manager():
    with Database(
        settings.mssql_server,
        settings.mssql_database,
        settings.mssql_master_database,
        settings.mssql_username,
        settings.mssql_password,
    ) as db:
        assert db.connection is not None
