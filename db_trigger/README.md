# SQL Database Trigger for the Event Table

This service publishes all rows as events to the `rdf-delta-events` topic in service bus if the `EventPublished` column is set to `FALSE`.

## Local Development

Create a `.env` file in this directory with the same values from `.env-template`.

Start the function by running `task dev`.
