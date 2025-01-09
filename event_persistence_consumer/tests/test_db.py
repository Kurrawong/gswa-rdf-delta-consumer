import pytest

from event_persistence_consumer.database import (
    EventTable,
    get_tables,
)

db_name = "rdf_delta"


def test_db_connection(master_connection):
    assert master_connection is not None


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


def test_enable_database_change_tracking(database):
    with database.connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM sys.change_tracking_databases WHERE database_id = DB_ID('{db_name}')"
        )
        result = cursor.fetchone()
        assert result is not None


def test_enable_table_change_tracking(database):
    # Create the event table, which enables change tracking in the constructor.
    EventTable(database.connection)
    with database.connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM sys.change_tracking_tables WHERE object_id = OBJECT_ID('Event')"
        )
        result = cursor.fetchone()
        assert result is not None
