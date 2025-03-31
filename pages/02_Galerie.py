import streamlit as st

# Cette ligne doit être la première commande Streamlit
st.set_page_config(page_title="ESCP AI Champions - Gallery", layout="wide")

from PIL import Image
from streamlit_carousel import carousel
import db_manager as db
import math
from utils.session_utils import pseudo_dialog  # Importer depuis le nouveau module

db.initialize_firebase()

st.sidebar.image(
    Image.open("static/ESCP_LOGO_CMJN.png"),
    width=150,
)

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    pseudo_dialog()


if st.sidebar.button("Reload"):
    st.rerun()

session_name = db.get_selected_session()
st.session_state["selected_session"] = session_name
if session_name != "":
    items = db.get_all_images_for_session(session_name)

    # Add filters to the gallery
    style_filter = st.sidebar.multiselect(
        "Filter by style",
        options=["vivid", "natural", "all"],
        default=["all"]
    )

    format_filter = st.sidebar.multiselect(
        "Filter by format",
        options=["1024x1024", "1792x1024", "1024x1792", "all"],
        default=["all"]
    )

    # Filter items based on selections
    filtered_items = items
    if "all" not in style_filter and style_filter:
        filtered_items = [item for item in filtered_items if item.get("style") in style_filter]
    if "all" not in format_filter and format_filter:
        filtered_items = [item for item in filtered_items if item.get("size") in format_filter]

    if st.sidebar.toggle("Carousel"):
        col_ref, col_car = st.columns([2, 5])
        with col_ref:
            url = db.get_img_ref_url(session_name)
            st.image(url)
        with col_car:
            # Ensure items are in the correct format
            carousel_items = []
            for item in filtered_items:
                # Make sure each item has the correct format for the carousel
                carousel_item = {
                    "title": item.get("title", ""),
                    "text": item.get("prompt", ""),
                    "img": item.get("img", "")
                }
                carousel_items.append(carousel_item)
            
            # Display carousel only if there are items
            if carousel_items:
                try:
                    st.write("Element structure:")
                    st.write(filtered_items[0] if filtered_items else "No elements")  # Display the first element to see its structure
                    carousel(items=carousel_items, width=0.9, container_height=900, pause="hover")
                except Exception as e:
                    st.error(f"Error displaying carousel: {e}")
                    # Display images in grid mode as an alternative
                    for item in carousel_items:
                        st.image(item["img"])
                        st.write(item["title"])
            else:
                st.warning("No images to display in the carousel.")
    else:
        elem_count = len(filtered_items)
        col_count = 4  # math.ceil(elem_count / 4)
        cols = [0] * col_count
        cols[0], cols[1], cols[2], cols[3] = st.columns(col_count)

        for i, item in enumerate(filtered_items):
            with cols[i % col_count]:
                st.image(item["img"])
                st.write(item["title"])

if "pseudo" in st.session_state and st.session_state["pseudo"] == "alex_lav":
    names = [""] + db.get_all_session_names()
    selected_session = st.sidebar.selectbox(
        "Available sessions",
        names,
        index=names.index(st.session_state["selected_session"]),
    )
    if selected_session != st.session_state["selected_session"]:
        st.session_state["selected_session"] = selected_session

        db.select_session(selected_session)
        st.rerun()

    if st.sidebar.button("Restart session"):
        db.clear_session(session_name)
        st.rerun()
