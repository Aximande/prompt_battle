import streamlit as st
from PIL import Image
import db_manager as db


@st.experimental_dialog("pseudo")
def pseudo_dialog():
    st.session_state["pseudo"] = st.text_input("Quelle est votre pseudo ??")
    st.rerun()


st.set_page_config(page_title="Accueil")

db.initialize_firebase()


# col_logo_0, col_logo_1 = st.columns(2)
# with col_logo_0:
#     st.image(
#         Image.open("static/ekko.png"),
#         width=300,
#     )
# with col_logo_1:
st.sidebar.image(
    Image.open("static/cerclevoyage.png"),
    width=80,
)
st.image(
    Image.open("static/cerclevoyagebandeau.png"),
    width=450,
)

st.title("Accueil")
st.write("Bienvenue sur notre application de démonstration !")

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()

if "selected_session" not in st.session_state:
    st.session_state["selected_session"] = ""


# faire une page avec des tips et des aides
# galerie avec toutes les miniatures + autres page avec carousel des images
# des rounds pour chaque generations
if st.button("Changer de pseudo"):
    pseudo_dialog()

st.page_link("pages/01_Prompt.py", label="Continuer vers la page de Prompt")

# if st.session_state["pseudo"] == "lavaleexx":
#     names = [""] + db.get_all_session_names()
#     selected_session = st.selectbox(
#         "available sessions",
#         names,
#         index=names.index(st.session_state["selected_session"]),
#     )
#     st.session_state["selected_session"] = selected_session

#     db.select_session(selected_session)
