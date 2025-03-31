import streamlit as st
from PIL import Image
import db_manager as db
import os

def pseudo_dialog():
    if "pseudo_submitted" not in st.session_state:
        st.session_state["pseudo_submitted"] = False
    
    if not st.session_state["pseudo_submitted"]:
        with st.container():
            st.subheader("Enter your username")
            pseudo = st.text_input("What is your username?")
            if st.button("Submit"):
                st.session_state["pseudo"] = pseudo
                st.session_state["pseudo_submitted"] = True
                st.rerun()


st.set_page_config(page_title="ESCP AI Champions - Battle of Prompt", layout="wide")

db.initialize_firebase()

# Display ESCP AI Champions banner
st.image(
    Image.open("static/escp ai champions battle prompt banner.png"),
    width=None,  # Use None to maintain aspect ratio
)

# Display ESCP logo in sidebar
st.sidebar.image(
    Image.open("static/ESCP_LOGO_CMJN.png"),
    width=150,
)

st.title("ESCP AI Champions - Battle of Prompt")
st.write("Welcome to our AI image generation application!")
st.write("Create impressive images using OpenAI's DALL-E 3 API.")

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()

if "selected_session" not in st.session_state:
    st.session_state["selected_session"] = ""

# Event information
with st.expander("About the event"):
    st.write("""
    **ESCP AI Champions - Battle of Prompt** is an event organized by ESCP Business School 
    on Friday, April 4th, 2025. This event allows participants to compete in a creative 
    competition using artificial intelligence to generate images.
    
    Use your creativity and prompt engineering skills to create the most impressive 
    images and win the title of ESCP AI Champion!
    """)

if st.button("Change username"):
    st.session_state["pseudo_submitted"] = False
    st.rerun()

st.page_link("pages/01_Prompt.py", label="Go to Prompt Page", icon="🎨")
st.page_link("pages/02_Galerie.py", label="View Gallery", icon="🖼️")

# Admin code
if "pseudo" in st.session_state and st.session_state["pseudo"] == "lavaleexx":
    st.divider()
    st.subheader("Administration")
    names = [""] + db.get_all_session_names()
    selected_session = st.selectbox(
        "Available sessions",
        names,
        index=names.index(st.session_state["selected_session"]),
    )
    st.session_state["selected_session"] = selected_session

    db.select_session(selected_session)

# Footer
st.markdown("""
---
<div style="text-align: center; color: gray; font-size: 0.8em;">
ESCP AI Champions - Battle of Prompt | April 4th, 2025 | ESCP Business School
</div>
""", unsafe_allow_html=True)
