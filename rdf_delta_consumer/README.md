# GSWA RDF Delta Consumer

This function consumes from a "sessionful" service bus topic, processes a message
(RDF, RDF Patch Log or SPARQL Update queries) and sends it to the RDF Delta Server or Fuseki SPARQL Update endpoint.

In a future iteration, it will integrate with Olis and do some message processing before sending it off to the target services.

This repository should be deployed as an azure function app.

> [!NOTE]
> The function_app.py script contains the code from https://github.com/Kurrawong/rdf-delta-python/
> because that package has a dependency on python 3.12 but function apps only support up
> to 3.11. It may be better in the future to modify the dependency of rdf-delta-python
> to allow 3.11, and then the package can be pip installed instead of duplicating its code here.
> I have tested locally and it works fine. Not a huge issue as it is only a small amount
> of code.

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

| variable             | example value                              | description                                                                                                                   |
| -------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS          | Endpoint=sb.//...                          | service bus connection string                                                                                                 |
| TOPIC_NAME           | my-topic                                   | name of service bus topic                                                                                                     |
| SUBSCRIPTION_NAME    | my-sub                                     | name of service bus subscription                                                                                              |
| SESSION_ID           | main                                       | service bus session identifier. needs to be the same value as set <br> in the `SHUI_SERVICE_BUS__SESSION_ID` variable in #137 |
| RDF_DELTA_URL        | https://myrdfdeltaserver.azurewebsites.net | url for rdf delta server                                                                                                      |
| RDF_DELTA_DATASOURCE | myds                                       | datasource name to submit patch logs to in rdf delta server                                                                   |

## Local Development

### Setting Up

Create a local.settings.json file and copy the example data into it.

```json
{
  "IsEncrypted": false,
  "Values": {
    "SERVICE_BUS": "",
    "SERVICE_BUS_SUBSCRIPTION": "rdf-patch-consumer",
    "SERVICE_BUS_TOPIC": "rdf-patch-log",
    "SESSION_ID": "main",
    "RDF_DELTA_URL": "http://localhost:9999",
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
