"""
This module defines a client to connect to the Rabbit Message Queue,
and send it tasks to perform. This largely leverages pika libraries to
achieve this.
"""
from api import config
import pika
import sys
import time
import json
import logging

logger = logging.getLogger(__name__)
HEARTBEAT_RATE = 7200 # Seconds
SEARCH_KEY = 'search'
VIDPROC_KEY = 'vidproc'

class RabbitMQClient(object):
    # If host and port are left as None, automatically connect,
    # to the local host.
    def __init__(self, host=config.rabbit_mq_host, port=config.rabbit_mq_port):
        # Initialize connection parameters. Set heartbeat to two hours so
        # we have relatively long standing connections.
        self.connection_parameters = pika.ConnectionParameters()
        self.connection_parameters.heartbeat = HEARTBEAT_RATE

        # Set the host and port if we have them
        if host is not None:
            self.connection_parameters.host = host
        if port is not None:
            self.connection_parameters.port = port

        # Connect to Rabbit MQ.
        self.conn = pika.BlockingConnection(parameters=self.connection_parameters)
        self.search_channel = self.conn.channel()
        self.vidproc_channel = self.conn.channel()

        # Create channels for our microservices to publish/subscribe to.
        self.search_queue = self.search_channel.queue_declare(queue='search')
        self.vidproc_queue = self.vidproc_channel.queue_declare(queue='vidproc')

        # Start listening.
        self.search_channel.basic_consume(self.callback, SEARCH_KEY)

    # On callback, log the message being queued up, and write the progress
    # to PSQL.
    def callback(self, ch, method, properties, body):
        if type(body) == str:
            body = json.loads(body)
        logger.info("[x] Received %r" % body)
        # TODO(rajkinra) Write body here to PSQL.

    def maybe_refresh_connections(self):
        # Refresh connection.
        if not self.conn.is_open:
            self.conn = self.conn = pika.BlockingConnection(parameters=self.connection_parameters)
            self.search_channel = self.conn.channel()
            self.vidproc_channel = self.conn.channel()
            return

        # Refresh channel only if needed.
        if not self.search_channel.is_open:
            self.search_channel = self.conn.channel()
        if not self.vidproc_channel.is_open:
            self.vidproc_channel = self.conn.channel()

    # Publish a search request to spark.
    def submit_search_job(self, query):
        # Refresh connections if they are down.
        self.maybe_refresh_connections()

        # Convert the arguments to a payload.
        payload = {
            'query': query,,
        }

        # Publish the payload to the search queue so that spark search
        # picks up the work. Dump the dictionary into a JSON format.
        self.search_channel.basic_publish(exchange='',
                                          routing_key=SEARCH_KEY,
                                          body=json.dumps(payload))

    # Define a listener on the search queue. This listener can live on some
    # asynchronous task in django.
    def listen_on_search(self):
        # Start consumption.
        self.search_channel.start_consuming()
