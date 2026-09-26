import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from gemini_client import GuidanceClient
from mqtt_client import LatestFrameStore, start_mqtt_client

app = FastAPI()

frame_store = LatestFrameStore()
guidance_client = GuidanceClient()
frame_interval_seconds = float(os.environ.get("FRAME_INTERVAL_SECONDS", "1.5"))

connected_clients: set[WebSocket] = set()
guidance_active = False


@app.on_event("startup")
def on_startup():
    start_mqtt_client(frame_store)
    asyncio.create_task(guidance_loop())


async def guidance_loop():
    last_frame_seen = None
    while True:
        await asyncio.sleep(frame_interval_seconds)
        if not guidance_active or not connected_clients:
            continue

        frame = frame_store.get()
        if frame is None or frame is last_frame_seen:
            continue
        last_frame_seen = frame

        try:
            text = await asyncio.to_thread(guidance_client.describe_frame, frame)
        except Exception as exc:
            print(f"[gemini] error: {exc}")
            continue

        if not text:
            continue

        for ws in list(connected_clients):
            try:
                await ws.send_json({"type": "guidance", "text": text})
            except Exception:
                connected_clients.discard(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global guidance_active

    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")
            if action == "start":
                guidance_active = True
            elif action == "stop":
                guidance_active = False
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        if not connected_clients:
            guidance_active = False


@app.get("/health")
def health():
    return {"status": "ok", "guidance_active": guidance_active, "clients": len(connected_clients)}
