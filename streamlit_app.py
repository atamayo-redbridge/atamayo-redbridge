import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import os
import io

# Load Excel File
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, dtype=str)
        df["Name_Lower"] = df["Name"].str.strip()  # Precompute stripped names
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
        st.error("❌ No file uploaded. Please provide an Excel file. / No se cargó ningún archivo. Por favor, suba un archivo Excel.")
        st.stop()

# Sidebar for Language Selection
st.sidebar.title("🌍 Language / Idioma")
selected_language = st.sidebar.radio("", ["English", "Español"])

# Language dictionary
languages = {
    "English": {
        "title": "Provider Name Lookup",
        "input_label": "Enter a name to check:",
        "button_label": "Find",
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
        "title": "Búsqueda de Proveedores",
        "input_label": "Ingrese un nombre para verificar:",
        "button_label": "Buscar",
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

# Title
st.markdown(f"<h1 style='text-align: center;'>{lang['title']}</h1>", unsafe_allow_html=True)

# User Input + Find Button
input_name = st.text_input(
    lang["input_label"], 
    "", 
    help=lang["help_text"],  # Dynamic tooltip translation
    placeholder="E.g., John A. Doe"
).strip()
find_button = st.button(lang["button_label"])

# Initialize session state for recent searches
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []

# Sidebar: Display recent searches
st.sidebar.subheader(f"🔍 {lang['recent_searches']}")
for name in st.session_state["search_history"][-5:]:  # Show last 5 searches
    st.sidebar.write(f"🔹 {name}")

# Search logic
if find_button and input_name:
    # Save search history
    if input_name not in st.session_state["search_history"]:
        st.session_state["search_history"].append(input_name)

    # Check for exact matches (Case-sensitive, space-sensitive)
    exact_matches = df[df["Name"] == input_name]  

    if not exact_matches.empty:
        st.success(f"{lang['exact_match']}:")
        unique_variations = set()

        for _, row in exact_matches.iterrows():
            st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")

            # Collect unique variations
            variations = row[["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
            unique_variations.update(variations)

        if unique_variations:
            st.info(lang["variations_found"])
            for var in unique_variations:
                var_id = df[df["Name"] == var]["ID"].values[0] if var in df["Name"].values else "Unknown"
                st.write(f"🔸 **{var}** (ID: {var_id})")

    else:
        # Perform fuzzy matching (case-insensitive)
        try:
            possible_matches = process.extract(input_name, df["Name"].dropna().tolist(), scorer=fuzz.ratio, limit=5)
            matched_variations = set()

            if possible_matches:
                st.warning(lang["not_found"])
                
                for name, score in possible_matches:
                    if name != input_name:  # Avoid exact matches
                        match_data = df[df["Name"] == name]
                        if not match_data.empty:
                            match_id = match_data["ID"].values[0]
                            st.write(f"🔹 **{name}** (ID: {match_id}) - {lang['status_not_sure']}: {score}")

                            # Collect unique variations
                            variations = match_data.iloc[0][["Variation 1", "Variation 2", "Variation 3", "Variation 4", "Variation 5"]].dropna().tolist()
                            matched_variations.update(variations)

                if matched_variations:
                    st.info(lang["variations_found"])
                    for var in matched_variations:
                        var_id = df[df["Name"] == var]["ID"].values[0] if var in df["Name"].values else "Unknown"
                        st.write(f"🔸 **{var}** (ID: {var_id})")

            else:
                st.error(lang["does_not_exist"])

        except Exception as e:
            st.error(f"❌ Error during fuzzy matching: {e} / Error durante la búsqueda difusa: {e}")

    # Convert search results to a DataFrame for download
    result_df = pd.DataFrame({
        "Searched Name": [input_name],
        "Exact Matches": [", ".join(exact_matches["Name"].tolist())] if not exact_matches.empty else [""],
        "Matched IDs": [", ".join(exact_matches["ID"].tolist())] if not exact_matches.empty else [""]
    })

    # Create a downloadable Excel file
    buffer = io.BytesIO()
    result_df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Provide a download button
    st.download_button(
        label=lang["download_results"],
        data=buffer,
        file_name="Search_Results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
