import logging
import os
from functools import wraps
from textwrap import dedent

import azure.functions as func

from event_persistence_consumer.database import Database, EventTable
from event_persistence_consumer.settings import settings

app = func.FunctionApp()

session_name = os.environ["SESSION_ID"]


def service_bus_topic_trigger(func_app):
    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            return handler(*args, **kwargs)

        return func_app.service_bus_topic_trigger(
            arg_name="message",
            subscription_name=os.environ["SERVICE_BUS_SUBSCRIPTION"],
            topic_name=os.environ["SERVICE_BUS_TOPIC"],
            connection="SERVICE_BUS",
            is_sessions_enabled=True,
        )(wrapper)

    return decorator


@service_bus_topic_trigger(app)
def servicebus_topic_trigger(message: func.ServiceBusMessage):
    logging.info(
        dedent(
            f"""Processing message:
         session_id: {message.session_id},
         id: {message.message_id},
         sequence no.: {message.sequence_number},
         correlation_id: {message.correlation_id}
         content_type: {message.content_type}
         headers: {message.application_properties}
         """
        )
    )
    if message.content_type is None:
        raise ValueError(f"message {message.message_id} missing content-type header")
    try:
        with Database(settings.sql_connection_string) as db:
            table = EventTable(db.connection)
            table.insert(
                message.application_properties,
                message.get_body().decode("utf-8"),
            )
    except Exception as err:
        logging.error(f"Failed to process message {message.message_id}.")
        raise err
