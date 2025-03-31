import streamlit as st

# Cette ligne doit être la première commande Streamlit
st.set_page_config(page_title="ESCP AI Champions - Prompt", layout="wide")

# Ensuite, importez les autres modules
from PIL import Image
from utils.images_generator import generate_image_openai
from Accueil import pseudo_dialog

import db_manager as db

# Activez le mode DEBUG si nécessaire
from utils.images_generator import DEBUG
# DEBUG = True  # Décommentez cette ligne pour activer le débogage

# st.image(
#     Image.open("static/Gaumont_logo.svg.png"),
#     width=400,
# )

st.sidebar.image(
    Image.open("static/ESCP_LOGO_CMJN.png"),
    width=150,
)

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()
    st.rerun()

st.session_state["selected_session_db"] = db.get_selected_session()

if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

if "img_url" not in st.session_state:
    st.session_state["img_url"] = ""


if st.button("Reload"):
    st.rerun()

if st.session_state["selected_session_db"] != "":
    session_name = st.session_state["selected_session_db"]
    url = db.get_img_ref_url(session_name)
    st.header(f"Reference Image: {session_name}")
    st.image(url)

    prompt = st.text_area("Enter your prompt", value=st.session_state["prompt"])
    
    # Options de génération avant le bouton "Generate!"
    st.header("Generation Options")
    col1, col2, col3 = st.columns(3)

    with col1:
        style = st.selectbox(
            "Style",
            options=["vivid", "natural"],
            help="'vivid' for hyper-realistic images, 'natural' for more natural-looking images"
        )

    with col2:
        quality = st.selectbox(
            "Quality",
            options=["standard", "hd"],
            help="'hd' for more detailed images (higher cost)"
        )

    with col3:
        size = st.selectbox(
            "Format",
            options=["1024x1024", "1792x1024", "1024x1792"],
            help="Square, landscape, or portrait format"
        )
    
    if st.button("Generate!"):
        st.session_state["prompt"] = prompt
        with st.spinner("Creating image..."):
            img_url = generate_image_openai(
                st.session_state["prompt"],
                style=style,
                quality=quality,
                size=size
            )
            if img_url:
                st.session_state["img_url"] = img_url
                db.add_image(
                    session_name,
                    st.session_state["pseudo"],
                    st.session_state["img_url"],
                    st.session_state["prompt"],
                )
            else:
                st.error("Image generation failed. Please try again.")

    if "img_url" in st.session_state and st.session_state["img_url"] is not None:
        st.header(f"Your image: {st.session_state['pseudo']}")
        if st.session_state["img_url"] != "":
            st.image(st.session_state["img_url"])
