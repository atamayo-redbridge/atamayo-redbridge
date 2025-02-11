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

/* 🔹 Search Bar Styling */
.stTextInput>div>div>input {
    background-color: #FFFFFF !important; /* White background */
    color: #000000 !important; /* Black text */
    border-radius: 5px;
    border: 1px solid #B22222; /* Red border */
    padding: 10px;
    font-size: 16px;
}

/* 🔹 Darken the Placeholder Text */
.stTextInput>div>div>input::placeholder {
    color: #555555 !important; /* Dark gray placeholder text */
    opacity: 1;
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

/* 🔹 Download Button */
div[data-testid="stDownloadButton"] button {
    border-radius: 5px !important;
    font-size: 16px !important;
    padding: 10px 20px !important;
    background-color: #B22222 !important; /* Redbridge Red */
    color: #FFFFFF !important; /* White text */
    font-weight: bold !important;
    border: none !important;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2) !important;
}

/* 🔹 ✅ Success Message (Green Background, Black Text) */
div[data-testid="stNotification"], div[data-testid="stAlert-success"] {
    background-color: #D4EDDA !important; /* Light green background */
    color: #000000 !important; /* Black text */
    font-weight: bold;
}

/* 🔹 ⚠️ Warning Message (Yellow Background, Black Text) */
div[data-testid="stNotification"], div[data-testid="stAlert-warning"] {
    background-color: #FFF3CD !important; /* Light yellow background */
    color: #000000 !important; /* Black text */
    font-weight: bold;
}

/* 🔹 ❌ Error Message (Red Background, Black Text) */
div[data-testid="stNotification"], div[data-testid="stAlert-error"] {
    background-color: #F8D7DA !important; /* Light red background */
    color: #000000 !important; /* Black text */
    font-weight: bold;
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
        "variations_found": "🟡 Unique Variations Found:",
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
        "placeholder": "🔎 Escriba un nombre aquí..."
    },
}

lang = languages[selected_language]

# Create a layout with two columns
col1, col2 = st.columns([1, 3])  # Adjust width ratio

# Left Column: Past Searches
with col1:
    if "search_history" in st.session_state and st.session_state["search_history"]:
        st.markdown(f"### 🔍 {lang['recent_searches']}")
        for search in st.session_state["search_history"][-5:][::-1]:
            st.write(f"🔹 {search}")
        
        if st.button("🗑️ Clear Search History"):
            st.session_state["search_history"] = []
            st.rerun()

# Right Column: Search Input and Results
with col2:
    # Title
    st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

    # Search Bar
    input_name = st.text_input(
        "",
        "",
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
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []
        if input_name not in st.session_state["search_history"]:
            st.session_state["search_history"].append(input_name)

        exact_matches = df[df["Name"] == input_name]
        if not exact_matches.empty:
            st.success(f"{lang['exact_match']} ({len(exact_matches)} results found)")
        else:
            st.warning(f"{lang['not_found']}")

    # Download Button
    st.download_button(
        label=lang["download_results"],
        data="",
        file_name="Search_Results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
