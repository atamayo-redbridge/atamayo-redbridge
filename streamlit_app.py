import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process

# Load Excel File (Make sure to update the file path)
@st.cache_data
def load_data():
    file_path = "Provider_Duplicates_Variations_Active.xlsx"  # Change to your file path
    df = pd.read_excel(file_path)
    return df

df = load_data()

# Ensure the column name matches the Excel file
name_column = "Name"  # Change if needed

# Language options
languages = {
    "English": {
        "title": "Name Lookup System",
        "input_label": "Enter a name to check:",
        "exists": "✅ Name Exists in the database.",
        "not_sure": "⚠️ Name Not Found, but we found similar names:",
        "status_not_sure": "❓ Status: Not Sure",
        "does_not_exist": "❌ Name Does Not Exist in the database.",
        "language_label": "Select Language:",
    },
    "Español": {
        "title": "Sistema de Búsqueda de Nombres",
        "input_label": "Ingrese un nombre para verificar:",
        "exists": "✅ El nombre existe en la base de datos.",
        "not_sure": "⚠️ Nombre no encontrado, pero encontramos nombres similares:",
        "status_not_sure": "❓ Estado: No Seguro",
        "does_not_exist": "❌ El nombre no existe en la base de datos.",
        "language_label": "Seleccionar idioma:",
    },
}

# Select Language
selected_language = st.selectbox("🌍 Select Language / Seleccionar idioma:", list(languages.keys()))
lang = languages[selected_language]

st.title(lang["title"])

# User Input
input_name = st.text_input(lang["input_label"], "")

if input_name:
    # Check for exact match
    exact_match = df[df[name_column].str.lower() == input_name.lower()]

    if not exact_match.empty:
        st.success(lang["exists"])
    else:
        # Check for variations using fuzzy matching
        possible_matches = process.extract(input_name, df[name_column], scorer=fuzz.ratio, limit=5)
        variations = [name for name, score in possible_matches if score > 80]  # Adjust threshold if needed

        if variations:
            st.warning(lang["not_sure"])
            st.write(variations)
            st.info(lang["status_not_sure"])
        else:
            st.error(lang["does_not_exist"])
