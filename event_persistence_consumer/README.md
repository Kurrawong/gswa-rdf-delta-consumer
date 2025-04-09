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

The following environment variables need to be set on the azure function app for python 3.11.

| variable                 | example value                                                                                                                                                     | description                                                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS              | Endpoint=sb://myservicebus.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...                                                                    | service bus connection string                                                                                                 |
| SERVICE_BUS_TOPIC        | mysb-topic                                                                                                                                                        | name of service bus topic                                                                                                     |
| SERVICE_BUS_SUBSCRIPTION | mysb-sub                                                                                                                                                          |
| SqlConnectionString      | Driver={ODBC Driver 18 for SQL Server};Server=tcp:myazuresql.database.windows.net,1433;Database=mydb;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30; | connection string for the database, azure default credential will be used, so no need to specify the Authentication parameter |

## Local Development

### Setting Up

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SERVICE_BUS": "Endpoint=sb://myservicebus.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...",
    "SERVICE_BUS_SUBSCRIPTION": "mysb-sub",
    "SERVICE_BUS_TOPIC": "mysb-topic",
    "SqlConnectionString": "DRIVER={ODBC Driver 18 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;"
  },
  "ConnectionStrings": {}
}
```

For more information, refer to [this article](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#local-settings)
for information about configuring local app settings.

### Start the local function app.

```bash
task dev
```

### Local Dev Env Vars

The `.env` file is used to set the environment variables for the local development environment.

The `SERVICE_BUS` value is only used by the `sb_producer.py` script.

The `SqlConnectionString` value is used by the `init_db.py` script.

### Deploy test function app to Azure

```bash
task deploy
```
