import io

import fitz
import streamlit as st
from PIL import Image

from exporter import COLUMNS, append_listing, DEFAULT_PATH, ensure_workbook
from parser import api_key_configured, extract_listing_fields

st.set_page_config(page_title="Realtor Listing Extractor", layout="wide")
st.title("Realtor Listing Extractor")
st.caption("Upload a screenshot or PDF of a realtor.ca listing detail page to extract its data into Excel.")

if not api_key_configured():
    st.error(
        "OPENAI_API_KEY is not set. Set it as an environment variable "
        "(e.g. in PowerShell: $env:OPENAI_API_KEY = 'your-key') and restart this app."
    )
    st.stop()

ensure_workbook()

uploaded = st.file_uploader("Listing screenshot or PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded is not None:
    images = []
    if uploaded.type == "application/pdf":
        doc = fitz.open(stream=uploaded.read(), filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            images.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    else:
        images.append(Image.open(uploaded))

    st.image(images, caption=[f"Page {i + 1}" for i in range(len(images))], width=250)

    with st.spinner("Extracting listing fields with OpenAI..."):
        try:
            extracted = extract_listing_fields(images)
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            extracted = {}

    # Latitude/longitude are geocoded from the address on save (see exporter.py),
    # not read from the screenshot — clear whatever placeholder the model returned.
    extracted["LATITUDE"] = ""
    extracted["LONGITUDE"] = ""
    extracted = {k: (v.upper() if isinstance(v, str) else v) for k, v in extracted.items()}

    st.subheader("Review and correct extracted fields before saving")
    edited = {}
    cols = st.columns(2)
    for i, col_name in enumerate(COLUMNS):
        with cols[i % 2]:
            if col_name in ("LATITUDE", "LONGITUDE"):
                edited[col_name] = st.text_input(
                    col_name, value="", placeholder="auto-filled from address on save", disabled=True
                )
            else:
                edited[col_name] = st.text_input(col_name, value=extracted.get(col_name, ""))

    if st.button("Save to Excel", type="primary"):
        path = append_listing(edited)
        st.success(f"Saved to {path}")

st.divider()
st.caption(f"Workbook location: {DEFAULT_PATH}")
