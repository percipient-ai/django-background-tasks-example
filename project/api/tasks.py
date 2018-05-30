from background_task import background
from logging import getLogger
from api import mq_client

logger = getLogger(__name__)

@background(schedule=0)
def demo_task(message):
    # Create a new client.
    client = mq_client.RabbitMQClient()

    # This task is dedicated to listening for work.
    logger.debug('Listening to search work')

    # Start consuming messages.
    client.listen_on_search()
    logger.debug('We stopped listening! Need to restart this task.')
