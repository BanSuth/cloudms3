from confluent_kafka import Producer, KafkaError
import json
import time
import random 
import numpy as np
import avro.schema
import io
from avro.io import DatumWriter, BinaryEncoder

# Read arguments and configurations and initialize
producer_conf = json.load(open('cred.json'))
producer = Producer(producer_conf)
topic= "ToRedis"

# Optional per-message on_delivery handler (triggered by poll() or flush())
# when a message has been successfully delivered or
# permanently failed delivery (after retries).
def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        print("Produced record to topic {} partition [{}] @ offset {}"
              .format(msg.topic(), msg.partition(), msg.offset()))

# read the image as bytes
with open("ontarioTech.jpg", "rb") as f:
    value = f.read();
producer.produce(topic,key= 'fromKafka', value=value, on_delivery=acked)
producer.poll(0)
producer.flush()

print("message was produced to topic {}!".format(topic))