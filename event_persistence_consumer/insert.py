from event_persistence_consumer.database import Database, EventTable
from event_persistence_consumer.settings import settings

with Database(settings.sql_connection_string) as db:
    table = EventTable(db.connection)
    table.insert(
        {"id": "123", "type": "test"},
        "test",
    )
