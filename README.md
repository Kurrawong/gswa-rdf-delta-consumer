# GSWA RDF Delta Consumer

This function consumes from a "sessionful" service bus topic, processes a message
(RDF, RDF Patch Log or SPARQL Update queries) and sends it to the RDF Delta Server or Fuseki SPARQL Update endpoint.

In a future iteration, it will integrate with Olis and do some message processing before sending it off to the target services.

This repository should be deployed as a containerized azure function app.

> [!NOTE]
> The function_app.py script contains the code from https://github.com/Kurrawong/rdf-delta-python/
> because that package has a dependency on python 3.12 but function apps only support up
> to 3.11. It may be better in the future to modify the dependency of rdf-delta-python
> to allow 3.11, I have tested locally and it works fine. And then the package can be
> pip installed instead of duplicating its code here.

## Deployment

1. Build the docker image
2. push to ACR
3. create a function app with container image source and use the pushed image.
4. set the environment variables as below
5. restart the app

| variable             | example value                              | description                                                                                                                   |
| -------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| SERVICE_BUS          | Endpoint=sb.//...                          | service bus connection string                                                                                                 |
| TOPIC_NAME           | my-topic                                   | name of service bus topic                                                                                                     |
| SUBSCRIPTION_NAME    | my-sub                                     | name of service bus subscription                                                                                              |
| SESSION_ID           | main                                       | service bus session identifier. needs to be the same value as set <br> in the `SHUI_SERVICE_BUS__SESSION_ID` variable in #137 |
| RDF_DELTA_URL        | https://myrdfdeltaserver.azurewebsites.net | url for rdf delta server                                                                                                      |
| RDF_DELTA_DATASOURCE | myds                                       | datasource name to submit patch logs to in rdf delta server                                                                   |

## Local Development

You can run the generated docker image locally, with the above environment variables set
for testing.
