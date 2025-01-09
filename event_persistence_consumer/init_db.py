from event_persistence_consumer.database import (
    Database,
    create_database_if_not_exists,
    create_event_table_if_not_exists,
    enable_database_change_tracking,
    enable_table_change_tracking,
    get_connection,
)
from event_persistence_consumer.settings import settings

db_name = "rdf_delta"
master_connection_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=master;UID=sa;PWD=P@ssw0rd!;"

connection = get_connection(master_connection_str)
create_database_if_not_exists(connection, db_name)
enable_database_change_tracking(connection, db_name)

_database = Database(
    settings.sql_connection_string,
)
create_event_table_if_not_exists(_database.connection)
enable_table_change_tracking(_database.connection, "Event")

_database.close()
connection.close()
