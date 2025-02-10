import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import os
import io

# Custom CSS Styling for UI Enhancements
st.markdown("""
    <style>
    /* Style the search input */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
    }
    
    /* Style the buttons */
    .stButton>button {
        border-radius: 8px;
        font-size: 16px;
        padding: 8px 16px;
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    
    /* Style the sidebar */
    .css-1d391kg {
        background-color: #f8f9fa !important;
    }

    /* Style the main container */
    .main {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
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
        "title": "🔎 Name Lookup with Variations",
        "input_label": "Enter a name to check:",
        "button_label": "Find",
        "clear_button": "🧹 Clear Search",
        "recent_searches": "Recent Searches",
        "download_results": "📥 Download Results",
        "exact_match": "✅ Exact Match Found",
        "not_found": "⚠️ No Exact Match, but Similar Names Found:",
        "does_not_exist": "❌ Name Does Not Exist in the database.",
        "variations_found": "🟡 Unique Variations Found:",
        "status_not_sure": "❓ Status: Not Sure",
        "help_text": "Enter the exact name (case-sensitive, no extra spaces)",
    },
    "Español": {
        "title": "🔎 Búsqueda de Nombres con Variaciones",
        "input_label": "Ingrese un nombre para verificar:",
        "button_label": "Buscar",
        "clear_button": "🧹 Limpiar Búsqueda",
        "recent_searches": "Búsquedas Recientes",
        "download_results": "📥 Descargar Resultados",
        "exact_match": "✅ Coincidencia Exacta Encontrada",
        "not_found": "⚠️ No hay coincidencia exacta, pero encontramos nombres similares:",
        "does_not_exist": "❌ El nombre no existe en la base de datos.",
        "variations_found": "🟡 Variaciones Únicas Encontradas:",
        "status_not_sure": "❓ Estado: No Seguro",
        "help_text": "Ingrese el nombre exacto (distingue mayúsculas y espacios)",
    },
}

lang = languages[selected_language]

# Sidebar: Company Logo
st.sidebar.image("https://your-company-logo-url.com/logo.png", use_container_width=True)

# Sidebar: Recent Searches
st.sidebar.subheader(f"🔍 {lang['recent_searches']}")
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []

if st.session_state["search_history"]:
    for name in reversed(st.session_state["search_history"][-5:]):
        st.sidebar.write(f"🔹 {name}")
else:
    st.sidebar.write("🔹 No recent searches")

# Title
st.markdown(f"<h1 style='text-align: center;'>{lang['title']}</h1>", unsafe_allow_html=True)

# Search Input with Tooltip
input_name = st.text_input(
    f"🔍 {lang['input_label']}",
    "",
    help=lang["help_text"],
    placeholder="🔎 Type a name here..."
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
        if input_name not in st.session_state["search_history"]:
            st.session_state["search_history"].append(input_name)

        # Exact Matches
        exact_matches = df[df["Name"] == input_name]
        if not exact_matches.empty:
            st.success(f"{lang['exact_match']} ({len(exact_matches)} results found)")
            with st.expander(f"📌 View Exact Matches ({len(exact_matches)})"):
                for _, row in exact_matches.iterrows():
                    st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")

        else:
            possible_matches = process.extract(input_name, df["Name"].dropna().tolist(), scorer=fuzz.ratio, limit=5)
            if possible_matches:
                st.warning(f"⚠️ {lang['not_found']} ({len(possible_matches)} similar names found)")
                with st.expander(f"🔍 View Similar Matches ({len(possible_matches)})"):
                    for name, score in possible_matches:
                        match_data = df[df["Name"] == name]
                        if not match_data.empty:
                            match_id = match_data["ID"].values[0]
                            st.write(f"🔹 **{name}** (ID: {match_id}) - {lang['status_not_sure']}: {score}")

            else:
                st.error(lang["does_not_exist"])

    # Convert results to DataFrame for download
    result_df = pd.DataFrame({
        "Searched Name": [input_name],
        "Exact Matches": [", ".join(exact_matches["Name"].tolist())] if not exact_matches.empty else [""],
        "Matched IDs": [", ".join(exact_matches["ID"].tolist())] if not exact_matches.empty else [""]
    })

    buffer = io.BytesIO()
    result_df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Download Button
    st.download_button(
        label=lang["download_results"],
        data=buffer,
        file_name="Search_Results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Click to download search results as an Excel file"
    )
