from contextlib import contextmanager

import pyodbc


@contextmanager
def get_db_connection():
    # Connection parameters
    server = 'localhost,1433'  # Update with your server name and port
    database = 'master'  # Replace with your database name
    username = 'sa'  # Replace with your username
    password = 'P@ssw0rd!'  # Replace with your password

    # Establishing the connection
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(connection_string)

    try:
        yield conn
    finally:
        conn.close()


def get_tables(cursor: pyodbc.Cursor) -> list[pyodbc.Row]:
    cursor.execute("""
        SELECT name
        FROM sys.tables
    """)
    rows = cursor.fetchall()
    return rows


def create_tables(cursor: pyodbc.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Event (
            EventID BIGINT IDENTITY(1,1) PRIMARY KEY,
            EventHeader
        )
    """)


def main():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            tables = get_tables(cursor)
            print(tables)
            print(tables[0].name)
            print(("spt_monitor",) in tables)


if __name__ == "__main__":
    main()

