import streamlit as st
from utils.export import export_user_gallery
from datetime import datetime

st.title("Export My Gallery")

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    st.warning("Please set your username on the home page first.")
    st.stop()
else:
    username = st.session_state["pseudo"]
    
    # Display username
    st.write(f"User: **{username}**")
    
    if st.button("Generate HTML Export"):
        with st.spinner("Generating gallery..."):
            html_content = export_user_gallery(username)
            
            # Create download button
            current_date = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label="Download HTML Gallery",
                data=html_content,
                file_name=f"gallery_{username}_{current_date}.html",
                mime="text/html"
            )
            
            # Display preview
            st.subheader("Gallery Preview")
            st.components.v1.html(html_content, height=600, scrolling=True) 