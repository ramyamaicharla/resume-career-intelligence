"""Service for extracting structured resume data from raw text using Gemini."""

import os

from google.genai import types
from google.genai.errors import APIError
from pydantic import ValidationError

from app.models.resume import StructuredResume
from app.services.llm import get_gemini_client


RESUME_EXTRACTION_SYSTEM_PROMPT = """
You are an expert Resume Information Extraction system.

Your job is to parse raw resume text and extract all factual details into the structured JSON schema.

STRICT EXTRACTION RULES:

1. Extract ONLY information that is explicitly stated in the provided resume text.

2. NEVER invent, infer, assume, or hallucinate missing information.
   Do NOT invent degrees, dates, skills, employers, projects, or statistics.

3. If an attribute or section is not mentioned or unavailable in the text,
   return null or an empty list [].

4. Faithfully preserve the candidate's actual skills, experience, job roles,
   education, and projects as written.

5. Do not include conversational commentary or advice.

6. Produce strictly the structured resume data conforming to the schema.

7. Pay careful attention to the resume text and populate every field
   whenever the corresponding information is explicitly available.
"""


async def extract_structured_resume(resume_text: str) -> StructuredResume:
    """Extract structured resume information from raw text using Gemini."""

    # Validate input
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty. Cannot perform analysis.")

    # Create Gemini client
    client = get_gemini_client()

    # Get Gemini model
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # Build extraction prompt
    prompt = (
        "Extract all structured resume information from the following resume text.\n\n"
        "--- RESUME TEXT START ---\n"
        f"{resume_text}\n"
        "--- RESUME TEXT END ---"
    )

    # Debug: verify text is actually reaching Gemini
    print("\n" + "=" * 80)
    print("RESUME TEXT SENT TO GEMINI:")
    print("=" * 80)
    print(resume_text)
    print("=" * 80)
    print(f"Resume text length: {len(resume_text)} characters")
    print(f"Gemini model: {model}")
    print("=" * 80 + "\n")

    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=RESUME_EXTRACTION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=StructuredResume,
                temperature=0.1,
            ),
        )

        # Check empty Gemini response
        if not response.text:
            raise ValueError(
                "The extraction model returned an empty response."
            )

        # Debug: inspect Gemini response
        print("\n" + "=" * 80)
        print("GEMINI RAW RESPONSE:")
        print("=" * 80)
        print(response.text)
        print("=" * 80 + "\n")

        # Validate Gemini JSON against Pydantic schema
        return StructuredResume.model_validate_json(response.text)

    except ValidationError as val_err:
        raise ValueError(
            "Failed to validate extracted resume data against schema: "
            f"{str(val_err)}"
        ) from val_err

    except APIError as api_err:
        print("RESUME GEMINI API ERROR:", repr(api_err))
        raise RuntimeError(
            f"Gemini API error during extraction: {str(api_err)}"
        ) from api_err