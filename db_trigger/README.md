# SQL Database Trigger for the Event Table

This service publishes all rows as events to the `rdf-delta-events` topic in service bus if the `EventPublished` column is set to `FALSE`.

Note that the database function app trigger is not supported on the flex consumption plan. See https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#considerations.

This function app has been tested with the App Service plan deployed in the Canada Central region. Some configuration settings are not supported in the Australian regions.

## Configuration

The following environment variables need to be set on the azure function app for python 3.11.

| variable               | example value                                                                                                                                                                          | description                                                                                                                   |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS            | Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;                                                                                   | service bus connection string                                                                                                 |
| SERVICE_BUS_TOPIC      | rdf-delta-events                                                                                                                                                                       | name of service bus topic                                                                                                     |
| SERVICE_BUS_SESSION_ID | main                                                                                                                                                                                   | service bus session identifier. needs to be the same value as set <br> in the `SHUI_SERVICE_BUS__SESSION_ID` variable in #137 |
| USE_AMQP_OVER_WS       | true                                                                                                                                                                                   | whether to use amqp over websockets                                                                                           |
| SqlConnectionString    | Server=tcp:gswa-rdf-delta-events.database.windows.net,1433;Database=rdf-delta;Uid=...;Pwd=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;TrustServerCertificate=True; | connection string for the database used by the function trigger                                                               |

### Running

Once the SQL Database has been created, in the Query Editor, run the following.

Enable database change tracking.

```sql
IF NOT EXISTS (SELECT * FROM sys.change_tracking_databases WHERE database_id = DB_ID('rdf-delta'))
BEGIN
    ALTER DATABASE [rdf-delta]
    SET CHANGE_TRACKING = ON
    (CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON)
END
```

Create the table.

```sql
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Event')
BEGIN
    CREATE TABLE Event (
        EventID BIGINT IDENTITY(1,1) PRIMARY KEY,
        EventHeader NVARCHAR(4000),
        EventBody NVARCHAR(MAX),
        EventPublished BIT DEFAULT 'FALSE'
    )
END
```

Enable table change tracking.

```sql
IF NOT EXISTS (SELECT * FROM sys.change_tracking_tables WHERE object_id = OBJECT_ID('Event'))
BEGIN
    ALTER TABLE [Event]
    ENABLE CHANGE_TRACKING
    WITH (TRACK_COLUMNS_UPDATED = ON)
END
```

## Local Development

### Local settings

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "WEBSITE_SITE_NAME": "db-trigger",
    "SqlConnectionString": "Server=tcp:gswa-rdf-delta-events.database.windows.net,1433;Database=rdf-delta;Uid=...;Pwd=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
    "SERVICE_BUS": "Endpoint=sb://gswaservicebus.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...",
    "SERVICE_BUS_TOPIC": "rdf-delta-events",
    "SERVICE_BUS_SESSION_ID": "main",
    "USE_AMQP_OVER_WS": "false"
  },
  "ConnectionStrings": {}
}
```

Start the function by running `task dev`.

### Deploy test function app to Azure

```bash
task deploy
```
