# guideGlass

Camera-powered glasses designed to assist visually impaired individuals navigate independently using AI-powered technology.

#
<img width="700" height="638" alt="esp cam pic" src="https://github.com/user-attachments/assets/1798c784-bc24-4b64-8a7f-45c6e0b148a1" />
#
<img width="1012" height="1045" alt="image" src="https://github.com/user-attachments/assets/ff8bce3a-5e82-495e-9158-a79b133474b1" />

## Inspiration

I'm big into health tech, and lately I've been paying attention to how fast AR glasses and AI cameras are blowing up, stuff like Meta's smart glasses. And it got me thinking, all this tech is being built just to make everyday life a little more convenient for people who honestly don't need it that badly. Meanwhile blind people are still walking around with a cane, going slow, tapping the ground just hoping they don't trip or walk into something. That felt backwards to me. So I wanted to take that same camera and AI tech and actually put it toward something that matters, helping blind people move through the world normally, at a normal pace, without having to be so cautious about every step they take.

## How it works

1. An ESP32-CAM mounted on the glasses captures frames and publishes them over MQTT (HiveMQ Cloud).
2. A Python backend subscribes to the frame topic, periodically sends the latest frame to Gemini, and asks it for short, spoken-style walking guidance (obstacles, hazards, clear path).
3. The backend streams that guidance to a browser frontend over a WebSocket, where it's read aloud via text-to-speech — since the glasses don't have a built-in speaker/mic yet.
4. The frontend also offers turn-by-turn walking directions to a destination, using the phone's GPS and the Google Maps Directions API, spoken aloud alongside the hazard warnings.

```
ESP32-CAM --(MQTT/HiveMQ)--> backend --(Gemini)--> guidance text --(WebSocket)--> browser (TTS)
                                                          phone GPS --(Directions API)--> turn-by-turn (TTS)
```

## Backend setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in HiveMQ credentials/topic + GEMINI_API_KEY
.venv/bin/uvicorn main:app --reload
```

## Status

- [x] ESP32-CAM firmware publishing frames over HiveMQ
- [x] Backend: MQTT ingestion + Gemini guidance + WebSocket output
- [x] Frontend: start/stop control + live text-to-speech
- [x] Frontend: turn-by-turn walking directions
