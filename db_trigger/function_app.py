import json
import logging

import azure.functions as func
from event_persistence_consumer.database import Database, EventTable
from event_persistence_consumer.servicebus import Client
from event_persistence_consumer.settings import settings as event_persistence_settings

from db_trigger.settings import settings

app = func.FunctionApp()


@app.function_name(name="EventTrigger")
@app.sql_trigger(
    arg_name="event",
    table_name="Event",
    connection_string_setting="SqlConnectionString",
)
async def event_trigger(event: str) -> None:
    rows: list[dict] = json.loads(event)
    rows.sort(key=lambda x: x["Item"]["EventID"])

    async with Client(
        conn_str=settings.service_bus,
        topic=settings.topic_name,
        ws=settings.ws,
    ) as client:
        for row in rows:
            event_published = row["Item"]["EventPublished"]
            if event_published:
                logging.info(f"Event {row['Item']['EventID']} already published")
            else:
                logging.info(f"Publishing event {row['Item']['EventID']}")
                metadata = json.loads(row["Item"]["EventHeader"])
                logging.info(metadata)
                await client.send_message(
                    session_id=settings.session_id,
                    message=row["Item"]["EventBody"],
                    metadata=metadata,
                )
                print(event_persistence_settings.sql_connection_string)
                with Database(event_persistence_settings.sql_connection_string) as db:
                    table = EventTable(db.connection)
                    table.mark_as_published(row["Item"]["EventID"])
