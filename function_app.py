import logging
import os
from textwrap import dedent
from uuid import uuid4

import azure.functions as func
from jinja2 import Template
from rdf_delta import DeltaClient
from rdflib import Dataset, Graph

app = func.FunctionApp()

subscription_name = os.environ("SUBSCRIPTION_NAME")
topic_name = os.environ("TOPIC_NAME")
session_name = os.environ["SESSION_ID"]
rdf_delta_url = os.environ["RDF_DELTA_URL"]
rdf_delta_datasource = os.environ["RDF_DELTA_DATASOURCE"]


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
    delta_client = DeltaClient(rdf_delta_url)
    ds = delta_client.describe_datasource(rdf_delta_datasource)
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


@app.service_bus_topic_trigger(
    arg_name="sb_message",
    subscription_name="rdf-patch-consumer",
    topic_name="rdf-patch-log",
    connection="CONN_STR",
    is_sessions_enabled=True,
)
def servicebus_topic_trigger(sb_message: func.ServiceBusMessage):
    logging.info(
        dedent(
            f"""processing message
         session_id: {sb_message.session_id},
         id: {sb_message.message_id},
         sequence no.: {sb_message.sequence_number},
         correlation_id: {sb_message.correlation_id}
         """
        )
    )
    if sb_message.content_type is None:
        raise ValueError("Received message with no Content-Type key in headers.")
    patch_log = sb_message.body.decode("utf-8")
    try:
        delta_client = DeltaClient(rdf_delta_url)
        if sb_message.content_type == "application/rdf-patch":
            raise NotImplementedError(
                "Only RDF Patch logs without header information are supported."
            )
        elif sb_message.content_type == "application/rdf-patch-body":
            patch_log = add_patch_log_header(patch_log)
            delta_client.create_log(patch_log, rdf_delta_datasource)
            logging.info(f"Message {sb_message.message_id} processed successfully.")
        elif sb_message.content_type in ("text/turtle", "application/trig"):
            contains_quads = (
                True if sb_message.content_type in ("application/trig",) else False
            )
            ds = delta_client.describe_datasource(rdf_delta_datasource)
            ds_log = delta_client.describe_log(ds.id)
            patch_log = convert_rdf_payload_to_rdf_patch(
                patch_log,
                ds_log.latest,
                format=sb_message.content_type,
                contains_quads=contains_quads,
            )
            delta_client.create_log(patch_log, rdf_delta_datasource)
            logging.info(f"Message {sb_message.message_id} processed successfully.")
        else:
            raise NotImplementedError(
                f"Message {sb_message.message_id} has an unsupported content type {sb_message.content_type}."
            )
    except Exception as err:
        logging.error(f"Failed to process message {sb_message.message_id}.")
        raise err
