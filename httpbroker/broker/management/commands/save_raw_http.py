import datetime
import logging
import os

from django.conf import settings

from broker.management.commands import RabbitCommand

logger = logging.getLogger('broker')

RAW_HTTP_EXCHANGE = settings.RAW_HTTP_EXCHANGE


def consumer_callback(channel, method, properties, body, options=None):
    # Construct filename
    fname = f'{method.routing_key}.msgpack'
    date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    path = os.path.join(settings.VAR_DIR, 'httprequests', date)
    fpath = os.path.join(path, fname)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(fpath, 'ab') as f:
        f.write(body)
    logger.debug(f'Successfully saved message {method.delivery_tag}')
    channel.basic_ack(method.delivery_tag)


class Command(RabbitCommand):
    help = 'Read RabbitMQ queue and save all messages to a file'

    def add_arguments(self, parser):
        # parser.add_argument('keys', nargs='+', type=str)
        super().add_arguments(parser)
        pass

    def handle(self, *args, **options):
        logger.info(f'Start handling {__name__}')
        options['exchange'] = settings.RAW_HTTP_EXCHANGE
        options['queue'] = 'raw_http_save_queue'
        options['routing_key'] = f'{settings.RABBITMQ["ROUTING_KEY_PREFIX"]}.#'
        options['consumer_callback'] = consumer_callback
        super().handle(*args, **options)
