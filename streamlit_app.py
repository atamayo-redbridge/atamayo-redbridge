import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import os
import io

# 🔹 Custom CSS Styling for Redbridge Branding (No Changes to Other UI Elements)
st.markdown("""
 <style>
/* 🔹 Global App Styling */
.stApp {
    background-color: #F8F9FA;
    font-family: Arial, sans-serif;
    color: #333333;
    padding: 20px;
}

/* 🔹 Title Styling */
h1 {
    color: #B22222;
    text-align: center;
    margin-bottom: 20px;
}

/* 🔹 Search Bar Styling */
.stTextInput>div>div>input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border-radius: 5px;
    border: 1px solid #B22222;
    padding: 10px;
    font-size: 16px;
}

/* 🔹 Darken Placeholder Text */
.stTextInput>div>div>input::placeholder {
    color: #444444 !important;
    opacity: 1;
}

/* 🔹 Button Styling */
.stButton>button {
    border-radius: 5px;
    font-size: 16px;
    padding: 10px 20px;
    background-color: #B22222;
    color: #FFFFFF;
    border: none;
}

.stButton>button:hover {
    background-color: #8B1A1A !important;
}

/* 🔹 Download Button */
.stDownloadButton>button {
    border-radius: 5px;
    font-size: 16px;
    padding: 10px 20px;
    background-color: #B22222;
    color: #FFFFFF !important;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Load Excel File
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, dtype=str)
        df["Name_Lower"] = df["Name"].str.strip()
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
        df["Name_Lower"] = df["Name"].str.strip()
        st.success("✅ File uploaded successfully! / Archivo cargado exitosamente!")
    else:
        st.error("❌ No file uploaded. Please provide an Excel file.")
        st.stop()

# Sidebar: Language Selection
st.sidebar.title("🌍 Language / Idioma")
selected_language = st.sidebar.radio("", ["English", "Español"])

# Language dictionary
languages = {
    "English": {
        "title": "Provider Name Lookup",
        "button_label": "Find",
        "clear_button": "🧹 Clear Search",
        "recent_searches": "Recent Searches",
        "download_results": "📥 Download Results",
        "exact_match": "✅ Exact Match Found",
        "not_found": "⚠️ No Exact Match, but Similar Names Found:",
        "does_not_exist": "❌ Name Does Not Exist in the database.",
        "placeholder": "🔎 Type a name here..."
    },
    "Español": {
        "title": "Búsqueda de Proveedores",
        "button_label": "Buscar",
        "clear_button": "🧹 Limpiar Búsqueda",
        "recent_searches": "Búsquedas Recientes",
        "download_results": "📥 Descargar Resultados",
        "exact_match": "✅ Coincidencia Exacta Encontrada",
        "not_found": "⚠️ No hay coincidencia exacta, pero encontramos nombres similares:",
        "does_not_exist": "❌ El nombre no existe en la base de datos.",
        "placeholder": "🔎 Escriba un nombre aquí..."
    },
}

lang = languages[selected_language]

# Title
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

# Search Input
input_name = st.text_input("", "", placeholder=lang["placeholder"]).strip()

# Buttons
find_button = st.button(lang["button_label"])
clear_button = st.button(lang["clear_button"])

# Search Logic
if find_button and input_name:
    with st.spinner("🔍 Searching... Please wait!"):
        exact_matches = df[df["Name"] == input_name]

        # ✅ Exact Match Found (Styled Message - Black Text, Green Background)
        if not exact_matches.empty:
            st.markdown(f"""
                <div style="background-color: #D4EDDA; border-left: 5px solid #155724; color: black; padding: 10px; font-weight: bold;">
                ✅ {lang['exact_match']} ({len(exact_matches)} results found)
                </div>
            """, unsafe_allow_html=True)
            
            for _, row in exact_matches.iterrows():
                st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")

        # ⚠️ No Exact Match, but Similar Names Found (Yellow Background)
        else:
            possible_matches = process.extract(input_name, df["Name"].dropna().tolist(), scorer=fuzz.ratio, limit=5)
            if possible_matches:
                st.markdown(f"""
                    <div style="background-color: #FFF3CD; border-left: 5px solid #856404; color: black; padding: 10px; font-weight: bold;">
                    ⚠️ {lang['not_found']} ({len(possible_matches)} found)
                    </div>
                """, unsafe_allow_html=True)

                for name, _ in possible_matches:
                    match_data = df[df["Name"] == name]
                    if not match_data.empty:
                        st.write(f"🔹 **{name}** (ID: {match_data['ID'].values[0]})")

            # ❌ No Match Found (Red Background)
            else:
                st.markdown(f"""
                    <div style="background-color: #F8D7DA; border-left: 5px solid #721C24; color: black; padding: 10px; font-weight: bold;">
                    ❌ {lang['does_not_exist']}
                    </div>
                """, unsafe_allow_html=True)
