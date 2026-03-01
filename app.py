import streamlit as st
import tempfile
import time
from pathlib import Path
import pandas as pd
from docling.document_converter import DocumentConverter

st.set_page_config(page_title="PDF Table Extractor", layout="wide")

st.title("📄 PDF Table Extractor to Excel")
st.write("Upload a PDF file. All detected tables will be converted into a single Excel file.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_pdf_path = Path(tmp_file.name)

    pdf_name = uploaded_file.name.replace(".pdf", "")
    output_excel = f"{pdf_name}.xlsx"

    st.info("Processing PDF... Please wait ⏳")

    start_time = time.time()

    try:
        doc_converter = DocumentConverter()
        conv_res = doc_converter.convert(tmp_pdf_path)

        tables = conv_res.document.tables

        if len(tables) == 0:
            st.warning("No tables detected in this PDF.")
        else:
            # Create Excel writer
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:

                for table_ix, table in enumerate(tables):
                    df = table.export_to_dataframe(doc=conv_res.document)

                    sheet_name = f"Table_{table_ix + 1}"
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

            end_time = time.time() - start_time

            st.success(f"✅ Extracted {len(tables)} tables in {end_time:.2f} seconds")

            # Download button
            with open(output_excel, "rb") as f:
                st.download_button(
                    label="📥 Download Excel File",
                    data=f,
                    file_name=output_excel,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"Error: {e}")