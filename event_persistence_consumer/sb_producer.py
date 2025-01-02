import argparse
import asyncio
import datetime
import logging
import pathlib

from azure.servicebus import ServiceBusMessage, TransportType
from azure.servicebus._pyamqp import AMQPClient
from azure.servicebus.aio import ServiceBusClient
from rdflib import SDO, Graph, URIRef

conn_str = "Endpoint=sb://sb;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"

# Workaround for service bus emulator retrieved from https://github.com/Azure/azure-sdk-for-python/issues/34273#issuecomment-2503806488
# Disable TLS. Workaround for https://github.com/Azure/azure-sdk-for-python/issues/34273
org_init = AMQPClient.__init__


def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False
    org_init(self, hostname, **kwargs)


AMQPClient.__init__ = new_init

SUPPORTED_FORMATS = ["application/rdf-patch", "text/turtle", "application/trig"]
path = pathlib.Path(__file__).parent.absolute()
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
        content_type = metadata[SDO.encodingFormat]
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


async def main(content_type: str, filename: str, topic: str, session_id: str, ws: bool):
    with open(path / filename, "r", encoding="utf-8") as file:
        content = file.read()
        graph = Graph().parse(data=content, format=content_type)
        async with Client(
            conn_str=conn_str,
            topic=topic,
            ws=ws,
        ) as client:
            metadata = {
                SDO.encodingFormat: content_type,
                SDO.dateCreated: datetime.datetime.now(datetime.UTC).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                SDO.schemaVersion: None,
                SDO.about: "|".join(
                    list(
                        x
                        for x in graph.subjects(None, None, unique=True)
                        if isinstance(x, URIRef)
                    )
                ),
                SDO.creator: "asb_file_producer.py",
            }
            await client.send_message(session_id, content, metadata)


async def cli():
    parser = argparse.ArgumentParser(
        "File Producer for Azure Service Bus",
        description="Add a file's content to a service bus topic.",
    )
    parser.add_argument("topic", help="Service Bus topic for all sent messages.")
    parser.add_argument("session", help="Session ID for the message.")
    parser.add_argument(
        "filename", help="File content to be added as the message value."
    )
    parser.add_argument(
        "--format",
        required=False,
        default="application/trig",
        help="The content type of the file (default: application/trig)",
    )
    parser.add_argument(
        "--ws",
        action="store_true",
        help="Flag to enable WebSocket connection",
    )
    args = parser.parse_args()
    topic = args.topic
    session_id = args.session
    content_type = args.format
    filename = args.filename
    ws = args.ws

    if content_type not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported content type: {content_type}")

    await main(content_type, filename, topic, session_id, ws)


if __name__ == "__main__":
    asyncio.run(cli())
