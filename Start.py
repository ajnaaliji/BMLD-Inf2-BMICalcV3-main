import streamlit as st
import pandas as pd
import base64
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ===== Seiteneinstellungen =====
st.set_page_config(
    page_title="Laborjournal",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== Init Block =====
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="App_Melinja")
login_manager = LoginManager(data_manager)

# ===== Login/Register anzeigen, wenn nicht eingeloggt =====
if st.session_state.get("authentication_status") is not True:
    login_manager.login_register()
    st.stop()

# ===== Hilfsfunktion zum Icon-Encoding =====
def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ===== Icons vorbereiten =====
icon_chemie = load_icon_base64("assets/chemie.png")
icon_haema = load_icon_base64("assets/blood.png")
icon_klinik = load_icon_base64("assets/clinical_chemistry.png")
icon_header = load_icon_base64("assets/labor.png")

# ===== CSS global (Hintergrund + Textzentrierung) =====
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to bottom, #eaf2f8, #f5f9fc);
        }
        h1, h2, h3, h4, h5, h6, p {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

if st.button("Logout 🔓"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===== Begrüßung oben rechts =====
if "username" in st.session_state:
    st.markdown(f"""
        <div style='text-align: right; font-size: 20px; font-weight: bold; margin-top: 10px;'>
            👋 Schön, dass du wieder da bist, <span style='color:#2c3e50;'>{st.session_state['username']}</span>!
            <div style='font-size: 16px; color: #888;'>Bereit für dein nächstes Praktikum?</div>
        </div>
    """, unsafe_allow_html=True)

# ===== Titelbereich mit Icon =====
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

# ===== Fachauswahl HTML-Karten =====
if st.session_state.get("authentication_status") is True:
    st.markdown("<h3 style='text-align: center;'>Wähle dein gewünschtes Fach:</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <a href="/?fach=chemie&ansicht=start" target="_self" style="text-decoration: none;">
                <div style="
                    background-color: #e0f7fa;
                    padding: 20px;
                    border-radius: 16px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: all 0.3s ease;
                    margin-bottom: 20px;
                " onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'">
                    <img src="data:image/png;base64,{icon_chemie}" width="40"><br>
                    <span style="font-size: 18px; font-weight: bold; color: #2c3e50;">Chemie</span>
                </div>
            </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <a href="/?fach=haematologie&ansicht=start" target="_self" style="text-decoration: none;">
                <div style="
                    background-color: #fdecea;
                    padding: 20px;
                    border-radius: 16px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: all 0.3s ease;
                    margin-bottom: 20px;
                " onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'">
                    <img src="data:image/png;base64,{icon_haema}" width="40"><br>
                    <span style="font-size: 18px; font-weight: bold; color: #2c3e50;">Hämatologie</span>
                </div>
            </a>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <a href="/?fach=klinische chemie&ansicht=start" target="_self" style="text-decoration: none;">
                <div style="
                    background-color: #e8f5e9;
                    padding: 20px;
                    border-radius: 16px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: all 0.3s ease;
                    margin-bottom: 20px;
                " onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'">
                    <img src="data:image/png;base64,{icon_klinik}" width="40"><br>
                    <span style="font-size: 18px; font-weight: bold; color: #2c3e50;">Klinische Chemie</span>
                </div>
            </a>
        """, unsafe_allow_html=True)

# ===== Query-Parameter auslesen und weiterleiten =====
params = st.query_params
if "fach" in params:
    st.session_state["fach"] = params["fach"]
    st.session_state["ansicht"] = params.get("ansicht", "start")
    st.switch_page("pages/01_Datei.py")

# ===== Hinweis unten =====
st.markdown("""
<div style="background-color: #FFF3CD; padding: 15px; border-radius: 8px; font-size: 16px; margin-top: 40px;">
    ⚠️ <strong>Hinweis:</strong> Dieses Journal unterstützt dich bei der Organisation deines Studiums – es ersetzt jedoch keine individuelle Lernstrategie.
</div>
""", unsafe_allow_html=True)
