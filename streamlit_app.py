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
        "button_label": "Find",
        "exact_match": "✅ Exact Matches Found",
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
        "button_label": "Buscar",
        "exact_match": "✅ Coincidencias Exactas Encontradas",
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

# User Input + Find Button
input_name = st.text_input(lang["input_label"], "").strip()
find_button = st.button(lang["button_label"])

# Run search only when button is clicked
if find_button and input_name:
    # Check for exact matches
    exact_matches = df[df["Name"].str.lower() == input_name.lower()]

    if not exact_matches.empty:
        st.success(f"{lang['exact_match']}:")
        for _, row in exact_matches.iterrows():
            st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")
            
            # Show variations if they exist
            variations = row[["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
            if variations:
                st.info(lang["variations_found"])
                for var in variations:
                    var_id = df[df["Name"] == var]["ID"].values[0] if var in df["Name"].values else "Unknown"
                    st.write(f"🔸 **{var}** (ID: {var_id})")
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

                # Check for variations in matched names
                var_match = df[df["Name"] == name]
                if not var_match.empty:
                    var_list = var_match.iloc[0][["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
                    if var_list:
                        st.info(lang["variations_found"])
                        for var in var_list:
                            var_id = df[df["Name"] == var]["ID"].values[0] if var in df["Name"].values else "Unknown"
                            st.write(f"🔸 **{var}** (ID: {var_id})")

            st.info(lang["status_not_sure"])
        else:
            st.error(lang["does_not_exist"])
