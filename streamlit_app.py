import os
import io

# 🔹 Custom CSS Styling for Redbridge Branding (Minimal Changes)
# Custom CSS Styling for Redbridge Branding
st.markdown("""
 <style>
/* 🔹 Global App Styling */
@@ -17,7 +17,7 @@
/* 🔹 Title Styling */
h1 {
    color: #B22222;
    color: #B22222; /* Redbridge brand color */
    text-align: center;
    margin-bottom: 20px;
}
@@ -34,10 +34,23 @@
/* 🔹 Darken Placeholder Text */
.stTextInput>div>div>input::placeholder {
    color: #444444 !important;
    color: #444444 !important; /* Darker contrast */
    opacity: 1;
}
/* 🔹 Sidebar Styling */
.css-1d391kg {
    background-color: #FFFFFF !important;
    border-right: 1px solid #B22222;
}
/* 🔹 Sidebar Title ("Language / Idioma") */
.stSidebar h1, .stSidebar h2, .stSidebar h3 {
    color: #FFFFFF !important;
    font-size: 18px;
    font-weight: bold;
}
/* 🔹 Button Styling */
.stButton>button {
    border-radius: 5px;
@@ -61,6 +74,33 @@
    color: #FFFFFF !important;
    border: none;
}
/* ✅ Success Message (Green Background, Black Text) */
div[data-testid="stNotification-success"], div[data-testid="stAlert-success"], div[role="alert"][class*="stSuccess"] {
    background-color: #D4EDDA !important; /* Light green */
    border-left: 5px solid #155724 !important;
    color: #000000 !important; /* Black text */
    font-weight: bold;
    padding: 10px;
}
/* ⚠️ Warning Message (Yellow Background, Black Text) */
div[data-testid="stNotification-warning"], div[data-testid="stAlert-warning"], div[role="alert"][class*="stWarning"] {
    background-color: #FFF3CD !important; /* Light yellow */
    border-left: 5px solid #856404 !important;
    color: #000000 !important; /* Black text */
    font-weight: bold;
    padding: 10px;
}
/* ❌ Error Message (Red Background, Black Text) */
div[data-testid="stNotification-error"], div[data-testid="stAlert-error"], div[role="alert"][class*="stError"] {
    background-color: #F8D7DA !important; /* Light red */
    border-left: 5px solid #721C24 !important;
    color: #000000 !important; /* Black text */
    font-weight: bold;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

@@ -105,6 +145,8 @@ def load_data(file_path):
        "exact_match": "✅ Exact Match Found",
        "not_found": "⚠️ No Exact Match, but Similar Names Found:",
        "does_not_exist": "❌ Name Does Not Exist in the database.",
        "variations_found": "🟡 Unique Variations Found:",
        "help_text": "Enter the exact name (case-sensitive, no extra spaces)",
        "placeholder": "🔎 Type a name here..."
    },
    "Español": {
@@ -116,6 +158,8 @@ def load_data(file_path):
        "exact_match": "✅ Coincidencia Exacta Encontrada",
        "not_found": "⚠️ No hay coincidencia exacta, pero encontramos nombres similares:",
        "does_not_exist": "❌ El nombre no existe en la base de datos.",
        "variations_found": "🟡 Variaciones Únicas Encontradas:",
        "help_text": "Ingrese el nombre exacto (distingue mayúsculas y espacios)",
        "placeholder": "🔎 Escriba un nombre aquí..."
    },
}
@@ -125,48 +169,70 @@ def load_data(file_path):
# Title
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

# Search Input
input_name = st.text_input("", "", placeholder=lang["placeholder"]).strip()
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
        exact_matches = df[df["Name"] == input_name]
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []
        if input_name not in st.session_state["search_history"]:
            st.session_state["search_history"].append(input_name)

        # ✅ Exact Match Found (Styled Message)
        # Exact Matches
        exact_matches = df[df["Name"] == input_name]
        if not exact_matches.empty:
            st.markdown(f"""
                <div style="background-color: #D4EDDA; border-left: 5px solid #155724; color: black; padding: 10px; font-weight: bold;">
                ✅ {lang['exact_match']} ({len(exact_matches)} results found)
                </div>
            """, unsafe_allow_html=True)
            
            for _, row in exact_matches.iterrows():
                st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")
        # ⚠️ No Exact Match, but Similar Names Found
            st.success(f"{lang['exact_match']} ({len(exact_matches)} results found)")
            with st.expander(f"📌 View Exact Matches ({len(exact_matches)})"):
                for _, row in exact_matches.iterrows():
                    st.write(f"🔹 **{row['Name']}** (ID: {row['ID']})")
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
            # ❌ No Match Found (Styled Message)
                st.warning(f"⚠️ {lang['not_found']} ({len(possible_matches)} {'similar names found' if selected_language == 'English' else 'nombres similares encontrados'})")
                
                with st.expander(f"🔍 {'View Similar Matches' if selected_language == 'English' else 'Ver Nombres Similares'} ({len(possible_matches)})"):
                    for name, score in possible_matches:
                        match_data = df[df["Name"] == name]
                        if not match_data.empty:
                            match_id = match_data["ID"].values[0]
                            st.write(f"🔹 **{name}** (ID: {match_id})")
            else:
                st.markdown(f"""
                    <div style="background-color: #F8D7DA; border-left: 5px solid #721C24; color: black; padding: 10px; font-weight: bold;">
                    ❌ {lang['does_not_exist']}
                    </div>
                """, unsafe_allow_html=True)
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
