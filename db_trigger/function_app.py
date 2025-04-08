import json
import logging
import azure.functions as func

from db_trigger.database import Database, EventTable
from db_trigger.servicebus import Client
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
        topic=settings.service_bus_topic,
        ws=settings.use_amqp_over_ws,
    ) as client:
        for row in rows:
            event_published = row["Item"]["EventPublished"]
            if event_published:
                logging.info(
                    f"Event {row['Item']['EventID']} already published")
            else:
                logging.info(f"Publishing event {row['Item']['EventID']}")
                metadata = json.loads(row["Item"]["EventHeader"])
                logging.info(metadata)

                try:
                    await client.send_message(
                        session_id=settings.service_bus_session_id,
                        message=row["Item"]["EventBody"],
                        metadata=metadata,
                    )
                except Exception as e:
                    logging.error("Error sending message: %s", e)

                try:
                    logging.info("Sql connection string: %s",
                                 settings.sql_connection_string_odbc)
                    with Database(settings.sql_connection_string_odbc) as db:
                        table = EventTable(db.connection)
                        row_id = int(row["Item"]["EventID"])
                        logging.info(f"Marking event {row_id} as published")
                        table.mark_as_published(row_id)
                except Exception as e:
                    logging.error("Error marking event as published: %s", e)
