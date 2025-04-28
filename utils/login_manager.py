import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager
import base64

class LoginManager:
    """
    Singleton class that manages authentication, storage, and application state.
    """
    def __new__(cls, *args, **kwargs):
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        else:
            instance = super(LoginManager, cls).__new__(cls)
            st.session_state.login_manager = instance
            return instance

    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        if hasattr(self, 'authenticator'):
            return

        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key
        )

    def _load_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Registrieren'):
        """
        Renders login and registration interface with custom styling.
        """

        # CSS Styling
        st.markdown("""
            <style>
                .stApp {
                    background-color: #eaf2f8;
                }
                .header-text {
                    text-align: center;
                    font-size: 26px;
                    font-weight: bold;
                    margin-top: 40px;
                    margin-bottom: 0px;
                }
                .title-row {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    font-size: 36px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }
                .login-card {
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 450px;
                    margin: 0 auto;
                }
                [data-baseweb="tab-list"] {
                    border-bottom: none !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # Logo laden
        try:
            with open("assets/labor.png", "rb") as f:
                image_data = f.read()
                encoded_image = base64.b64encode(image_data).decode("utf-8")
                img_html = f'<img src="data:image/png;base64,{encoded_image}" width="32" style="vertical-align: middle;">'
        except Exception:
            img_html = ""

        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout")
            st.stop()

        login_tab, register_tab = st.tabs((login_title, register_title))

        with login_tab:
            st.markdown("<div class='header-text'>Herzlich willkommen in deinem</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='title-row'>Laborjournal {img_html}</div>", unsafe_allow_html=True)
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            self.login(stop=False)
            st.markdown('</div>', unsafe_allow_html=True)

        with register_tab:
            st.markdown("<div class='header-text'>Registriere dich für dein</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='title-row'>Laborjournal {img_html}</div>", unsafe_allow_html=True)
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            self.register(stop=False)
            st.markdown('</div>', unsafe_allow_html=True)

    def login(self, stop=True):
        """
        Renders login form and handles authentication.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout")
        else:
            self.authenticator.login('Login-Formular', location='main')
            if st.session_state.get("authentication_status") is False:
                st.error("Benutzername oder Passwort ist falsch.")
            elif st.session_state.get("authentication_status") is None:
                st.warning("Bitte Benutzername und Passwort eingeben.")
        if stop:
            st.stop()

    def register(self, stop=True):
        """
        Renders registration form and handles new user registration.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout")
        else:
            st.info("""
                Das Passwort muss 8–20 Zeichen lang sein und mindestens einen Großbuchstaben, 
                eine Zahl und ein Sonderzeichen @$!%*?& enthalten.
            """)
            res = self.authenticator.register_user('Registrierungs-Formular', preauthorization=False)
            if res:
                st.success("Benutzer erfolgreich registriert.")
                try:
                    self._save_auth_credentials()
                    st.success("Zugangsdaten gespeichert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Zugangsdaten: {e}")
        if stop:
            st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Forces logout and redirects to login page if necessary.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout("Logout")
