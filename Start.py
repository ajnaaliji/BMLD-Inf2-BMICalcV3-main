import streamlit as st
import base64
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
from utils.ui_helpers import apply_theme

# ===== Seiteneinstellungen =====
st.set_page_config(
    page_title="Laborjournal",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== Initialisierung =====
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="App_Melinja")
login_manager = LoginManager(data_manager)

# ===== Theme-Schalter (nur auf Startseite nötig) =====
if "theme" not in st.session_state:
    st.session_state.theme = "light"
mode = st.radio("🌓 Design-Modus wählen:", ["light", "dark"], index=0 if st.session_state.theme == "light" else 1, horizontal=True)
st.session_state.theme = mode

# ===== Theme anwenden =====
apply_theme()

# ===== Login/Register =====
if st.session_state.get("authentication_status") is not True:
    login_manager.login_register()
    st.stop()

# ===== Hilfsfunktion: Icon einlesen =====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ===== Icons laden =====
icon_chemie = load_icon_base64("assets/chemie.png")
icon_haema = load_icon_base64("assets/blood.png")
icon_klinik = load_icon_base64("assets/clinical_chemistry.png")
icon_header = load_icon_base64("assets/labor.png")

# ===== Logout-Button =====
if st.button("Logout 🔓"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===== Begrüßung =====
if "username" in st.session_state:
    st.markdown(f"""
        <div style='text-align: right; font-size: 20px; font-weight: bold; margin-top: 10px;'>
            👋 Hallo, <span style='color:#2c3e50;'>{st.session_state['username']}</span>!
            <div style='font-size: 16px; color: #888;'>Bereit für dein nächstes Praktikum?</div>
        </div>
    """, unsafe_allow_html=True)

# ===== Titelbereich =====
st.markdown(f"""
    <div style='text-align: center; margin-top: 30px; margin-bottom: 20px;'>
        <p style='font-size: 22px; color: #666;'>Dein persönliches</p>
        <h1 style='font-size: 50px; font-weight: bold;'>
            Laborjournal <img src="data:image/png;base64,{icon_header}" width="36" style="vertical-align: middle;">
        </h1>
    </div>
""", unsafe_allow_html=True)

# ===== Einführungstext =====
st.markdown("""
<div style="background-color: #dceeff; padding: 20px; border-radius: 10px; font-size: 18px; text-align: center; margin-bottom: 40px;">
    <p>Plane, dokumentiere und behalte den Überblick über deine Praktika – alles an einem Ort.</p>
    <p>Wähle ein Fach – und bring Ordnung ins Versuchswirrwarr.</p>
    <p><strong>Laborkittel an, Journal starten. 🧪</strong></p>
</div>
""", unsafe_allow_html=True)

# ===== Fachauswahl-Karten =====
st.markdown("<h3 style='text-align: center;'>Wähle dein gewünschtes Fach:</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="fachkarte">
            <img src="data:image/png;base64,{icon_chemie}" width="40"><br>
            <span style="font-size: 18px; font-weight: bold;">Chemie</span>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Fach öffnen", key="chemie_btn"):
        st.session_state["fach"] = "chemie"
        st.session_state["ansicht"] = "start"
        st.switch_page("pages/01_Datei.py")

with col2:
    st.markdown(f"""
        <div class="fachkarte">
            <img src="data:image/png;base64,{icon_haema}" width="40"><br>
            <span style="font-size: 18px; font-weight: bold;">Hämatologie</span>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Fach öffnen", key="haema_btn"):
        st.session_state["fach"] = "haematologie"
        st.session_state["ansicht"] = "start"
        st.switch_page("pages/01_Datei.py")

with col3:
    st.markdown(f"""
        <div class="fachkarte">
            <img src="data:image/png;base64,{icon_klinik}" width="40"><br>
            <span style="font-size: 18px; font-weight: bold;">Klinische Chemie</span>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Fach öffnen", key="klinik_btn"):
        st.session_state["fach"] = "klinische chemie"
        st.session_state["ansicht"] = "start"
        st.switch_page("pages/01_Datei.py")

# ===== Hinweis unten =====
st.markdown("""
<div style="background-color: #FFF3CD; padding: 15px; border-radius: 8px; font-size: 16px; margin-top: 40px;">
    ⚠️ <strong>Hinweis:</strong> Dieses Journal unterstützt dich bei der Organisation deines Studiums – es ersetzt jedoch keine individuelle Lernstrategie.
</div>
""", unsafe_allow_html=True)
