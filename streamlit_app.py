import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import os

# Load Excel File
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, dtype=str)  # Ensure all data is treated as strings
        return df
    return None

# File path (update if necessary)
file_path = "data/Provider_Duplicates_Variations_Active.xlsx"
df = load_data(file_path)

# Ensure the file is loaded
if df is None:
    st.warning("⚠️ File not found! Please upload the database.")
    uploaded_file = st.file_uploader("Upload the Excel file / Cargar archivo Excel", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file, dtype=str)
        st.success("✅ File uploaded successfully! / Archivo cargado exitosamente!")
    else:
        st.error("❌ No file uploaded. Please provide an Excel file. / No se cargó ningún archivo. Por favor, suba un archivo Excel.")
        st.stop()

# Ensure necessary columns exist
required_columns = ["Name", "ID", "Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"❌ Missing columns in Excel file: {', '.join(missing_columns)} / Faltan columnas en el archivo de Excel: {', '.join(missing_columns)}")
    st.stop()

# Language options
languages = {
    "English": {
        "title": "🔎 Name Lookup with Variations",
        "input_label": "Enter a name to check:",
        "exact_match": "✅ Exact Match Found",
        "not_found": "⚠️ No Exact Match, but Similar Names Found:",
        "does_not_exist": "❌ Name Does Not Exist in the database.",
        "variations_found": "🟡 Possible Variations Found:",
        "status_not_sure": "❓ Status: Not Sure",
        "upload_label": "Upload the Excel file",
        "language_label": "Select Language:",
    },
    "Español": {
        "title": "🔎 Búsqueda de Nombres con Variaciones",
        "input_label": "Ingrese un nombre para verificar:",
        "exact_match": "✅ Coincidencia Exacta Encontrada",
        "not_found": "⚠️ No hay coincidencia exacta, pero encontramos nombres similares:",
        "does_not_exist": "❌ El nombre no existe en la base de datos.",
        "variations_found": "🟡 Posibles Variaciones Encontradas:",
        "status_not_sure": "❓ Estado: No Seguro",
        "upload_label": "Cargar archivo Excel",
        "language_label": "Seleccionar idioma:",
    },
}

# Select Language
selected_language = st.selectbox("🌍 Select Language / Seleccionar idioma:", list(languages.keys()))
lang = languages[selected_language]

st.title(lang["title"])

# User Input
input_name = st.text_input(lang["input_label"], "").strip()

if input_name:
    # Check for exact match
    exact_match = df[df["Name"].str.lower() == input_name.lower()]

    if not exact_match.empty:
        exact_id = exact_match["ID"].values[0]
        st.success(f"{lang['exact_match']}: **{input_name}** (ID: {exact_id})")
    else:
        # Perform fuzzy matching safely
        try:
            possible_matches = process.extract(input_name, df["Name"].dropna().tolist(), scorer=fuzz.ratio, limit=5)
            variations = [(name, score, df[df["Name"] == name]["ID"].values[0]) for name, score in possible_matches if isinstance(name, str) and score > 80]
        except Exception as e:
            variations = []
            st.error(f"❌ Error during fuzzy matching: {e} / Error durante la búsqueda difusa: {e}")

        if variations:
            st.warning(lang["not_found"])
            for name, score, id_num in variations:
                st.write(f"🔹 **{name}** (ID: {id_num}) - {lang['status_not_sure']}: {score}")
            st.info(lang["status_not_sure"])
        else:
            st.error(lang["does_not_exist"])

    # Check for name variations
    name_variations = df[df["Name"].str.lower() == input_name.lower()]
    if not name_variations.empty:
        var_list = name_variations.iloc[0][["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
        if var_list:
            st.info(lang["variations_found"])
            for variation in var_list:
                variation_id = df[df["Name"] == variation]["ID"].values[0] if variation in df["Name"].values else "Unknown"
                st.write(f"🔸 **{variation}** (ID: {variation_id})")
