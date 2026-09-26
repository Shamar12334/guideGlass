import os

from google import genai
from google.genai import types

_SYSTEM_PROMPT = (
    "You are a navigation assistant for a blind person wearing camera glasses. "
    "You are given a single frame from their point of view. "
    "In one short sentence, tell them what is immediately ahead and any hazard "
    "or obstacle they should react to (e.g. steps, curb, person, wall, vehicle, obstacle on the ground). "
    "Be direct and concise, like a live guide speaking to them. "
    "If the path ahead is clear, say so briefly. Do not describe the scene in general, only what matters for walking safely."
)


class GuidanceClient:
    def __init__(self):
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def describe_frame(self, jpeg_bytes: bytes) -> str:
        response = self._client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[
                _SYSTEM_PROMPT,
                types.Part.from_bytes(data=jpeg_bytes, mime_type="image/jpeg"),
            ],
        )
        return (response.text or "").strip()
