# SQL Database Trigger for the Event Table

This service publishes all rows as events to the `rdf-delta-events` topic in service bus if the `EventPublished` column is set to `FALSE`.

## Local Development

Create a `.env` file in this directory with the same values from `.env-template`.

Start the function by running `task dev`.

## Configuration

The following environment variables need to be set on the azure function app.

| variable            | example value                                                                                                              | description                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS         | Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;                       | service bus connection string                                                                                                 |
| TOPIC_NAME          | rdf-delta-events                                                                                                           | name of service bus topic                                                                                                     |
| SESSION_ID          | main                                                                                                                       | service bus session identifier. needs to be the same value as set <br> in the `SHUI_SERVICE_BUS__SESSION_ID` variable in #137 |
| WS                  | true                                                                                                                       | whether to use websockets for service bus                                                                                     |
| SqlConnectionString | DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;TrustServerCertificate=True; | connection string for the database                                                                                            |
