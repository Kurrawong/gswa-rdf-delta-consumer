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
    # table.mark_as_published(5)
    with table.connection.cursor() as cursor:
        event_id = 0
        cursor.execute(
            "UPDATE Event SET EventPublished = 'FALSE' WHERE EventID > ?", event_id
        )
