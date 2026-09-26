import os
import ssl
import threading

import paho.mqtt.client as mqtt


class LatestFrameStore:
    """Holds only the most recently received frame, discarding older ones."""

    def __init__(self):
        self._lock = threading.Lock()
        self._frame: bytes | None = None

    def set(self, frame: bytes) -> None:
        with self._lock:
            self._frame = frame

    def get(self) -> bytes | None:
        with self._lock:
            return self._frame


def start_mqtt_client(frame_store: LatestFrameStore) -> mqtt.Client:
    host = os.environ["HIVEMQ_HOST"]
    port = int(os.environ.get("HIVEMQ_PORT", "8883"))
    username = os.environ["HIVEMQ_USERNAME"]
    password = os.environ["HIVEMQ_PASSWORD"]
    topic = os.environ.get("HIVEMQ_TOPIC", "guideglass/frames")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(username, password)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"[mqtt] connected (reason_code={reason_code}), subscribing to {topic!r}")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        print(f"[mqtt] frame received ({len(msg.payload)} bytes)")
        frame_store.set(msg.payload)

    def on_disconnect(client, userdata, flags, reason_code, properties):
        print(f"[mqtt] disconnected (reason_code={reason_code})")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(host, port)
    client.loop_start()
    return client
