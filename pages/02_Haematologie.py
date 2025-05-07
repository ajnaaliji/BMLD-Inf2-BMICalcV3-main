import streamlit as st
import math
import base64
import ast
import os
import io
import tempfile
import pandas as pd
from docx.shared import Inches
from PIL import Image

from docx import Document
from utils.data_manager import DataManager
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import uuid

st.set_page_config(page_title="Blutbilddifferenzierung", page_icon="🩸")

# ==== Benutzername und DataManager vorbereiten ====
from utils.data_manager import DataManager
import pandas as pd

username = st.session_state.get("username", "anonymous")
data_manager = DataManager()

# Hämatologie-Daten in Session registrieren, falls leer oder nicht vorhanden
try:
    data_manager.load_user_data("haematologie_df", f"data_haematologie_{username}.csv", initial_value=pd.DataFrame())
except pd.errors.EmptyDataError:
    st.warning("⚠️ Datei war leer – neue Session gestartet.")
    st.session_state["haematologie_df"] = []

# Manuell absichern (immer nötig!)
if "haematologie_df" not in st.session_state:
    st.session_state["haematologie_df"] = pd.DataFrame()
data_manager.register_data("haematologie_df", st.session_state["haematologie_df"])

# ==== Benutzername und DataManager vorbereiten ====
dh = data_manager._get_data_handler(f"word_haematologie/{username}")

# ==== Dateipfade und Ordner definieren ====
dateipfad = f"data/data_haematologie_{username}.csv"
image_folder = f"bilder_haematologie/{username}"
anhang_ordner = f"anhang_haematologie/{username}"
os.makedirs(os.path.dirname(dateipfad), exist_ok=True)

# ==== Handler ====
dh_img = data_manager._get_data_handler(image_folder)
dh_docs = data_manager._get_data_handler(anhang_ordner)
os.makedirs(dh_img.root_path, exist_ok=True)
os.makedirs(dh_docs.root_path, exist_ok=True)

if "authentication_status" not in st.session_state or not st.session_state.authentication_status:
    st.error("🚫 Zugriff verweigert. Bitte zuerst einloggen.")
    st.stop()

def load_icon_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

img_rbb = load_icon_base64("assets/red-blood-cells.png")
img_neutro = load_icon_base64("assets/neutrophil.png")
img_lympho = load_icon_base64("assets/lymphocyte.png")
img_platelet = load_icon_base64("assets/platelet.png")
img_title = load_icon_base64("assets/blood-count.png")
img_blood = load_icon_base64("assets/blood.png")

titel_key = "haema_titel"
fach = "Hämatologie"  # oder falls du `query_params` nutzen willst: auslesen wie früher

st.markdown(f"""
<h1 style='display: flex; align-items: center; gap: 24px;'>
    Zellzählung {fach}
    <img src='data:image/png;base64,{img_blood}' width='50'>
</h1>
""", unsafe_allow_html=True)

zelltypen = [
    "Blasten", "Promyelozyten", "Myelozyten", "Metamyelozyten",
    "Stabkernige Granulozyten", "Segmentkernige Granulozyten",
    "Eosinophile", "Basophile", "Monozyten", "Lymphozyten", "Plasmazellen",
    "Erythroblasten", "Unbekannt / Diverses"
]

rb_felder = [
    "Anisozytose", "Mikrozyten", "Makrozyten", "Anisochromasie",
    "Hypochrom", "Hyperchrom", "Polychromasie", "Poikilozytose",
    "Ovalozyten", "Akanthozyten", "Sphärozyten", "Stomatozyten",
    "Echinozyten", "Targetzellen", "Tränenformen", "Sichelzellen",
    "Fragmentozyten", "Baso. Punktierung", "Howell Jollies", "Pappenheim",
]

gb_felder = [
    "vergröberte Granula", "basophile Schlieren",
    "Zytoplasmavakuolen", "Fehlende Granula", "Kernpyknose", "Pseudopelger",
    "Linksverschiebung", "Kerne hoch-/übersegmentiert"
]

ly_felder = [">10% LGL", "reaktiv", "pathologisch", "lymphoplasmozytoid"]

th_felder = ["Grosse Formen", "Riesenformen", "Agranulär"]

username = st.session_state.get("username", "anonymous")
dateipfad = f"data/data_haematologie_{username}.csv"
os.makedirs(os.path.dirname(dateipfad), exist_ok=True)

st.text_input("🧾 Titel des Eintrags", key=titel_key)

