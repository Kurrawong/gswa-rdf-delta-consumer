# Event Persistence Consumer

## Overview

This function consumes from a "sessionful" service bus topic, processes a message and persists it to a SQL Database.

## Deployment

### Pre-requisites

- Service Bus topic with a sessionful subscription
- Azure SQL Database and Event Table

### Create the function app

1. Create a function app with the Python 3.12 runtime.
2. Enable the System Managed Identity for the app.

### Configure the Azure SQL Database

1. Add the app as a user to the Azure SQL Database and assign the necessary permissions

```sql
CREATE USER [<identity-name>] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [<identity-name>];
ALTER ROLE db_datawriter ADD MEMBER [<identity-name>];
GRANT VIEW CHANGE TRACKING ON [Event] TO [<identity-name>];
```

> where \<identity-name> is the name of the managed identity in Microsoft Entra ID.
> If the identity is system-assigned, the name is always the same as the name of the
> function app.

### Deploy the code

1. Deploy the function app code to the function app.

This can be done in a number of ways. including via devops pipeline or
the azure functions core tools cli.

### Configure the function app

#### Environment variables

| variable                 | example value                                                                                                               | description                                                                                                                                                                                                                                      |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SERVICE_BUS              | Endpoint=...;SharedAccessKeyName=...;SharedAccessKey=...                                                                    | service bus connection string                                                                                                                                                                                                                    |
| SERVICE_BUS_TOPIC        | my-topic                                                                                                                    | name of service bus topic to consume from                                                                                                                                                                                                        |
| SERVICE_BUS_SUBSCRIPTION | my-topic-sub                                                                                                                | name of service bus subscription to use (must have sessions enabled)                                                                                                                                                                             |
| SqlConnectionString      | Driver={ODBC Driver 18 for SQL Server};Server=...;Database=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30; | Azure SQL connection string. Driver must be specified and Authentication must not be specified. The function code will automatically acquire a token for the apps system managed identity and use that for authentication to Azure SQL Database. |

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
