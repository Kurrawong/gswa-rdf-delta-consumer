# SQL Database Trigger for the Event Table

This service publishes all rows as events to the `rdf-delta-events` topic in service bus if the `EventPublished` column is set to `FALSE`.

Note that the database function app trigger is not supported on the flex consumption plan. See https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#considerations.

This function app has been tested with the App Service plan.

## Configuration

The following environment variables need to be set on the azure function app for python 3.11.

| variable                   | example value                                                                                                                                                                                     | description                                                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS                | Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;                                                                                              | service bus connection string                                                                                                 |
| TOPIC_NAME                 | rdf-delta-events                                                                                                                                                                                  | name of service bus topic                                                                                                     |
| SESSION_ID                 | main                                                                                                                                                                                              | service bus session identifier. needs to be the same value as set <br> in the `SHUI_SERVICE_BUS__SESSION_ID` variable in #137 |
| WS                         | true                                                                                                                                                                                              | whether to use amqp over websockets                                                                                           |
| SqlConnectionString        | Server=tcp:gswa-rdf-delta-events.database.windows.net,1433;Database=rdf-delta;Uid=...;Pwd=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;TrustServerCertificate=True;            | connection string for the database used by the function trigger                                                               |
| SQL_CONNECTION_STRING_ODBC | Driver={ODBC Driver 18 for SQL Server};Server=tcp:gswa-rdf-delta-events.database.windows.net,1433;Database=rdf-delta;Uid=...;Pwd=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30; | connection string for the database - requires the ODBC Driver to be 17 for python 3.10 and 18 for python 3.11                 |

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
    "SQL_CONNECTION_STRING_ODBC": "Driver={ODBC Driver 17 for SQL Server};Server=tcp:gswa-rdf-delta-events.database.windows.net,1433;Database=rdf-delta;Uid=...;Pwd=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
    "SERVICE_BUS": "Endpoint=sb://gswaservicebus.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...",
    "TOPIC_NAME": "rdf-delta-events",
    "SESSION_ID": "main",
    "WS": "false"
  },
  "ConnectionStrings": {}
}
```

Start the function by running `task dev`.
