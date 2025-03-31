import streamlit as st
from utils.image_search import search_images_by_author, search_images_by_style

st.title("Image Search")

search_type = st.selectbox("Search by:", ["Author", "Style"])

if search_type == "Author":
    author = st.text_input("Author name:")
    if st.button("Search") and author:
        results = search_images_by_author(author)
        if results:
            st.success(f"{len(results)} images found")
            for img in results:
                st.image(img['url'])
                st.write(f"Prompt: {img['prompt']}")
                st.write(f"Date: {img['created_at']}")
        else:
            st.info("No images found for this author")
elif search_type == "Style":
    style = st.selectbox("Style:", ["vivid", "natural"])
    if st.button("Search"):
        results = search_images_by_style(style)
        if results:
            st.success(f"{len(results)} images found")
            for img in results:
                st.image(img['url'])
                st.write(f"Author: {img['author']}")
                st.write(f"Prompt: {img['prompt']}")
        else:
            st.info(f"No images found with style {style}") 