# GSWA RDF Delta Consumer

This function consumes from a "sessionful" service bus topic, processes a message
(RDF, RDF Patch Log or SPARQL Update queries) and sends it to the RDF Delta Server or Fuseki SPARQL Update endpoint.

In a future iteration, it will integrate with Olis and do some message processing before sending it off to the target services.

This repository is deployed as an azure function app on python 3.11.

## Setting up the topic

Create a new topic `rdf-delta-events`. No need to check any additional settings. Message ordering is enforced by using sessions in the consumer (subscriber).

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

| variable                 | example value                                                                                        | description                                                 |
| ------------------------ | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| SERVICE_BUS              | Endpoint=sb://gswaservicebus.servicebus.windows.net/;SharedAccessKeyName=testSAP;SharedAccessKey=... | service bus connection string                               |
| SERVICE_BUS_TOPIC        | rdf-delta-events                                                                                     | name of service bus topic                                   |
| SERVICE_BUS_SUBSCRIPTION | rdf-delta-events-consumer                                                                            | name of service bus subscription                            |
| RDF_DELTA_URL            | https://myrdfdeltaserver.azurewebsites.net                                                           | url for rdf delta server                                    |
| RDF_DELTA_DATASOURCE     | ds                                                                                                   | datasource name to submit patch logs to in rdf delta server |

## Local Development

### Setting Up

Create a local.settings.json file and copy the example data into it.

```json
{
  "IsEncrypted": false,
  "Values": {
    "SERVICE_BUS": "Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
    "SERVICE_BUS_SUBSCRIPTION": "rdf-delta-events-consumer",
    "SERVICE_BUS_TOPIC": "rdf-delta-events",
    "RDF_DELTA_URL": "http://rdf-delta-server:1066",
    "RDF_DELTA_DATASOURCE": "ds",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  },
  "ConnectionStrings": {}
}
```

Populate the `SERVICE_BUS` value with the connection string for service bus. Update the other values as needed.

For more information, refer to [this article](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#local-settings)
for information about configuring local app settings.

### Running

Start the local function app.

```bash
func start
```
