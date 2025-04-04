import argparse
import asyncio
import datetime
import logging
import os
import pathlib

from rdflib import SDO, Graph, URIRef
from dotenv import load_dotenv

from event_persistence_consumer.servicebus import Client

try:
    load_dotenv()
except ModuleNotFoundError:
    pass

conn_str = os.getenv("SERVICE_BUS")

SUPPORTED_FORMATS = ["application/rdf-patch", "text/turtle", "application/trig"]
path = pathlib.Path(__file__).parent.absolute()
logger = logging.getLogger(__name__)


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
                str(SDO.encodingFormat): content_type,
                str(SDO.dateCreated): datetime.datetime.now(datetime.UTC).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                str(SDO.schemaVersion): None,
                str(SDO.about): "|".join(
                    list(
                        x
                        for x in graph.subjects(None, None, unique=True)
                        if isinstance(x, URIRef)
                    )
                ),
                str(SDO.creator): "asb_file_producer.py",
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
