from event_persistence_consumer.database import Database, EventTable
from event_persistence_consumer.settings import settings

with Database(
    settings.mssql_server,
    settings.mssql_database,
    settings.mssql_master_database,
    settings.mssql_username,
    settings.mssql_password,
) as db:
    table = EventTable(db.connection)
    table.insert(
        {"id": "123", "type": "test"},
        "test",
    )