import streamlit as st
from utils.image_search import search_images_by_author

st.title("My Image Gallery")

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    st.warning("Please set your username on the home page first.")
    st.stop()
else:
    user_images = search_images_by_author(st.session_state["pseudo"])
    
    if not user_images:
        st.info("You haven't generated any images yet")
    else:
        st.success(f"You have generated {len(user_images)} images")
        
        # Display images in a grid
        cols = st.columns(3)
        for i, img in enumerate(user_images):
            with cols[i % 3]:
                st.image(img['url'])
                st.caption(f"Created on: {img['created_at'][:10]}")
                st.write(img['prompt']) 