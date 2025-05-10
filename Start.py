import streamlit as st
import base64
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
from utils.ui_helpers import apply_theme
from PIL import Image
import io

# ===== Hilfsfunktion: Icon einlesen =====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
# ===== Icons laden =====
icon_chemie = load_icon_base64("assets/chemie.png")
icon_haema = load_icon_base64("assets/blood.png")
icon_klinik = load_icon_base64("assets/clinical_chemistry.png")
icon_header = load_icon_base64("assets/labor.png")
icon_screen = load_icon_base64("assets/screen.png")
icon_hello = load_icon_base64("assets/groundhog.png")
icon_chemical = load_icon_base64("assets/chemical.png")
icon_journal = load_icon_base64("assets/journal.png")

def load_icon_bytes(path):
    with open(path, "rb") as image_file:
        return image_file.read()
    
icon_bytes = load_icon_bytes("assets/journal.png")

# Konvertiere zu PIL.Image (für Streamlit-kompatibles Format)
icon_image = Image.open(io.BytesIO(icon_bytes))

# Setze das Page-Icon mit PIL.Image
st.set_page_config(
    page_title="Laborjournal",
    page_icon=icon_image,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== Initialisierung =====
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="App_Melinja")
login_manager = LoginManager(data_manager)

# ===== Theme-Schalter (links ausgerichtet) =====
if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.container():
    st.markdown(
        f"""
        <div style='text-align: left; display: flex; align-items: center; gap: 10px;'>
            <span style='font-size: 16px; color: {"#000" if st.session_state.theme == "light" else "#fff"};'>
                Design-Modus wählen:
            </span>
            <img src="data:image/png;base64,{icon_screen}" width="24">
        </div>
        """,
        unsafe_allow_html=True
    )

    mode = st.radio(
        "", ["light", "dark"],
        index=0 if st.session_state["theme"] == "light" else 1,
        horizontal=True
    )

    if mode != st.session_state["theme"]:
        st.session_state["theme"] = mode
        st.rerun()

# ===== Theme anwenden =====
apply_theme()

# ===== Custom CSS für Fachkarten, Buttons und Farben (dynamisch) =====
if st.session_state.theme == "dark":
    chemie_color = "#145A64"
    haema_color = "#78281F"
    klinik_color = "#1E8449"
    einleitung_bg = "#333333"
    einleitung_color = "#ffffff"
    hinweis_bg = "#5c5757"
    hinweis_color = "#ffffff"
else:
    chemie_color = "#e0f7fa"
    haema_color = "#fdecea"
    klinik_color = "#e8f5e9"
    einleitung_bg = "#dceeff"
    einleitung_color = "#000000"
    hinweis_bg = "#FFF3CD"
    hinweis_color = "#000000"

st.markdown(f"""
    <style>
        .fachkarte {{
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        }}
        .themed-button > button {{
            border-radius: 10px;
            width: 100%;
            margin-top: 10px;
        }}
        h1, h2, h3, h4, h5, h6, p {{
            text-align: center;
        }}
    </style>
""", unsafe_allow_html=True)

# ===== Login/Register =====
if st.session_state.get("authentication_status") is not True:
    login_manager.login_register()
    st.stop()
if st.session_state.get("registration_success", False):
    st.success("✅ Registrierung erfolgreich! Du kannst dich jetzt einloggen.")
    st.session_state["registration_success"] = False

# ===== Logout-Button =====
if st.button("Logout 🔓"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===== Begrüßung =====
if "username" in st.session_state:
    st.markdown(f"""
    <div style='text-align: right; font-size: 20px; font-weight: bold; margin-top: 10px;'>
        <img src="data:image/png;base64,{icon_hello}" width="40" style="vertical-align: middle; margin-right: 6px;">
        <span style='color:#2c3e50;'>{st.session_state['username']}</span>!
        <div style='font-size: 16px; color: #888;'>Bereit für dein nächstes Praktikum?</div>
    </div>
""", unsafe_allow_html=True)

# ===== Titelbereich =====
st.markdown(f"""
    <div style='text-align: center; margin-top: 30px; margin-bottom: 20px;'>
        <p style='font-size: 22px;'>Dein persönliches</p>
        <h1 style='font-size: 50px; font-weight: bold;'>
            Laborjournal <img src="data:image/png;base64,{icon_header}" width="36" style="vertical-align: middle;">
        </h1>
    </div>
""", unsafe_allow_html=True)

# ===== Einführungstext =====
st.markdown(f"""
<div style="background-color: {einleitung_bg}; color: {einleitung_color}; padding: 20px; border-radius: 10px; font-size: 18px; text-align: center; margin-bottom: 40px;">
    <p>Plane, dokumentiere und behalte den Überblick über deine Praktika, alles an einem Ort.</p>
    <p>Wähle ein Fach und bring Ordnung ins Versuchswirrwarr.</p>
    <p><strong>Laborkittel an, Journal starten. 🧪</strong></p>
</div>
""", unsafe_allow_html=True)

# ===== Fachauswahl-Karten =====
st.markdown("<h3 style='text-align: center;'>Wähle dein gewünschtes Fach:</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

farben = [chemie_color, haema_color, klinik_color]
symbole = [icon_chemie, icon_haema, icon_klinik]
namen = ["Chemie", "Hämatologie", "Klinische Chemie"]
schluessel = ["chemie", "haematologie", "klinische chemie"]

for col, icon, name, fach, farbe in zip([col1, col2, col3], symbole, namen, schluessel, farben):
    with col:
        st.markdown(f"""
            <div class="fachkarte" style="background-color: {farbe};">
                <img src="data:image/png;base64,{icon}" width="40"><br>
                <span style="font-size: 18px; font-weight: bold;">{name}</span>
            </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="themed-button">', unsafe_allow_html=True)
            if st.button("Fach öffnen", key=f"btn_{fach}"):
                st.session_state["fach"] = fach
                st.session_state["ansicht"] = "start"
                st.switch_page("pages/01_Datei.py")
            st.markdown('</div>', unsafe_allow_html=True)

# ===== Hinweis unten =====
st.markdown(f"""
<div style="background-color: {hinweis_bg}; color: {hinweis_color}; padding: 15px; border-radius: 8px; font-size: 16px; margin-top: 40px;">
    ⚠️ <strong>Hinweis:</strong> Dieses Journal unterstützt dich bei der Organisation deines Studiums, es ersetzt jedoch keine individuelle Lernstrategie.
</div>
""", unsafe_allow_html=True)

