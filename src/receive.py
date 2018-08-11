#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

with open('../mac.json', 'a') as output_file:
    HOST = '127.0.0.1'
    CLIENT_ID = 'psd'
    TOPIC = 'amq.topic.psd'

    def on_message(client, userdata, message):
        msg = str(message.payload.decode('utf-8'))
        print(msg)
        output_file.write(msg+'\n')
        output_file.flush()

    print('creating new client instance')
    client = mqtt.Client(CLIENT_ID)
    client.on_message = on_message
    print('connecting to broker')
    client.connect(HOST)
    print('subscribing to topic', TOPIC)
    client.subscribe(TOPIC)
    client.loop_forever()
