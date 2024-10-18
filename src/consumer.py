import asyncio
import argparse

from loguru import logger
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import TransportType
from azure.servicebus.exceptions import SessionLockLostError

from gswa_rdf_delta_consumer import process_message
from gswa_rdf_delta_consumer.settings import settings

MAX_MESSAGE_COUNT = 1
MAX_WAIT_TIME = 5
TIMEOUT = 10.0


async def main():
    logger.info("Starting up RDF Delta Consumer")
    async with ServiceBusClient.from_connection_string(
        settings.conn_str,
        transport_type=TransportType.AmqpOverWebsocket,
    ) as client:
        receiver = client.get_subscription_receiver(
            topic_name=settings.topic,
            subscription_name=settings.subscription,
            session_id=settings.session_id,
            max_wait_time=TIMEOUT,
        )
        logger.info(
            f"Connected to subscription {settings.subscription} and awaiting messages on topic {settings.topic}"
        )
        async with receiver:
            while True:
                try:
                    logger.debug("Renewing session lock.")
                    await receiver.session.renew_lock(timeout=TIMEOUT)
                    logger.debug("Session lock renewed. Waiting for messages.")
                    messages = await asyncio.wait_for(
                        receiver.receive_messages(
                            max_message_count=MAX_MESSAGE_COUNT, max_wait_time=MAX_WAIT_TIME
                        ),
                        timeout=MAX_WAIT_TIME + 5  # Add a small buffer to the timeout
                    )
                    logger.debug(f"{len(messages)} messages received.")
                    for message in messages:
                        logger.info(f"Processing message with ID {message.message_id}")
                        await process_message(
                            message, receiver, settings.topic, settings.session_id
                        )
                        logger.info(f"Message processed successfully. Message ID {message.message_id}")
                except asyncio.TimeoutError:
                    logger.debug("Timeout occurred while receiving messages.")
                except SessionLockLostError:
                    logger.debug("Session lock lost")
                except Exception as err:
                    logger.error(f"An unexpected error occurred: {err}")


async def cli():
    parser = argparse.ArgumentParser(
        "RDF Delta Consumer",
        description="An RDF Delta Consumer consuming from a subscription's topic in the Azure Service Bus.",
    )
    parser.parse_args()

    await main()


if __name__ == "__main__":
    try:
        asyncio.run(cli())
    except KeyboardInterrupt:
        logger.info("Shutting down RDF Delta Consumer")