st.markdown("""
<style>
.zell-header {
    font-weight: bold;
    background-color: #f2f2f2;
    padding: 6px;
    border: 1px solid #ccc;
    text-align: center;
}
.zell-row {
    border-bottom: 1px solid #eee;
    padding: 8px 0;
}
.zell-cell {
    padding: 4px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Header manuell
st.markdown("""
<div class="zell-row">
    <div class="zell-cell" style="display: inline-block; width: 20%;"><div class="zell-header">Zelltyp</div></div>
    <div class="zell-cell" style="display: inline-block; width: 30%;"><div class="zell-header">Zählung 1</div></div>
    <div class="zell-cell" style="display: inline-block; width: 30%;"><div class="zell-header">Zählung 2</div></div>
    <div class="zell-cell" style="display: inline-block; width: 15%;"><div class="zell-header">Durchschnitt</div></div>
</div>
""", unsafe_allow_html=True)

for zelltyp in zelltypen:
    z1_key = f"{zelltyp}_z1"
    z2_key = f"{zelltyp}_z2"

    if z1_key not in st.session_state:
        st.session_state[z1_key] = 0
    if z2_key not in st.session_state:
        st.session_state[z2_key] = 0

    col1, col2, col3, col4 = st.columns([2, 3, 3, 2])

    with col1:
        st.markdown(f"**{zelltyp}**")

    with col2:
        c1, c2, c3 = st.columns([1, 1, 1])
        current_val_z1 = st.session_state[z1_key]
        if c1.button("➖", key=f"sub_{zelltyp}_z1"):
            current_val_z1 = max(0, current_val_z1 - 1)
        if c3.button("➕", key=f"add_{zelltyp}_z1"):
            current_val_z1 += 1
        st.session_state[z1_key] = current_val_z1
        c2.markdown(
            f"<div style='text-align: center; padding-top: 8px;'>{current_val_z1}</div>",
            unsafe_allow_html=True
        )

    with col3:
        c4, c5, c6 = st.columns([1, 1, 1])
        current_val_z2 = st.session_state[z2_key]
        if c4.button("➖", key=f"sub_{zelltyp}_z2"):
            current_val_z2 = max(0, current_val_z2 - 1)
        if c6.button("➕", key=f"add_{zelltyp}_z2"):
            current_val_z2 += 1
        st.session_state[z2_key] = current_val_z2
        c5.markdown(
            f"<div style='text-align: center; padding-top: 8px;'>{current_val_z2}</div>",
            unsafe_allow_html=True
        )

    with col4:
        avg = (st.session_state[z1_key] + st.session_state[z2_key]) / 2
        st.markdown(f"**{avg:.1f}**")

st.markdown("---")

# Untere Zusatzbereiche
st.markdown(f"""
<h3 style='display: flex; align-items: center; gap: 10px;'>
    Rotes Blutbild
    <img src='data:image/png;base64,{img_rbb}' width='30'>
</h3>
""", unsafe_allow_html=True)

rb_felder = [
    "Anisozytose", "Mikrozyten", "Makrozyten", "Anisochromasie",
    "Hypochrom", "Hyperchrom", "Polychromasie", "Poikilozytose",
    "Ovalozyten", "Akanthozyten", "Sphärozyten", "Stomatozyten",
    "Echinozyten", "Targetzellen", "Tränenformen", "Sichelzellen",
    "Fragmentozyten", "Baso. Punktierung", "Howell Jollies", "Pappenheim",
]
for feld in rb_felder:
    st.selectbox(feld, ["-", "+", "++", "+++"] , key=f"rb_{feld}")
st.text_area("Sonstiges:", key="rb_sonstiges", height=80)

st.markdown(f"""
<h3 style='display: flex; align-items: center; gap: 10px;'>
    Neutrophile Granulozyten
    <img src='data:image/png;base64,{img_neutro}' width='30'>
</h3>
""", unsafe_allow_html=True)

gb_felder = [
    "vergröberte Granula", "basophile Schlieren",
    "Zytoplasmavakuolen", "Fehlende Granula", "Kernpyknose", "Pseudopelger",
    "Linksverschiebung", "Kerne hoch-/übersegmentiert"
]
for feld in gb_felder:
    st.selectbox(feld, ["-", "+", "++", "+++"] , key=f"gb_{feld}")
st.text_area("Sonstiges:", key="ng_sonstiges", height=80)

st.markdown(f"""
<h3 style='display: flex; align-items: center; gap: 10px;'>
    Lymphozytenveränderungen
    <img src='data:image/png;base64,{img_lympho}' width='30'>
</h3>
""", unsafe_allow_html=True)

ly_felder = [">10% LGL", "reaktiv", "pathologisch", "lymphoplasmozytoid"]
for feld in ly_felder:
    st.selectbox(feld, ["-", "+", "++", "+++"] , key=f"ly_{feld}")
st.text_area("Sonstiges:", key="lc_sonstiges", height=80)

st.markdown(f"""
<h3 style='display: flex; align-items: center; gap: 10px;'>
    Thrombozyten
    <img src='data:image/png;base64,{img_platelet}' width='30'>
</h3>
""", unsafe_allow_html=True)

th_felder = ["Grosse Formen", "Riesenformen", "Agranulär"]
for feld in th_felder:
    st.selectbox(feld, ["-", "+", "++", "+++"] , key=f"th_{feld}")
st.text_area("Sonstiges:", key="th_sonstiges", height=80)

fehlende = []

# Kontrolle: leere Felder (""), "-" ist erlaubt!
for feld in rb_felder:
    if st.session_state.get(f"rb_{feld}", "") == "":
        fehlende.append(f"Rotes Blutbild: {feld}")
for feld in gb_felder:
    if st.session_state.get(f"gb_{feld}", "") == "":
        fehlende.append(f"Granulozyten: {feld}")
for feld in ly_felder:
    if st.session_state.get(f"ly_{feld}", "") == "":
        fehlende.append(f"Lymphozyten: {feld}")
for feld in th_felder:
    if st.session_state.get(f"th_{feld}", "") == "":
        fehlende.append(f"Thrombozyten: {feld}")

if fehlende:
    st.error("❌ Bitte alle Felder ausfüllen:")
    for f in fehlende:
        st.markdown(f"- {f}")
    st.stop()

# ===== Bild-Upload vor dem Speichern =====
st.markdown("### 📷 Mikroskopiebilder oder Befundfotos hochladen")
uploaded_images = st.file_uploader("Wähle ein oder mehrere Bilder", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
temp_uploaded_images = []
if not dh_img.filesystem.exists(dh_img.root_path):
    dh_img.filesystem.makedirs(dh_img.root_path)

bestehende_bilder = [f["name"] for f in dh_img.filesystem.ls(dh_img.root_path)]

if uploaded_images:
    st.markdown("**Vorschau:**")
    for img in uploaded_images:
        st.image(img, use_container_width=True)
        name_clean = img.name.replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        if name_clean in bestehende_bilder:
            st.info(f"⏭️ Bild bereits vorhanden: {name_clean}")
        else:
            temp_uploaded_images.append((name_clean, img.getvalue()))

# ==== Datei-Upload (PDF/Word) ====            
st.markdown("### 📎 Weitere Dateien anhängen (z. B. PDF, Word)")
uploaded_docs = st.file_uploader("Dateien auswählen", type=["pdf", "docx"], accept_multiple_files=True)
temp_uploads = []
if not dh_docs.filesystem.exists(dh_docs.root_path):
    dh_docs.filesystem.makedirs(dh_docs.root_path)
bestehende_dateien = [f["name"] for f in dh_docs.filesystem.ls(dh_docs.root_path)]
if uploaded_docs:
    for file in uploaded_docs:
        name_clean = file.name.replace(" ", "_")
        if name_clean in bestehende_dateien:
            st.info(f"⏭️ Datei bereits vorhanden: {name_clean}")
        else:
            temp_uploads.append((name_clean, file.getvalue()))

# === SPEICHERN & EXPORT VORBEREITUNG ===
if st.button("💾 Speichern und Exportieren"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    anhang_dateien = []

    # Bilder speichern
    for name, img_bytes in temp_uploaded_images:
        unique = uuid.uuid4().hex[:8]
        filename = f"{timestamp}_{unique}_{name}"
        dh_img.save(filename, img_bytes)

    # Anhänge speichern
    for name, content in temp_uploads:
        unique = uuid.uuid4().hex[:8]
        filename = f"{timestamp}_{unique}_{name}"
        dh_docs.save(filename, content)
        anhang_dateien.append(filename)

    eintrag = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "titel": st.session_state.get(titel_key, ""),
        "zellwerte": {zt: {
            "z1": st.session_state.get(f"{zt}_z1", 0),
            "z2": st.session_state.get(f"{zt}_z2", 0),
            "avg": (st.session_state.get(f"{zt}_z1", 0) + st.session_state.get(f"{zt}_z2", 0)) / 2
        } for zt in zelltypen},
        "notizen": {
            "rbb": st.session_state.get("rb_sonstiges", ""),
            "granulo": st.session_state.get("ng_sonstiges", ""),
            "lympho": st.session_state.get("lc_sonstiges", ""),
            "thrombo": st.session_state.get("th_sonstiges", "")
        },
        "rbb": {feld: st.session_state.get(f"rb_{feld}", "") for feld in rb_felder},
        "granulo": {feld: st.session_state.get(f"gb_{feld}", "") for feld in gb_felder},
        "lympho": {feld: st.session_state.get(f"ly_{feld}", "") for feld in ly_felder},
        "thrombo": {feld: st.session_state.get(f"th_{feld}", "") for feld in th_felder},
    }

    # Speichern in SWITCHdrive
    data_manager.append_record("haematologie_df", eintrag)

    # === WORD erstellen ===
    doc = Document()
    doc.add_heading(f"Zellzählung: {eintrag['titel']}", 0)

    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Zelltyp'
    hdr_cells[1].text = 'Zählung 1'
    hdr_cells[2].text = 'Zählung 2'
    hdr_cells[3].text = 'Ø Durchschnitt'

    for zt, werte in eintrag["zellwerte"].items():
        row_cells = table.add_row().cells
        row_cells[0].text = zt
        row_cells[1].text = str(werte['z1'])
        row_cells[2].text = str(werte['z2'])
        row_cells[3].text = f"{werte['avg']:.1f}"

    def add_section(doc, title, felder_dict, sonst_text):
        doc.add_heading(title, level=2)
        for k in felder_dict:
            v = felder_dict[k]
            doc.add_paragraph(f"{k}: {v if v != '' else '-'}", style="List Bullet")
        doc.add_paragraph("Sonstiges:", style="List Bullet")
        if sonst_text:
            for line in sonst_text.splitlines():
                doc.add_paragraph(line.strip(), style="Normal")
        else:
            doc.add_paragraph("-", style="Normal")

    add_section(doc, "Rotes Blutbild", eintrag["rbb"], eintrag["notizen"]["rbb"])
    add_section(doc, "Neutrophile Granulozyten", eintrag["granulo"], eintrag["notizen"]["granulo"])
    add_section(doc, "Lymphozytenveränderungen", eintrag["lympho"], eintrag["notizen"]["lympho"])
    add_section(doc, "Thrombozyten", eintrag["thrombo"], eintrag["notizen"]["thrombo"])
 
# 📷 Bilder ins Word-Dokument einfügen
    if uploaded_images:
        doc.add_page_break()
        doc.add_heading("Mikroskopiebilder / Befundfotos", level=2)
        for img in uploaded_images:
            # Temporäre Datei anlegen
            try:
                image_pil = Image.open(img)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    image_pil.save(tmp_img.name)
                    doc.add_picture(tmp_img.name, width=Inches(4.5))
            except Exception as e:
                st.warning(f"⚠️ Bild konnte nicht eingefügt werden: {img.name} ({e})")

    # === Word speichern in Puffer
    buffer_word = io.BytesIO()
    doc.save(buffer_word)
    buffer_word.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    x, y = 2 * cm, height - 2 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, f"Zellzählung: {eintrag['titel']}")
    y -= 1.5 * cm

    c.setFont("Helvetica", 12)
    c.drawString(x, y, "Zellwerte:")
    y -= 1 * cm

    for zt, werte in eintrag["zellwerte"].items():
        line = f"{zt}: Z1 = {werte['z1']}, Z2 = {werte['z2']}, Ø = {werte['avg']:.1f}"
        c.drawString(x, y, line)
        y -= 0.6 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm

    c.save()
    pdf_buffer.seek(0)

    pdf_name = f"{timestamp}_Haematologie.pdf"
    dh_docs.save(pdf_name, pdf_buffer.getvalue())
    anhang_dateien.append(pdf_name)

    neuer_eintrag = {
        "id": f"HAE_{timestamp}",
        "titel": eintrag["titel"],
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "anhaenge": anhang_dateien
    }

    if os.path.exists(dateipfad):
        df = pd.read_csv(dateipfad)
        df = pd.concat([df, pd.DataFrame([neuer_eintrag])], ignore_index=True)
    else:
        df = pd.DataFrame([neuer_eintrag])
    df.to_csv(dateipfad, index=False)

    # Speichern in SWITCHdrive
    username = st.session_state.get("username", "anonymous")
    word_ordner = "word_haematologie"
    user_folder = os.path.join(word_ordner, username)
    os.makedirs(user_folder, exist_ok=True)

    dh = data_manager._get_data_handler(f"{word_ordner}/{username}")
    titel = st.session_state.get(titel_key, "")

    # === Erfolgsmeldung + Downloadbuttons
    st.success("✅ Eintrag gespeichert!")

    st.download_button("⬇️ Word herunterladen", buffer_word, file_name=f"{timestamp}_{titel.replace(' ', '-')}.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.download_button("⬇️ PDF herunterladen", pdf_buffer, file_name=f"{timestamp}_{titel.replace(' ', '-')}.pdf",
                       mime="application/pdf")

# === GANZ UNTEN: Zurück-Button ===
st.markdown("---")
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
