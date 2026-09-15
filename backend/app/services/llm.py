"""LLM service wrapper for interacting with Google Gemini API."""

import os
from pathlib import Path

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.prompts.career_assistant import CAREER_ASSISTANT_SYSTEM_PROMPT


def _load_env_file() -> None:
    """Load variables from .env file into os.environ if present."""

    env_path = Path(__file__).resolve().parent.parent.parent / ".env"

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)

                    key = key.strip()
                    val = val.strip().strip('"').strip("'")

                    if key not in os.environ:
                        os.environ[key] = val


_load_env_file()


def get_gemini_client() -> genai.Client:
    """Retrieve initialized Google GenAI client."""

    api_key = os.getenv("GEMINI_API_KEY")

    if (
        not api_key
        or api_key.strip() == ""
        or api_key == "your_gemini_api_key_here"
    ):
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please set it in backend/.env or your system environment."
        )

    return genai.Client(api_key=api_key)


async def generate_gemini_response(prompt: str) -> str:
    """Send a generic prompt to Google Gemini and return the response."""

    client = get_gemini_client()

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
            ),
        )

        return response.text or ""

    except APIError as err:
        print("GEMINI ERROR:", str(err))
        raise RuntimeError(
            f"Gemini service error: {str(err)}"
        ) from err

    except Exception as err:
        print("GEMINI UNKNOWN ERROR:", repr(err))
        raise RuntimeError(
            f"Gemini unknown error: {str(err)}"
        ) from err


async def get_career_assistant_response(
    user_message: str,
) -> str:
    """Send the user query to Google Gemini using the Career Assistant prompt."""

    client = get_gemini_client()

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=CAREER_ASSISTANT_SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )

        return response.text or ""

    except APIError as err:
        raise RuntimeError(
            f"Gemini service error: {str(err)}"
        ) from err