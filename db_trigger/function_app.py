import json
import logging

import azure.functions as func
from event_persistence_consumer.servicebus import Client

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
    logging.info(f"Received rows: {json.dumps(rows, indent=2)}")

    async with Client(
        conn_str=settings.conn_str,
        topic=settings.topic,
        ws=settings.ws,
    ) as client:
        for row in rows:
            event_published = row["Item"]["EventPublished"]
            if event_published:
                logging.info(f"Event {row['Item']['EventID']} already published")
            else:
                logging.info(f"Publishing event {row['Item']['EventID']}")
                metadata = json.loads(row["Item"]["EventHeader"])
                logging.info(type(metadata))
                logging.info(metadata)
                await client.send_message(
                    session_id=settings.session,
                    message=row["Item"]["EventBody"],
                    metadata=metadata,
                )
