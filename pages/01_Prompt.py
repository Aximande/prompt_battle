import streamlit as st
from PIL import Image
from utils.images_generator import generate_image_openai

import db_manager as db

# st.image(
#     Image.open("static/Gaumont_logo.svg.png"),
#     width=400,
# )

st.set_page_config(page_title="Prompt")

st.session_state["selected_session_db"] = db.get_selected_session()

if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

if "img_url" not in st.session_state:
    st.session_state["img_url"] = ""


# Afficher les mises à jour dans Streamlit
selected_session_db = st.session_state["selected_session_db"]
if st.session_state["selected_session_db"] != "":
    session_name = st.session_state["selected_session_db"]
    url = db.get_img_ref_url(session_name)
    st.header(session_name)
    st.image(url)

    prompt = st.text_area("Entrez votre prompt", value=st.session_state["prompt"])
    if prompt != st.session_state["prompt"] and prompt != "":
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
        st.header("Votre image")
        st.image(st.session_state["img_url"], width=703)


# callback_done, doc_watch = db.get_selection_watch()

# # Boucle de mise à jour pour Streamlit
# try:
#     while True:
#         callback_done.wait(
#             timeout=60
#         )  # Vous pouvez ajuster le timeout selon vos besoins
#         callback_done.clear()  # Réinitialiser l'Event après avoir capturé le snapshot
#         if (
#             "selected_session_db" in st.session_state
#             and selected_session_db != st.session_state["selected_session_db"]
#         ):
#             st.rerun()


# except KeyboardInterrupt:
#     # Arrêter la surveillance proprement en cas d'interruption (Ctrl+C)
#     doc_watch.unsubscribe()
#     st.write("Stopped listening for changes.")
