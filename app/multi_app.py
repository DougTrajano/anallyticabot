import logging
import streamlit as st
from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from app.helper_functions import check_watson


class MultiApp:
    """Framework for combining multiple streamlit applications.
    Usage:
        def foo():
            st.title("Hello Foo")
        def bar():
            st.title("Hello Bar")
        app = MultiApp()
        app.add_app("Foo", foo)
        app.add_app("Bar", bar)
        app.run()
    It is also possible keep each application in a separate file.
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """

    def __init__(self):

        logging.info({"message": "Instantiate MultiApp object."})

        self.apps = []

    def add_app(self, title, func, logged_page=False):
        """Adds a new application.
        Parameters
        ----------
        title:
            title of the app. Appears in the dropdown in the sidebar.
        func:
            the python function to render this app.

        """

        logging.info({"message": "Adding page to app.",
                      "title": title, "logged_page": logged_page})

        self.apps.append({
            "title": title,
            "function": func,
            "logged_page": logged_page
        })

    def run(self, parameters=None):

        logging.info({"message": "Starting MultiApp."})

        state = _get_state()

        if isinstance(parameters, dict):
            st.set_page_config(page_title=parameters.get("page_title"), layout="wide",
                               page_icon=parameters.get("page_icon"))

            if parameters["disable_streamlit_menu"] == True:
                self.disable_menu()

            for key in parameters.keys():
                state[key] = parameters[key]

        st.sidebar.image("images/anallyticabot_logo.png",
                         use_column_width=True)
        st.sidebar.markdown(
            '<img src="https://i.ibb.co/yqsMMdm/with-watson.png" style="{ width: 100px; margin-left: auto; margin-right: auto; display: block; text-align: center; }" alt="With Watson">', unsafe_allow_html=True)

        if check_watson(state) == False:
            self.apps = [app for app in self.apps if app["logged_page"] != True]

        app = st.sidebar.radio(
            ' ',
            self.apps,
            format_func=lambda app: app['title'])

        if st.sidebar.button("Clear session"):
            state.clear()

        app['function'](state)

        state.sync()

    def disable_menu(self):
        logging.info({"message": "Disabling Streamlit's menu."})
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>

        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)


class _SessionState:
    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(
            self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state
