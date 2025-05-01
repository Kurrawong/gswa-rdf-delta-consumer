# Azure SQL Database Trigger

## Overview

This function app publishes rows from an Azure SQL database table called `Event`
to a service bus topic.

The `Event` table is populated with messages from the `event persistence consumer`
function.

The Event table maintains a record of which rows have been published
in the `EventPublished` column.

The function app is triggered by change events coming from the database table. And thus
change tracking must be enabled on the database and table to support triggering of this
function.

Instructions for creating and configuring the Azure SQL Database table are given below.

## Deployment

### Pre-requisites

- Azure SQL Database and Event Table
- Service Bus topic

### Create the function app

1. Create a function app with the Python 3.12 runtime and not the Flex Consumption
   hosting plan
2. Enable the System Managed Identity for the app.

### Configure the Azure SQL Database

1. Add the app as a user to the Azure SQL Database and assign the necessary permissions

```sql
CREATE USER [<identity-name>] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [<identity-name>];
ALTER ROLE db_datawriter ADD MEMBER [<identity-name>];
ALTER ROLE db_ddladmin ADD MEMBER [<identity-name>];
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

| variable                       | example value                                                                                                               | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SCM_DO_BUILD_DURING_DEPLOYMENT | true                                                                                                                        | enable remote builds                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ENABLE_ORYX_BUILD              | true                                                                                                                        | use oryx for remote build                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| SERVICE_BUS                    | Endpoint=...;SharedAccessKeyName=...;SharedAccessKey=...;                                                                   | service bus connection string                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| SERVICE_BUS_TOPIC              | my-second-topic                                                                                                             | name of service bus topic to publish events to                                                                                                                                                                                                                                                                                                                                                                                                                               |
| SERVICE_BUS_SESSION_ID         | main                                                                                                                        | service bus session identifier. needs to be the same value as set in KG CMS                                                                                                                                                                                                                                                                                                                                                                                                  |
| USE_AMQP_OVER_WS               | true                                                                                                                        | whether to use amqp over websockets for the service bus connection                                                                                                                                                                                                                                                                                                                                                                                                           |
| SqlConnectionString            | Server=...;Database=...;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=Active Directory Default | connection string for Azure SQL Database, `Authentication=Active Directory Default` will use the system managed identity of the function app to authenticate to the Azure SQL Database. **Note that the structure of this connection string is different to the one used in the event persistence consumer** (this is because the connection string is handled by the function app trigger and not the function app code, as is the case for the event persistence consumer) |

## Development

Environment variables should be set in the `local.settings.json` file (not kept in
version control).

> [!IMPORTANT]  
> You need to set the WEBSITE_SITE_NAME variable in the local.settings.json to run this
> function app locally. But this setting cannot be pushed to the deployed function app.

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
