import streamlit as st
from PIL import Image
from utils.images_generator import generate_image_openai
from Accueil import pseudo_dialog

import db_manager as db

# st.image(
#     Image.open("static/Gaumont_logo.svg.png"),
#     width=400,
# )

st.set_page_config(page_title="Prompt")

db.initialize_firebase()

#st.sidebar.image(
#    Image.open("static/cerclevoyage.png"),
#    width=80,
#)

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()

st.session_state["selected_session_db"] = db.get_selected_session()

if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

if "img_url" not in st.session_state:
    st.session_state["img_url"] = ""


if st.button("Recharger"):
    st.rerun()

if st.session_state["selected_session_db"] != "":
    session_name = st.session_state["selected_session_db"]
    url = db.get_img_ref_url(session_name)
    st.header(f"Image reference: {session_name}")
    st.image(url)

    prompt = st.text_area("Entrez votre prompt", value=st.session_state["prompt"])
    if st.button("Generer !"):
        st.session_state["prompt"] = prompt
        with st.spinner("Creation de l'image..."):
            st.session_state["img_url"] = generate_image_openai(
                st.session_state["prompt"]
            )
            db.add_image(
                session_name,
                st.session_state["pseudo"],
                st.session_state["img_url"],
                st.session_state["prompt"],
            )
    if "img_url" in st.session_state and st.session_state["img_url"] is not None:
        st.header(f"Votre image : {st.session_state['pseudo']}")
        if st.session_state["img_url"] != "":
            st.image(st.session_state["img_url"])
