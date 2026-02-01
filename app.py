import io
import csv
import pandas as pd
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="CSV Merger",
    layout="wide"
)

st.title("CSV Merger")
st.write(
    "Upload multiple CSV files from your computer, merge them into one file, "
    "and download the result."
)

# -----------------------------
# Sidebar settings
# -----------------------------
with st.sidebar:
    st.header("CSV Settings")

    read_delimiter = st.text_input(
        "Input delimiter",
        value=",",
        help="Delimiter used in the uploaded CSV files (e.g. , ; | or \\t)"
    )

    output_delimiter = st.text_input(
        "Output delimiter",
        value=";",
        help="Delimiter for the merged CSV file"
    )

    quote_strings = st.checkbox(
        "Quote all fields in output",
        value=True,
        help="If enabled, all values will be wrapped in quotes in the output CSV"
    )

# -----------------------------
# File upload
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload one or more CSV files",
    type="csv",
    accept_multiple_files=True
)

# -----------------------------
# Processing
# -----------------------------
if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded.")

    dataframes = []
    errors = []

    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(
                uploaded_file,
                delimiter=read_delimiter
            )
            # Track origin of each row (optional but useful)
            df["__source_file__"] = uploaded_file.name
            dataframes.append(df)
        except Exception as e:
            errors.append((uploaded_file.name, str(e)))

    if errors:
        st.error("Some files could not be processed:")
        for name, message in errors:
            st.write(f"- **{name}**: {message}")
        st.stop()

    # Merge all CSVs
    merged_df = pd.concat(dataframes, ignore_index=True)

    # -----------------------------
    # Preview
    # -----------------------------
    st.subheader("Preview merged data")
    st.write(
        f"Rows: {len(merged_df):,} • Columns: {merged_df.shape[1]}"
    )
    st.dataframe(merged_df, use_container_width=True)

    # -----------------------------
    # Download
    # -----------------------------
    output_buffer = io.StringIO()
    quoting_mode = csv.QUOTE_ALL if quote_strings else csv.QUOTE_MINIMAL

    merged_df.to_csv(
        output_buffer,
        sep=output_delimiter,
        index=False,
        quoting=quoting_mode
    )

    st.download_button(
        label="⬇️ Download merged CSV",
        data=output_buffer.getvalue().encode("utf-8"),
        file_name="merged_output.csv",
        mime="text/csv"
    )

else:
    st.info("Upload CSV files to begin.")
