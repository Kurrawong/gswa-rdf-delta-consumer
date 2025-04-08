import logging

from azure.servicebus import ServiceBusMessage, TransportType
from azure.servicebus.aio import ServiceBusClient
from rdflib import SDO

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, conn_str: str, topic: str, ws: bool):
        self._conn_str = conn_str
        self._topic = topic
        logger.info("Setting up Service Bus client")
        if ws:
            self._client = ServiceBusClient.from_connection_string(
                conn_str=conn_str, transport_type=TransportType.AmqpOverWebsocket
            )
        else:
            self._client = ServiceBusClient.from_connection_string(conn_str=conn_str)

    async def send_message(self, session_id: str, message: str, metadata: dict):
        content_type = metadata[str(SDO.encodingFormat)]
        _message = ServiceBusMessage(
            message,
            content_type=content_type,
            application_properties=metadata,
            session_id=session_id,
        )
        logger.info("Getting topic sender")
        sender = self._client.get_topic_sender(self._topic)
        logger.info("Sending message")
        await sender.send_messages(message=_message)
        logger.info("Message sent")
        await sender.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        logger.info("Cleaning up Service Bus client")
        await self._client.close()
