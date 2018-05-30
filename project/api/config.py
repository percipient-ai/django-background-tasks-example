import os

rabbit_mq_host = os.environ['RABBIT_MQ_HOST'] if 'RABBIT_MQ_HOST' in os.environ else '0.0.0.0'
rabbit_mq_port = os.environ['RABBIT_MQ_PORT'] if 'RABBIT_MQ_PORT' in os.environ else 5672
