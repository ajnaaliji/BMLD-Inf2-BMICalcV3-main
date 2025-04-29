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
                 auth_cookie_name: str = 'melinjaneu_app'):  # <- Cookie-Name angepasst
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

        try:
            with open("assets/labor.png", "rb") as f:
                image_data = f.read()
                self.img_html = f'<img src="data:image/png;base64,{base64.b64encode(image_data).decode("utf-8")}" width="32" style="vertical-align: middle;">'
        except Exception:
            self.img_html = ""

    def _load_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Registrieren'):
        login_tab, register_tab = st.tabs((login_title, register_title))
        with login_tab:
            st.markdown("<div class='header-text'>Herzlich willkommen in deinem</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='title-row'>Laborjournal {self.img_html}</div>", unsafe_allow_html=True)
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            self.login(stop=False)
            st.markdown('</div>', unsafe_allow_html=True)

        with register_tab:
            self.register()

    def login(self, stop=True):
        name, authentication_status, username = self.authenticator.login('Login', 'main')

        if authentication_status is True:
            st.session_state["name"] = name
            st.session_state["username"] = username
        elif authentication_status is False:
            st.error("Benutzername oder Passwort ist falsch.")
        elif authentication_status is None:
            st.warning("Bitte Benutzername und Passwort eingeben.")

        if stop:
            st.stop()

    def register(self, stop=True):
        st.subheader("Registrieren")

        try:
            with st.form("Registrierungsformular", clear_on_submit=True):
                new_username = st.text_input("Benutzername")
                new_firstname = st.text_input("Vorname")
                new_lastname = st.text_input("Nachname")
                new_email = st.text_input("E-Mail-Adresse")
                new_password = st.text_input("Passwort", type="password")
                submitted = st.form_submit_button("Registrieren")

                if submitted:
                    if not (new_username and new_firstname and new_lastname and new_email and new_password):
                        st.error("Bitte alle Felder ausfüllen.")
                    elif len(new_password) < 8:
                        st.error("Das Passwort muss mindestens 8 Zeichen lang sein.")
                    elif new_username in self.authenticator.credentials["usernames"]:
                        st.error("Benutzername existiert bereits.")
                    else:
                        hashed_password = stauth.Hasher([new_password]).generate()[0]
                        full_name = f"{new_firstname.strip()} {new_lastname.strip()}"
                        self.authenticator.credentials["usernames"][new_username] = {
                            "name": full_name,
                            "first_name": new_firstname.strip(),
                            "last_name": new_lastname.strip(),
                            "email": new_email,
                            "password": hashed_password
                        }

                        self._save_auth_credentials()
                        st.success(f"Benutzer {new_username} erfolgreich registriert.")
                        st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Registrierung: {e}")

        if stop:
            st.stop()

    def go_to_login(self, login_page_py_file):
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()
