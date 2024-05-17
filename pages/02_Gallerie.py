import streamlit as st
from PIL import Image
from streamlit_carousel import carousel
import db_manager as db
import math
from Accueil import pseudo_dialog

st.set_page_config(page_title="Gallerie", layout="wide")

db.initialize_firebase()

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()


if st.sidebar.button("Recharger"):
    st.rerun()

session_name = db.get_selected_session()
if session_name != "":
    items = db.get_all_images_for_session(session_name)
    # items = items + items + items

    if st.sidebar.toggle("Carousel"):
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
