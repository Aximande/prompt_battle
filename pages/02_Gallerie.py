import streamlit as st
from PIL import Image
from streamlit_carousel import carousel
import db_manager as db

st.set_page_config(page_title="Gallerie", layout="wide")

session_name = db.get_selected_session()
test_items = db.get_all_images_for_session(session_name)

carousel(items=test_items, width=0.5, container_height=800, pause="hover")
