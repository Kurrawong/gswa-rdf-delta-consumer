# Event Persistence Consumer

This function consumes from a "sessionful" service bus topic, processes a message
(RDF, RDF Patch Log or SPARQL Update queries) and sends it to the RDF Delta Server or Fuseki SPARQL Update endpoint.

In a future iteration, it will integrate with Olis and do some message processing before sending it off to the target services.

This repository should be deployed as an azure function app.

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

| variable             | example value                                                                                                                    | description                                                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS          | Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true; | service bus connection string                                                                                                 |
| TOPIC_NAME           | rdf-delta                                                                                                                        | name of service bus topic                                                                                                     |
| SUBSCRIPTION_NAME    | event-persistence-consumer                                                                                                       | name of service bus subscription                                                                                              |
| SESSION_ID           | main                                                                                                                             | service bus session identifier. needs to be the same value as set <br> in the `SHUI_SERVICE_BUS__SESSION_ID` variable in #137 |
| RDF_DELTA_URL        | https://myrdfdeltaserver.azurewebsites.net                                                                                       | url for rdf delta server                                                                                                      |
| RDF_DELTA_DATASOURCE | ds                                                                                                                               | datasource name to submit patch logs to in rdf delta server                                                                   |
| SqlConnectionString  | DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;                                   | connection string for the database                                                                                            |

## Local Development

### Setting Up

Create a local.settings.json file and copy the example data into it.

```json
{
  "IsEncrypted": false,
  "Values": {
    "SERVICE_BUS": "Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
    "SERVICE_BUS_SUBSCRIPTION": "event-persistence-consumer",
    "SERVICE_BUS_TOPIC": "rdf-delta",
    "SESSION_ID": "main",
    "RDF_DELTA_URL": "http://rdf-delta-server:1066",
    "RDF_DELTA_DATASOURCE": "ds",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "SqlConnectionString": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;"
  },
  "ConnectionStrings": {}
}

```

Populate the `SERVICE_BUS` value with the connection string for service bus. Update the other values as needed.

For more information, refer to [this article](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#local-settings)
for information about configuring local app settings.

### Running

Before starting the function app, initialise the database by running the init.py script.

```bash
python init.py
```

Start the local function app.

```bash
func start
```
