import asyncio
import argparse

from loguru import logger
from azure.servicebus.aio import ServiceBusClient, AutoLockRenewer
from azure.servicebus import TransportType

from gswa_rdf_delta_consumer import process_message
from gswa_rdf_delta_consumer.settings import settings

MAX_MESSAGE_COUNT = 1
MAX_WAIT_TIME = 5


async def main():
    logger.info("Starting up RDF Delta Consumer")
    async with ServiceBusClient.from_connection_string(
        settings.conn_str,
        transport_type=TransportType.AmqpOverWebsocket,
    ) as client:
        async with client:
            receiver = client.get_subscription_receiver(
                topic_name=settings.topic,
                subscription_name=settings.subscription,
                session_id=settings.session_id,
            )
            renewer = AutoLockRenewer()
            receiver._auto_lock_renewer = renewer
            logger.info(
                f"Connected to subscription {settings.subscription} and awaiting messages on topic {settings.topic}"
            )
            async with receiver:
                while True:
                    messages = await receiver.receive_messages(
                        max_message_count=MAX_MESSAGE_COUNT, max_wait_time=MAX_WAIT_TIME
                    )
                    for message in messages:
                        logger.info(f"Processing message id {message.message_id}")
                        await process_message(
                            message, receiver, settings.topic, settings.session_id
                        )


async def cli():
    parser = argparse.ArgumentParser(
        "RDF Delta Consumer",
        description="An RDF Delta Consumer consuming from a subscription's topic in the Azure Service Bus.",
    )
    parser.parse_args()
    await main()


if __name__ == "__main__":
    asyncio.run(cli())
