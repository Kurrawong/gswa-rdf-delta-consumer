# RDF Delta Consumer

## Overview

This function consumes from a "sessionful" service bus topic, processes a message
(RDF, RDF Patch Log or SPARQL Update queries) and sends it to RDF Delta Server.

## Deployment

### Pre-requisites

- Service Bus topic with a sessionful subscription
- RDF Delta Server

### Create the function app

1. Create a function app with the Python 3.12 runtime.

### Deploy the code

1. Deploy the function app code to the function app.

This can be done in a number of ways. including via devops pipeline or
the azure functions core tools cli.

### Configure the function app

#### Environment variables

| variable                       | example value                                            | description                                                   |
| ------------------------------ | -------------------------------------------------------- | ------------------------------------------------------------- |
| SERVICE_BUS                    | Endpoint=...;SharedAccessKeyName=...;SharedAccessKey=... | service bus connection string                                 |
| SERVICE_BUS_TOPIC              | my-second-topic                                          | name of service bus topic to consume from                     |
| SERVICE_BUS_SUBSCRIPTION       | my-second-topic-sub                                      | name of service bus subscription (must have sessions enabled) |
| RDF_DELTA_URL                  | https://myrdfdeltaserver.azurewebsites.net               | url for rdf delta server                                      |
| RDF_DELTA_DATASOURCE           | myds                                                     | datasource name to submit patch logs to in rdf delta server   |

## Development

Environment variables should be set in the `local.settings.json` file (not kept in
version control).

Python dependencies are managed with the `requirements.txt` file and can be installed
with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Using the core tools cli you can start and test the function app locally by running

```bash
func start
```
