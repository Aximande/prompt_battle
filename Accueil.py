import streamlit as st
from PIL import Image
import db_manager as db


st.set_page_config(page_title="Accueil")

# st.image(
#     Image.open("static/Gaumont_logo.svg.png"),
#     width=400,
# )

db.initialize_firebase()

st.title("Accueil")
st.write("Bienvenue sur notre application de démonstration !")

if "pseudo" not in st.session_state:
    st.session_state["pseudo"] = ""

if "selected_session" not in st.session_state:
    st.session_state["selected_session"] = ""

st.session_state["pseudo"] = st.text_input(
    "Quelle est votre pseudo ??", value=st.session_state["pseudo"]
)

# faire une page avec des tips et des aides
# gallerie avec toutes les miniatures + autres page avec carousel des images
# des rounds pour chaque generations

if st.session_state["pseudo"] == "lavaleexx":
    names = [""] + db.get_all_session_names()
    selected_session = st.selectbox(
        "available sessions",
        names,
        index=names.index(st.session_state["selected_session"]),
    )
    st.session_state["selected_session"] = selected_session

    db.select_session(selected_session)
