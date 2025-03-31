import streamlit as st
import firebase_admin
from firebase_admin import storage

def delete_image(image_path):
    bucket = storage.bucket(name="prompt-battle-9b72d.appspot.com")
    blob = bucket.blob(image_path)
    blob.delete()
    st.success(f"Image {image_path} supprimée avec succès")

st.title("Modération des images")

if st.session_state.get("pseudo") != "lavaleexx":
    st.error("Accès non autorisé")
    st.stop()

# Lister toutes les images
bucket = storage.bucket(name="prompt-battle-9b72d.appspot.com")
blobs = list(bucket.list_blobs(prefix="images/"))

for blob in blobs:
    blob.reload()
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.image(blob.public_url, width=300)
        if blob.metadata:
            st.write(f"Auteur: {blob.metadata.get('author', 'Inconnu')}")
            st.write(f"Prompt: {blob.metadata.get('prompt', '')}")
    
    with col2:
        if st.button("Supprimer", key=blob.name):
            delete_image(blob.name)
            st.rerun() 