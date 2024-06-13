import streamlit as st
from PIL import Image
from streamlit_carousel import carousel
import db_manager as db
import math
from Accueil import pseudo_dialog

st.set_page_config(page_title="Galerie", layout="wide")

db.initialize_firebase()

#st.sidebar.image(
#    Image.open("static/cerclevoyage.png"),
#    width=80,
#)

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()


if st.sidebar.button("Recharger"):
    st.rerun()

session_name = db.get_selected_session()
st.session_state["selected_session"] = session_name
if session_name != "":
    items = db.get_all_images_for_session(session_name)
    # items = items + items + items

    if st.sidebar.toggle("Carrousel"):
        col_ref, col_car = st.columns([2, 5])
        with col_ref:
            url = db.get_img_ref_url(session_name)
            st.image(url)
        with col_car:
            carousel(items=items, width=0.9, container_height=900, pause="hover")
    else:
        elem_count = len(items)
        col_count = 4  # math.ceil(elem_count / 4)
        cols = [0] * col_count
        cols[0], cols[1], cols[2], cols[3] = st.columns(col_count)

        for i, item in enumerate(items):
            with cols[i % col_count]:
                st.image(item["img"])
                st.write(item["title"])

if st.session_state["pseudo"] == "lavaleexx":
    names = [""] + db.get_all_session_names()
    selected_session = st.sidebar.selectbox(
        "available sessions",
        names,
        index=names.index(st.session_state["selected_session"]),
    )
    if selected_session != st.session_state["selected_session"]:
        st.session_state["selected_session"] = selected_session

        db.select_session(selected_session)
        st.rerun()

    if st.sidebar.button("Redemarrer la session"):
        db.clear_session(session_name)
        st.rerun()
