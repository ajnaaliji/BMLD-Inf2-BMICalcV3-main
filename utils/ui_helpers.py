import streamlit as st

def apply_theme():
    theme = st.session_state.get("theme", "light")
    if theme == "dark":
        st.markdown("""
            <style>
                .stApp { background-color: #1e1e1e; color: white; }
                .fachkarte { background-color: #333; color: white; }
                .stButton>button { background-color: #444; color: white; }
                .stRadio > div { background-color: transparent !important; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .stApp { background: linear-gradient(to bottom, #eaf2f8, #f5f9fc); color: black; }
                .fachkarte { background-color: white; color: black; }
                .stRadio > div { background-color: transparent !important; }
            </style>
        """, unsafe_allow_html=True)
