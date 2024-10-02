from uuid import uuid4
from textwrap import dedent

from loguru import logger
from jinja2 import Template
from rdflib import SDO, Dataset, Graph
from rdf_delta import DeltaClient
from azure.servicebus import ServiceBusReceivedMessage
from azure.servicebus.aio import ServiceBusReceiver

from gswa_rdf_delta_consumer.settings import settings

SUPPORTED_FORMATS = ["application/rdf-patch", "text/turtle", "application/trig"]


def convert_rdf_payload_to_rdf_patch(
    input_data: str,
    latest_id: str,
    format: str = "text/turtle",
    contains_quads: bool = False,
) -> str:
    if contains_quads:
        graph = Dataset()
        graph.parse(data=input_data, format=format)
        lines = graph.serialize(format="application/n-quads").strip()
    else:
        graph = Graph()
        graph.parse(data=input_data, format=format)
        lines = graph.serialize(format="application/n-triples").strip()

    patch_log = dedent(
        Template(
            """
        H id <uuid:{{ new_id }}> .
        {% if latest_id %}H prev <uuid:{{ latest_id }}> .{% endif %}

        TX .
        {% for line in lines %}
        A {{ line }}
        {% endfor %}
        TC .
    """
        ).render(latest_id=latest_id, new_id=(uuid4()), lines=lines.split("\n"))
    )
    return patch_log


def add_patch_log_header(patch_log: str):
    delta_client = DeltaClient(settings.rdf_delta_url)
    ds = delta_client.describe_datasource(settings.rdf_delta_datasource)
    ds_log = delta_client.describe_log(ds.id)
    previous_id = ds_log.latest
    new_id = str(uuid4())
    patch_log = (
        dedent(
            Template(
                """\
        H id <uuid:{{ new_id }}> .
        H prev <uuid:{{ previous_id }}> .
    """
            ).render(previous_id=previous_id, new_id=new_id)
        )
        + patch_log
    )
    return patch_log


async def process_message(
    message: ServiceBusReceivedMessage,
    receiver: ServiceBusReceiver,
    topic: str,
    session_id: str,
):
    metadata = f"topic {topic} session id {session_id} message id {message.message_id}"

    patch_log = str(message.raw_amqp_message)
    headers = {
        (k.decode("utf-8") if isinstance(k, bytes) else k): (
            v.decode("utf-8") if isinstance(v, bytes) else v
        )
        for k, v in message.application_properties.items()
    }

    if headers is None:
        raise ValueError(f"Received message with no headers. Context: {metadata}")

    content_type = headers.get(str(SDO.encodingFormat))
    if not content_type:
        raise ValueError(
            f"Received message with no Content-Type key in headers. Metadata: {metadata}"
        )

    try:
        delta_client = DeltaClient(settings.rdf_delta_url)
        if content_type == "application/rdf-patch":
            raise NotImplementedError(
                "Only RDF Patch logs without header information are supported."
            )
        elif content_type == "application/rdf-patch-body":
            patch_log = add_patch_log_header(patch_log)
            # TODO: This is where we would include offset info in the patch log for event replays.
            #       Replays are not supported using Service Bus.
            delta_client.create_log(patch_log, settings.rdf_delta_datasource)
            await receiver.complete_message(message)
            logger.info(f"Processed message successfully. Metadata: {metadata}")
        elif content_type in ("text/turtle", "application/trig"):
            contains_quads = True if content_type in ("application/trig",) else False
            ds = delta_client.describe_datasource(settings.rdf_delta_datasource)
            ds_log = delta_client.describe_log(ds.id)
            patch_log = convert_rdf_payload_to_rdf_patch(
                patch_log,
                ds_log.latest,
                format=content_type,
                contains_quads=contains_quads,
            )
            # TODO: This is where we would include offset info in the patch log for event replays.
            #       Replays are not supported using Service Bus.
            delta_client.create_log(patch_log, settings.rdf_delta_datasource)
            await receiver.complete_message(message)
            logger.info(f"Processed message successfully. Metadata: {metadata}")
        else:
            raise NotImplementedError(
                f"Unsupported content type {content_type}. Metadata: {metadata}"
            )
    except Exception as err:
        logger.error(
            f"Failed to process message. Metadata: {metadata}\nMessage:\n{patch_log}"
        )
        raise err
