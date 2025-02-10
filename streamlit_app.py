import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import os

# Load Excel File
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, dtype=str)  # Ensure string data type
        return df
    return None

# File path (update if necessary)
file_path = "data/Provider_Duplicates_Variations_Active.xlsx"
df = load_data(file_path)

# Ensure the file is loaded
if df is None:
    st.warning("⚠️ File not found! Please upload the database.")
    uploaded_file = st.file_uploader("Upload the Excel file", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file, dtype=str)
        st.success("✅ File uploaded successfully!")
    else:
        st.error("❌ No file uploaded. Please provide an Excel file.")
        st.stop()

# Ensure necessary columns exist
required_columns = ["Name", "ID", "Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"❌ Missing columns in Excel file: {', '.join(missing_columns)}")
    st.stop()

st.title("🔎 Name Lookup with Variations")

# User Input
input_name = st.text_input("Enter a name to check:", "").strip()

if input_name:
    # Check for exact match
    exact_match = df[df["Name"].str.lower() == input_name.lower()]

    if not exact_match.empty:
        exact_id = exact_match["ID"].values[0]
        st.success(f"✅ Exact Match Found: **{input_name}** (ID: {exact_id})")
    else:
        # Perform fuzzy matching safely
        try:
            possible_matches = process.extract(input_name, df["Name"].dropna().tolist(), scorer=fuzz.ratio, limit=5)
            variations = [(name, score, df[df["Name"] == name]["ID"].values[0]) for name, score in possible_matches if isinstance(name, str) and score > 80]
        except Exception as e:
            variations = []
            st.error(f"❌ Error during fuzzy matching: {e}")

        if variations:
            st.warning("⚠️ No Exact Match, but Similar Names Found:")
            for name, score, id_num in variations:
                st.write(f"🔹 **{name}** (ID: {id_num}) - Match Score: {score}")
            st.info("❓ Status: Not Sure")
        else:
            st.error("❌ Name Does Not Exist in the database.")

    # Check for name variations
    name_variations = df[df["Name"].str.lower() == input_name.lower()]
    if not name_variations.empty:
        var_list = name_variations.iloc[0][["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
        if var_list:
            st.info("🟡 Possible Variations Found:")
            for variation in var_list:
                variation_id = df[df["Name"] == variation]["ID"].values[0] if variation in df["Name"].values else "Unknown"
                st.write(f"🔸 **{variation}** (ID: {variation_id})")
