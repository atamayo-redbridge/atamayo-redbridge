import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import os
import io

# Custom CSS Styling for Redbridge Branding
st.markdown("""
 <style>
/* 🔹 Global App Styling */
.stApp {
    background-color: #F8F9FA; /* Light gray background */
    font-family: Arial, sans-serif;
    color: #333333;
    padding: 20px;
}

/* 🔹 Title Styling */
h1 {
    color: #B22222; /* Redbridge brand color */
    text-align: center;
    margin-bottom: 20px;
}

/* 🔹 Sidebar Styling */
.css-1d391kg {
    background-color: #FFFFFF !important; /* White sidebar */
    border-right: 1px solid #B22222; /* Red border */
}

/* 🔹 Buttons Styling */
.stButton>button {
    border-radius: 5px;
    font-size: 16px;
    padding: 10px 20px;
    background-color: #B22222; /* Red primary button */
    color: #FFFFFF;
    border: none;
}

/* 🔹 Button Hover Effects */
.stButton>button:hover {
    background-color: #8B1A1A !important;
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

# Create two columns for layout
col1, col2 = st.columns([1, 3])  # 1:3 ratio for space distribution

# 🌍 Move Language Selector to Left Side
with col1:
    st.markdown("### 🌍 Language / Idioma")
    selected_language = st.radio("", ["English", "Español"])

# 🔍 Move Past Searches Below Language Selector
with col1:
    if "search_history" in st.session_state and st.session_state["search_history"]:
        st.markdown("### 🔍 Past Searches")
        
        # Show last 5 searches
        for search in st.session_state["search_history"][-5:][::-1]:
            st.write(f"🔹 {search}")

        # Option to Clear Search History
        if st.button("🗑️ Clear Search History"):
            st.session_state["search_history"] = []
            st.rerun()

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
        "variations_found": "🟡 Unique Variations Found:",
        "help_text": "Enter the exact name (case-sensitive, no extra spaces)",
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
        "variations_found": "🟡 Variaciones Únicas Encontradas:",
        "help_text": "Ingrese el nombre exacto (distingue mayúsculas y espacios)",
        "placeholder": "🔎 Escriba un nombre aquí..."
    },
}

lang = languages[selected_language]

# Title
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

# Search Input with Dynamic Placeholder
input_name = st.text_input(
    "",
    "",
    help=lang["help_text"],
    placeholder=lang["placeholder"]
).strip()

# Buttons
find_button = st.button(lang["button_label"])
clear_button = st.button(lang["clear_button"])

# Clear Search History
if clear_button:
    st.session_state["search_history"] = []
    st.rerun()

# Search Logic
if find_button and input_name:
    with st.spinner("🔍 Searching... Please wait!"):
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []
        if input_name not in st.session_state["search_history"]:
            st.session_state["search_history"].append(input_name)

        # Exact Matches
        exact_matches = df[df["Name"] == input_name]
        if not exact_matches.empty:
            st.success(f"{lang['exact_match']} ({len(exact_matches)} results found)")
            with st.expander(f"📌 View Exact Matches ({len(exact_matches)})"):
                for _, row in exact_matches.iterrows():
                    st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")
