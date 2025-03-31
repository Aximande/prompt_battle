import streamlit as st
from datetime import datetime

# This line must be the first Streamlit command
st.set_page_config(page_title="ESCP AI Champions - Prompt", layout="wide")

# Then import other modules
from PIL import Image
from utils.images_generator import generate_image_openai, check_firebase_initialization
from utils.session_utils import pseudo_dialog

import db_manager as db

# Check Firebase initialization
check_firebase_initialization()

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    st.warning("Please set your username on the home page first.")
    st.stop()

st.session_state["selected_session_db"] = db.get_selected_session()

# Initialize image history if needed
if "image_history" not in st.session_state:
    st.session_state["image_history"] = []

if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

if "img_url" not in st.session_state:
    st.session_state["img_url"] = ""

# Sidebar with logo and controls
st.sidebar.image(
    Image.open("static/ESCP_LOGO_CMJN.png"),
    width=150,
)

# Button to clear history
if st.sidebar.button("Clear History"):
    st.session_state["image_history"] = []
    st.rerun()

# Button to reload the page
if st.sidebar.button("Reload"):
    st.rerun()

# Main content
if st.session_state["selected_session_db"] != "":
    session_name = st.session_state["selected_session_db"]
    url = db.get_img_ref_url(session_name)
    
    if url:
        st.header(f"Reference Image: {session_name}")
        st.image(url)
    else:
        st.warning(f"No reference image found for session: {session_name}")

    # Prompt input area
    prompt = st.text_area("Enter your prompt", value=st.session_state["prompt"])
    
    # Generation options before the "Generate!" button
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
    
    # Generation button
    if st.button("Generate Image"):
        st.session_state["prompt"] = prompt
        with st.spinner("Creating image..."):
            temp_url, permanent_url = generate_image_openai(
                st.session_state["prompt"],
                style=style,
                quality=quality,
                size=size,
                author=st.session_state["pseudo"]
            )
            if temp_url and permanent_url:
                # Add image to history
                st.session_state["image_history"].append({
                    "temp_url": temp_url,
                    "permanent_url": permanent_url,
                    "prompt": st.session_state["prompt"],
                    "style": style,
                    "size": size,
                    "timestamp": datetime.now().isoformat(),
                    "submitted": False  # Indicates if the image has been submitted to the gallery
                })
                st.session_state["img_url"] = permanent_url
                st.rerun()  # Reload to display updated history
            else:
                st.error("Image generation failed. Please try again.")

    # Display generated image history
    if st.session_state["image_history"]:
        st.header("Your Generation History")
        st.write("Select the image you want to submit to the main gallery.")
        
        # Display images in a grid
        cols = st.columns(3)
        for i, img_data in enumerate(reversed(st.session_state["image_history"])):
            with cols[i % 3]:
                st.image(img_data["permanent_url"])
                st.write(f"Prompt: {img_data['prompt'][:50]}...")
                
                # Button to submit to gallery
                if not img_data["submitted"]:
                    if st.button(f"Submit to Gallery", key=f"submit_{i}"):
                        # Add image to main gallery with replacement option
                        success = db.add_image(
                            session_name,
                            st.session_state["pseudo"],
                            img_data["temp_url"],
                            img_data["permanent_url"],
                            img_data["prompt"],
                            style=img_data["style"],
                            size=img_data["size"],
                            check_duplicate=False  # Disable duplicate checking to allow replacement
                        )
                        
                        if success:
                            # Mark as submitted
                            st.session_state["image_history"][len(st.session_state["image_history"]) - 1 - i]["submitted"] = True
                            st.success("Image successfully submitted to the gallery!")
                            # Force page reload to see changes
                            st.rerun()
                        else:
                            st.error("Error submitting image to gallery.")
                else:
                    st.write("✅ Submitted to gallery")
    
    # Display current image (last generated)
    if "img_url" in st.session_state and st.session_state["img_url"] is not None and st.session_state["img_url"] != "":
        st.header(f"Your latest image: {st.session_state['pseudo']}")
        st.image(st.session_state["img_url"], use_container_width=True)
else:
    st.warning("No session selected. Please choose a session on the home page.")
