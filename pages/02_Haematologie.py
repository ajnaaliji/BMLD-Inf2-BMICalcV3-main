import streamlit as st
import math
import base64
import ast
import os
import pandas as pd

st.set_page_config(page_title="Blutbilddifferenzierung", page_icon="🩸")

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

from utils.data_manager import DataManager
import pandas as pd

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

data_manager = DataManager()

# WICHTIG: Direkt reload erzwingen
data_manager.load_user_data("haematologie_df", "haematologie.csv", initial_value=pd.DataFrame())

import ast  # Falls noch nicht ganz oben eingefügt

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

import io
import os
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile

# === ZUERST: Word speichern und exportieren ===
if st.button("📝 Eintrag speichern und als Word exportieren"):
    timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")

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

    # Word-Dokument erstellen
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

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # Word-Download
    st.download_button(
        label="⬇️ Word-Dokument herunterladen",
        data=buffer,
        file_name=f"{timestamp}_{eintrag['titel'].replace(' ', '-')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Word-Speicherung
    save_path = os.path.join("data/word_haematologie", f"{timestamp}_{eintrag['titel'].replace(' ', '-')}.docx")
    with open(save_path, "wb") as out_file:
        out_file.write(buffer.getvalue())

    st.success("✅ Eintrag gespeichert und Word-Datei exportiert!")

# === DANN: PDF exportieren ===
if st.button("📄 Als PDF exportieren"):
    eintrag = {
        "titel": st.session_state.get(titel_key, ""),
        "zellwerte": {zt: {
            "z1": st.session_state.get(f"{zt}_z1", 0),
            "z2": st.session_state.get(f"{zt}_z2", 0),
            "avg": (st.session_state.get(f"{zt}_z1", 0) + st.session_state.get(f"{zt}_z2", 0)) / 2
        } for zt in zelltypen},
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        c = canvas.Canvas(tmp.name, pagesize=A4)
        width, height = A4
        x = 2 * cm
        y = height - 2 * cm

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

        with open(tmp.name, "rb") as f:
            st.download_button(
                label="⬇️ PDF herunterladen",
                data=f.read(),
                file_name=f"{eintrag['titel']}_Zellzaehlung.pdf",
                mime="application/pdf"
            )

# === GANZ UNTEN: Zurück-Button ===
st.markdown("---")
if st.button("🔙 Zurück zur Übersicht"):
    st.switch_page("pages/01_Datei.py")
