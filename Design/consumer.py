from google.cloud import pubsub_v1
import json
import os
from concurrent.futures import TimeoutError

# Read arguments and configurations and initialize
credPath = os.path.abspath('cred.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credPath


timeout = 2.0

subscriber = pubsub_v1.SubscriberClient();
sub_path = 'projects/trans-filament-412615/subscriptions/SM_R-sub'


def callback(message):
    print(f'Received message: {message}')
    print(f'Data: {message.data}')
    message.ack()


streaming_future = subscriber.subscribe(sub_path, callback=callback)
print(f'Listening for messages on {sub_path}')

with subscriber:
    try:
        streaming_future.result()
    except TimeoutError:
        streaming_future.cancel()
        streaming_future.result()
    except KeyboardInterrupt:
        streaming_future.cancel()
        streaming_future.result()