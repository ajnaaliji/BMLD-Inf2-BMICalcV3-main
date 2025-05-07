# ==== Datei: 01_Datei.py ====
import streamlit as st
import pandas as pd
import base64
import time
import ast
from utils.data_manager import DataManager

# ===== Login-Schutz =====
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("/")
    st.stop()

# ===== Icons laden =====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

icons = {
    "chemie": load_icon_base64("assets/adrenaline.png"),
    "haematologie": load_icon_base64("assets/blood.png"),
    "klinische chemie": load_icon_base64("assets/rna.png")
}

# ===== Session-Daten =====
st.set_page_config(page_title="Fachansicht", page_icon="📂")
fach_key = st.session_state.get("fach", "").lower().strip()
username = st.session_state.get("username")

fach_namen = {
    "chemie": "Chemie",
    "haematologie": "Hämatologie",
    "klinische chemie": "Klinische Chemie"
}
ordner_pfade = {
    "chemie": "word_chemie",
    "haematologie": "word_haematologie",
    "klinische chemie": "word_klinische_chemie"
}

fach = fach_namen.get(fach_key, "Unbekannt")
fach_icon = icons.get(fach_key)

st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 20px; font-size: 36px;'>
    {fach}
    <img src="data:image/png;base64,{fach_icon}" width="42">
</h1>
""", unsafe_allow_html=True)

# ===== Navigation =====
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Start"):
        st.switch_page("Start.py")
with col2:
    if st.button("📝 Neuer Eintrag"):
        seiten = {
            "haematologie": "pages/02_Haematologie.py",
            "klinische chemie": "pages/04_Klinische Chemie.py",
            "chemie": "pages/03_Chemie.py"
        }
        st.switch_page(seiten.get(fach_key, "Start.py"))
with col3:
    if fach_key == "haematologie" and st.button("🦮 Zellatlas"):
        st.switch_page("pages/08_Referenz_Haematologie.py")
    elif fach_key == "klinische chemie" and st.button("📊 Referenzwerte"):
        st.switch_page("pages/07_Referenzwerte.py")

st.markdown("### Finde deine Einträge und lade sie herunter.")

# ===== DataManager initialisieren =====
data_manager = DataManager()
dh = data_manager._get_data_handler(f"{ordner_pfade.get(fach_key)}/{username}")

# === Einträge & Anhänge laden ===
if fach_key == "chemie":
    data_manager.load_user_data("chemie_eintraege", "data_chemie.csv", initial_value=[])
    eintrags_df = pd.DataFrame(st.session_state["chemie_eintraege"])
    dh_anhang = data_manager._get_data_handler(f"anhang_chemie/{username}")
elif fach_key == "klinische chemie":
    data_manager.load_user_data("klinische_eintraege", f"data_klinische_chemie_{username}.csv", initial_value=[])
    eintrags_df = pd.DataFrame(st.session_state["klinische_eintraege"])
    dh_anhang = data_manager._get_data_handler(f"anhang_klinische_chemie/{username}")
elif fach_key == "haematologie":
    data_manager.load_user_data("haematologie_eintraege", f"data_haematologie_{username}.csv", initial_value=[])
    eintrags_df = pd.DataFrame(st.session_state["haematologie_eintraege"])
    dh_anhang = data_manager._get_data_handler(f"anhang_haematologie/{username}")
else:
    eintrags_df = pd.DataFrame()

# ==== Prüfung auf gültige Daten ====
if eintrags_df.empty or "titel" not in eintrags_df.columns or "datum" not in eintrags_df.columns:
    st.info("Noch keine gültigen Einträge vorhanden.")
    st.stop()

# ==== Suche und Anzeige ====
suchbegriff = st.text_input("🔍 Suche nach Titel oder Datum").strip().lower()
eintrags_df["suchtext"] = eintrags_df["titel"].str.lower() + " " + eintrags_df["datum"].astype(str)
gefiltert = eintrags_df[eintrags_df["suchtext"].str.contains(suchbegriff, na=False)] if suchbegriff else eintrags_df

for _, row in gefiltert.iterrows():
    col1, col2 = st.columns([6, 2])
    with col1:
        st.markdown(f"🗓️ **{row['datum']}** – 📄 *{row['titel']}*")
    with col2:
        word_file = row.get("dateiname")
        if word_file:
            try:
                file_data = dh.read_binary(word_file)
                st.download_button(
                    label="⬇️ Word öffnen",
                    data=file_data,
                    file_name=word_file,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"word_{word_file}"
                )
            except Exception as e:
                st.warning(f"❌ Word-Datei fehlt: {e}")

    # === Anhänge anzeigen ===
    anhaenge = row.get("anhaenge", [])
    if isinstance(anhaenge, str):
        try:
            anhaenge = ast.literal_eval(anhaenge)
        except Exception:
            anhaenge = []

    if anhaenge:
        st.markdown("📌 Zugehörige Anhänge:")
        for anhang in list(dict.fromkeys(anhaenge)):
            file_data = None
            for _ in range(3):
                try:
                    file_data = dh_anhang.read_binary(anhang)
                    break
                except FileNotFoundError:
                    time.sleep(1)
            if file_data:
                st.download_button(
                    label=f"⬇️ {anhang}",
                    data=file_data,
                    file_name=anhang,
                    mime="application/pdf" if anhang.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"anhang_{anhang}"
                )
            else:
                st.error(f"❌ Anhang nicht gefunden: {anhang}")

# ==== Zurück zur Startseite ====
if st.button("🔙 Zurück zur Übersicht"):
    st.session_state.ansicht = "start"
    st.switch_page("Start.py")