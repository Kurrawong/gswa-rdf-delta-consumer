import logging
import os
from textwrap import dedent
from uuid import uuid4

import azure.functions as func
import httpx
from jinja2 import Template
from pydantic import BaseModel, field_validator
from rdflib import Dataset, Graph

app = func.FunctionApp()

session_name = os.environ["SESSION_ID"]
rdf_delta_url = os.environ["RDF_DELTA_URL"]
rdf_delta_datasource = os.environ["RDF_DELTA_DATASOURCE"]


class Datasource(BaseModel):
    """Basic datasource description."""

    id: str
    name: str
    uri: str

    @field_validator("id")
    @classmethod
    def convert_id_value(cls, v: str):
        """Remove the id: prefix from the identifier value."""
        return v.split("id:")[-1]


class DatasourceLogInfo(Datasource):
    """Datasource description with additional information related to patch logs."""

    min_version: int
    max_version: int
    latest: str

    @field_validator("latest")
    @classmethod
    def convert_latest_id_value(cls, v: str):
        """Remove the id: prefix from the identifier value."""
        return v.split("id:")[-1]


class LogCreatedMetadata(BaseModel):
    """Patch log metadata for new creations."""

    version: int
    location: str


class DeltaServerError(Exception):
    """Any errors returned from the Delta Server."""


class DeltaClient:
    """Perform common operations against an RDF Delta Server.

    The API interface is based on the documentation at https://afs.github.io/rdf-delta/delta-server-api.

    :param base_url: The base URL of the Delta Server. Example, http://localhost:1066/.
    """

    def __init__(self, base_url: str):
        url = base_url if base_url.endswith("/") else base_url + "/"
        self.url = url
        self.client = httpx.Client()

    def _fetch_rpc(self, payload: dict) -> dict:
        """Helper function to send requests to the Delta server via the RPC endpoint.

        :param payload: The payload to send to the Delta server.
        :return: The JSON response body from the Delta server.
        """
        logging.debug(f"Sending {payload['operation']} operation to {self.url}")
        response = self.client.post(self.url + "$/rpc", json=payload)
        if response.status_code != 200:
            raise DeltaServerError(
                f"Delta server responded with error {response.status_code}: {response.text}"
            )

        return response.json()

    def close(self):
        """Close the delta client and perform cleanup routines."""
        self.client.close()

    def list_datasource(self) -> list[str]:
        """Get a list of datasource identifiers.

        :return: A list of datasource identifiers.
        """
        payload = {"opid": "", "operation": "list_datasource", "arg": {}}
        data = self._fetch_rpc(payload)
        return data["array"]

    def list_descriptions(self) -> list[Datasource]:
        """Get a list of datasource object descriptions.

        :return: A list of datasource objects.
        """
        payload = {"opid": "", "operation": "list_descriptions", "arg": {}}
        data = self._fetch_rpc(payload)
        datasources = [Datasource(**v) for v in data["array"]]
        return datasources

    def create_datasource(self, name: str) -> Datasource:
        """Create a new datasource.

        :param name: Datasource name.
        :return: Datasource object.
        """

        raise NotImplementedError(
            "Delta operation 'create_datasource' currently not supported."
        )

        payload = {
            "opid": "",
            "operation": "create_datasource",
            "arg": {"name": name, "id": str(uuid4())},
        }
        data = self._fetch_rpc(payload)
        return Datasource(**data)

    def describe_datasource(self, name: str) -> Datasource:
        """Get a datasource object description by name.

        :param name: Datasource name.
        :return: Datasource object.
        """
        payload = {
            "opid": "",
            "operation": "describe_datasource",
            "arg": {"name": name},
        }
        data = self._fetch_rpc(payload)
        return Datasource(**data)

    def describe_log(self, id_: str) -> DatasourceLogInfo:
        """Get a datasource log object description by identifier.

        :param id_: Datasource identifier.
        :return: Datasource log object with additional information related to patch logs.
        """
        payload = {"opid": "", "operation": "describe_log", "arg": {"datasource": id_}}
        data = self._fetch_rpc(payload)
        return DatasourceLogInfo(**data)

    def create_log(self, patch_log: str, name: str) -> LogCreatedMetadata:
        """Create a new patch log on a datasource.

        :param patch_log: Patch log content.
        :param name: Datasource name.
        """
        headers = {"Content-Type": "application/rdf-patch"}
        response = self.client.post(
            self.url + f"{name}", content=patch_log, headers=headers
        )
        if response.status_code != 200:
            raise DeltaServerError(
                f"Delta server responded with error {response.status_code}: {response.text}"
            )

        data = response.json()
        return LogCreatedMetadata(**data)

    def get_log(self, version: int, datasource: str) -> str:
        """Get a patch log by version.

        :param version: Patch log version.
        :param datasource: Datasource name.
        :return: Patch log content.
        """
        response = self.client.get(self.url + f"{datasource}/{version}")
        if response.status_code != 200:
            raise DeltaServerError(
                f"Delta server responded with error {response.status_code}: {response.text}"
            )

        return response.text


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
    arg_name="message",
    subscription_name="rdf-patch-consumer",
    topic_name="rdf-patch-log",
    connection="SERVICE_BUS",
    is_sessions_enabled=True,
)
def servicebus_topic_trigger(message: func.ServiceBusMessage):
    logging.info(
        dedent(
            f"""Processing message
         session_id: {message.session_id},
         id: {message.message_id},
         sequence no.: {message.sequence_number},
         correlation_id: {message.correlation_id}
         """
        )
    )
    if message.content_type is None:
        raise ValueError(f"message {message.message_id} missing content-type header")
    patch_log = message.get_body().decode("utf-8")
    try:
        delta_client = DeltaClient(rdf_delta_url)
        if message.content_type == "application/rdf-patch":
            raise NotImplementedError(
                "Only RDF Patch logs without header information are supported."
            )
        elif message.content_type == "application/rdf-patch-body":
            patch_log = add_patch_log_header(patch_log)
            delta_client.create_log(patch_log, rdf_delta_datasource)
            logging.info(f"Message {message.message_id} processed successfully.")
        elif message.content_type in ("text/turtle", "application/trig"):
            contains_quads = (
                True if message.content_type in ("application/trig",) else False
            )
            ds = delta_client.describe_datasource(rdf_delta_datasource)
            ds_log = delta_client.describe_log(ds.id)
            patch_log = convert_rdf_payload_to_rdf_patch(
                patch_log,
                ds_log.latest,
                format=message.content_type,
                contains_quads=contains_quads,
            )
            delta_client.create_log(patch_log, rdf_delta_datasource)
            logging.info(f"Message {message.message_id} processed successfully.")
        else:
            raise NotImplementedError(
                f"Message {message.message_id} has an unsupported content type {message.content_type}."
            )
    except Exception as err:
        logging.error(f"Failed to process message {message.message_id}.")
        raise err
