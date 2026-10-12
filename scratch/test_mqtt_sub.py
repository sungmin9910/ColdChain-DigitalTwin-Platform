import paho.mqtt.client as mqtt
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

broker = "broker.hivemq.com"
port = 1883
topic = sys.argv[1] if len(sys.argv) > 1 else "coldchain/truck02/sensor"

messages_received = []

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(topic)
    print(f"Subscribed to topic: {topic}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8', errors='replace')
    print(f"\n[LIVE MQTT RECEIVED from {msg.topic}]:\n{payload}")
    messages_received.append(payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to {broker}:{port}...")
client.connect(broker, port, 60)
client.loop_start()

start = time.time()
while time.time() - start < 15 and len(messages_received) < 2:
    time.sleep(0.5)

client.loop_stop()
client.disconnect()

print(f"\nDone. Total messages captured: {len(messages_received)}")
