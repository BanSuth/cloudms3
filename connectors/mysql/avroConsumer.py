from confluent_kafka import Consumer
import json
import io
from avro.io import DatumReader, BinaryDecoder
import avro.schema

# Read arguments and configurations and initialize
consumer_conf = json.load(open('cred.json'))
topic= "SM_Readings"

# Create Consumer instance
# 'auto.offset.reset=earliest' to start reading from the beginning of the
#   topic if no committed offsets exist
consumer_conf['group.id'] = 'python_example_group_1'
consumer_conf['auto.offset.reset'] = 'earliest'
consumer_conf["session.timeout.ms"]=45000
consumer = Consumer(consumer_conf)

# Subscribe to topic
consumer.subscribe([topic])

#deserialize
schema = avro.schema.parse(open("./schema2.txt").read())
reader = DatumReader(schema)
def decode(msg_value):
    message_bytes = io.BytesIO(msg_value)
    message_bytes.seek(5)
    decoder = BinaryDecoder(message_bytes)
    event_dict = reader.read(decoder)
    return event_dict
   
# Process messages
total_count = 0
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            continue
        elif msg.error():
            print('error: {}'.format(msg.error()))
        else:
            # Check for Kafka message
            record_key = str(msg.key())
            record_value = decode(msg.value())
            print("Consumed record with key {} and value {}"
                  .format(record_key, record_value))
except KeyboardInterrupt:
    pass
finally:
    # Leave group and commit final offsets
    consumer.close()