# GSWA RDF Delta Services

This repository contains several microservices that make up the GSWA RDF Delta Services.

## Services Overview

### Event Persistence Consumer

Source code: [event_persistence_consumer](event_persistence_consumer)

A function app service bus consumer.

The consumer consumes events from the `rdf-delta` topic and persists them in the event store in SQL Managed Instance. The service bus subscription is named `event-persistence-consumer`.

### SQL Database Trigger

Source code: [db_trigger](db_trigger)

A SQL database function trigger. The function runs when updates are made to the `Event` table in the `rdf_delta` database.

If the `EventPublished` column is set to `FALSE`, the function will publish the event to the `rdf-delta-events` topic in service bus.

### RDF Delta Consumer

Source code: [rdf_delta_consumer](rdf_delta_consumer)

A function app service bus consumer.

The consumer consumes events from the `rdf-delta-events` topic, processes them, and sends them to the RDF Delta Server or Fuseki SPARQL Update endpoint.

## Local Development

The recommended way to do development is to use (VS Code with the Dev Container extension)[https://code.visualstudio.com/docs/devcontainers/containers].

Before doing anything, first create a `.env` file in the `.devcontainer` directory. Copy the contents of the `.env-template` file into the `.env` file and fill in the values. Note that this same database password needs to be set for any dependent services that connect to the database.

Now, open the project in VS Code and search for "Dev Containers: Rebuild and Reopen in Container" in the Command Palette. This will build the dev container and reopen the project in the container using the docker engine. By using this method, you can ensure your dev environment has all of the necessary dependencies and tools installed to develop with Azure Functions and Azure SQL Managed Instance.

You will now have all of the .NET dependencies required to run a local instance of SQL Server along with go-task and uv for managing python.

Last step before developing, click on the extensions tab to ensure all of the extensions are loaded. Some may say the window needs to be reloaded. Click it to allow it to reload and initialise correctly.

> [!NOTE]
> A warning from the Azure extension may appear to complain that it has found multiple function apps in the one project. Just ignore this, we are not using any features from the extension for functions.

### Local SQL Server

The local SQL Server is running in a docker container when the dev container starts. An easy way to view the database is to use the `ms-mssql` extension in VS Code. Once installed, you can connect to the local SQL Server by opening the SQL Server view.

Right-clicking on `LocalDev` will allow you to lodge a SQL query to test your connection. Paste the following query in, right-click the file window and click "Execute Query".

```sql
SELECT name
FROM sys.tables
```

### sqlcmd

Alternatively, you can use the `sqlcmd` command to connect to the local SQL Server.

```bash
sqlcmd -S localhost -U sa -P password
```

For example, to drop a database.

```sql
DROP DATABASE rdf_delta;
GO
```

Use the `-d` flag to specify the database when connecting using `sqlcmd`.

```bash
sqlcmd -S localhost -U sa -P password -d rdf_delta
```
