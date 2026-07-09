import io

import fitz
import streamlit as st
from PIL import Image

from exporter import COLUMNS, append_listing, DEFAULT_PATH, ensure_workbook

st.set_page_config(page_title="Realtor Listing Extractor", layout="wide")
st.title("Realtor Listing Extractor")
st.caption(
    "Upload a screenshot or PDF of a realtor.ca listing detail page, "
    "then fill in the extracted fields below and save to Excel."
)

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

    st.subheader("Enter the extracted fields before saving")
    edited = {}
    cols = st.columns(2)
    for i, col_name in enumerate(COLUMNS):
        with cols[i % 2]:
            if col_name in ("LATITUDE", "LONGITUDE"):
                edited[col_name] = st.text_input(
                    col_name, value="", placeholder="auto-filled from address on save", disabled=True
                )
            else:
                edited[col_name] = st.text_input(col_name, value="")

    if st.button("Save to Excel", type="primary"):
        path = append_listing(edited)
        st.success(f"Saved to {path}")

st.divider()
st.caption(f"Workbook location: {DEFAULT_PATH}")
