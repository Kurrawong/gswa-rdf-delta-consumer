# Event Persistence Consumer

This function consumes from a "sessionful" service bus topic, processes a message and persists it to a SQL Database.

## Setting up the topic

Create a new topic `rdf-delta`. No need to check any additional settings. Message ordering is enforced by using sessions in the consumer (subscriber).

## Deployment

Deployment can be done from the command line using the
[azure-functions-core-tools](https://github.com/Azure/azure-functions-core-tools) library.

To deploy you need to have created a function app and then run the following command:

```bash
func azure functionapp fetch-app-settings <app_name>
func azure functionapp publish <app_name>
```

After deployment you then need to set the below configuration options and restart the
app.

### Configuration

The following environment variables need to be set on the azure function app.

| variable                 | example value                                                                                  | description                                                                                 |
| ------------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| SERVICE_BUS_TOPIC        | rdf-delta                                                                                      | name of service bus topic                                                                   |
| SERVICE_BUS_SUBSCRIPTION | event-persistence-consumer                                                                     | name of service bus subscription                                                            |
| SqlConnectionString      | DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!; | connection string for the database - ensure the driver is included in the connection string |
| FUNCTIONS_WORKER_RUNTIME | python                                                                                         | runtime for the function app                                                                |

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

Start the local function app.

```bash
func start
```

## Local Development

### Setting Up

```json
{
  "IsEncrypted": false,
  "Values": {
    "SERVICE_BUS": "Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
    "SERVICE_BUS_SUBSCRIPTION": "event-persistence-consumer",
    "SERVICE_BUS_TOPIC": "rdf-delta",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "SqlConnectionString": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;"
  },
  "ConnectionStrings": {}
}
```

For more information, refer to [this article](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#local-settings)
for information about configuring local app settings.

### Local Dev Env Vars

The `.env` file is used to set the environment variables for the local development environment.

The `SERVICE_BUS` value is only used by the `sb_producer.py` script.

The `SqlConnectionString` value is used by the `init_db.py` script.
