import base64
import io
import json
import os

from openai import OpenAI
from PIL import Image

COLUMNS = [
    "URL", "ADDRESS", "CITY", "PROVINCE", "POSTAL", "AGENT", "BROKER",
    "PRICE", "LATITUDE", "LONGITUDE", "MLS NUMBER", "BEDROOMS", "BATHROOMS",
    "SQFT", "FLOORING", "COOLING", "HEATING TYPE", "POOL TYPE", "PARKING TYPE",
    "TOTAL PARKING SPACES", "PROPERTY TYPE", "BUILDING TYPE", "STOREYS",
    "SQUARE FOOTAGE", "COMMUNITY NAME", "TITLE", "LAND SIZE",
    "AGE OF BUILDING", "ANNUAL PROPERTY TAXES", "TIME ON REALTOR",
]

FIELD_SCHEMA = {
    "type": "object",
    "properties": {col: {"type": "string"} for col in COLUMNS},
    "required": COLUMNS,
    "additionalProperties": False,
}

MODEL = "gpt-4o"


def api_key_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def _image_to_data_url(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def extract_listing_fields(images: list) -> dict:
    client = OpenAI()

    content = [{
        "type": "text",
        "text": (
            "Extract the real estate listing details visible in this realtor.ca "
            "listing page screenshot. Leave a field as an empty string if it is "
            "not visible anywhere in the image(s)."
        ),
    }]
    for img in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": _image_to_data_url(img)},
        })

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "listing_fields",
                "schema": FIELD_SCHEMA,
                "strict": True,
            },
        },
    )

    text = response.choices[0].message.content
    return json.loads(text)
