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

# Move Language Selection to the Top-Right Corner
st.sidebar.title("🌍 Language / Idioma")
selected_language = st.sidebar.radio("", ["English", "Español"])

# Language options
languages = {
    "English": {
        "title": "🔎 Name Lookup with Variations",
        "input_label": "Enter a name to check:",
        "button_label": "Find",
        "exact_match": "✅ Exact Matches Found",
        "not_found": "⚠️ No Exact Match, but Similar Names Found:",
        "does_not_exist": "❌ Name Does Not Exist in the database.",
        "variations_found": "🟡 Unique Variations Found:",
        "status_not_sure": "❓ Status: Not Sure",
    },
    "Español": {
        "title": "🔎 Búsqueda de Nombres con Variaciones",
        "input_label": "Ingrese un nombre para verificar:",
        "button_label": "Buscar",
        "exact_match": "✅ Coincidencias Exactas Encontradas",
        "not_found": "⚠️ No hay coincidencia exacta, pero encontramos nombres similares:",
        "does_not_exist": "❌ El nombre no existe en la base de datos.",
        "variations_found": "🟡 Variaciones Únicas Encontradas:",
        "status_not_sure": "❓ Estado: No Seguro",
    },
}

lang = languages[selected_language]

# Title
st.markdown(f"<h1 style='text-align: center;'>{lang['title']}</h1>", unsafe_allow_html=True)

# User Input + Find Button
input_name = st.text_input(lang["input_label"], "").strip()
find_button = st.button(lang["button_label"])

# Run search only when button is clicked
if find_button and input_name:
    # Check for exact matches
    exact_matches = df[df["Name"].str.lower() == input_name.lower()]

    if not exact_matches.empty:
        st.success(f"{lang['exact_match']}:")
        unique_variations = set()  # Store unique variations

        for _, row in exact_matches.iterrows():
            st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")

            # Collect unique variations for this specific ID
            variations = row[["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
            unique_variations.update(variations)

        # Display unique variations (only once)
        if unique_variations:
            st.info(lang["variations_found"])
            for var in unique_variations:
                var_id = df[df["Name"] == var]["ID"].values[0] if var in df["Name"].values else "Unknown"
                st.write(f"🔸 **{var}** (ID: {var_id})")

    else:
        # Perform fuzzy matching safely
        try:
            possible_matches = process.extract(input_name, df["Name"].dropna().tolist(), scorer=fuzz.ratio, limit=5)
            matched_variations = set()  # Store unique variations across all fuzzy matches
            variations_displayed = False  # Track if we displayed variations

            if possible_matches:
                st.warning(lang["not_found"])
                
                for name, score in possible_matches:
                    match_data = df[df["Name"] == name]
                    if not match_data.empty:
                        match_id = match_data["ID"].values[0]
                        st.write(f"🔹 **{name}** (ID: {match_id}) - {lang['status_not_sure']}: {score}")

                        # Collect unique variations for this ID
                        variations = match_data.iloc[0][["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
                        matched_variations.update(variations)

                # Display unique variations once
                if matched_variations:
                    st.info(lang["variations_found"])
                    for var in matched_variations:
                        var_id = df[df["Name"] == var]["ID"].values[0] if var in df["Name"].values else "Unknown"
                        st.write(f"🔸 **{var}** (ID: {var_id})")
                        variations_displayed = True

                if not variations_displayed:
                    st.info(lang["status_not_sure"])
            else:
                st.error(lang["does_not_exist"])

        except Exception as e:
            st.error(f"❌ Error during fuzzy matching: {e} / Error durante la búsqueda difusa: {e}")
