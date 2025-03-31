import streamlit as st
from datetime import datetime

# Cette ligne doit être la première commande Streamlit
st.set_page_config(page_title="ESCP AI Champions - Battle of Prompt", layout="wide")

from PIL import Image
import db_manager as db
import os
from utils.session_utils import pseudo_dialog  # Importer depuis le nouveau module

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

# Username selection in sidebar
st.sidebar.subheader("User Settings")
if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    with st.sidebar.form("username_form"):
        username = st.text_input("Enter your username:")
        submit_button = st.form_submit_button("Set Username")
        if submit_button and username:
            st.session_state["pseudo"] = username
            st.rerun()
else:
    st.sidebar.write(f"Current user: **{st.session_state['pseudo']}**")
    if st.sidebar.button("Change Username"):
        st.session_state["pseudo"] = ""
        st.rerun()

st.title("ESCP AI Champions - Prompt Battle")

st.write("""
## Welcome to the Prompt Battle!

In this competition, you'll create images using AI that match a reference image as closely as possible.
Other participants will vote for the best submissions, and the image with the most votes wins!

### How to participate:
1. Enter your username in the sidebar
2. Select a session from the list below
3. Go to the 'Prompt' page to generate your image
4. Submit your best creation to the gallery
5. Vote for other participants' images in the 'Gallery' page

Good luck!
""")

# Check if username is set before showing sessions
if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    st.warning("Please enter your username in the sidebar to continue.")
else:
    # Get all session names
    session_names = db.get_all_session_names()
    
    if session_names:
        # Différencier l'affichage pour l'administrateur et les utilisateurs normaux
        if st.session_state["pseudo"] == "alex_lav":
            # Code existant pour l'administrateur
            st.subheader("Available Sessions")
            
            # Create columns for active and completed sessions
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Active Sessions")
                active_sessions = []
                
                for session in session_names:
                    if not db.is_session_finalized(session):
                        active_sessions.append(session)
                        
                        # Create a card for each active session
                        with st.container():
                            st.write(f"**{session}**")
                            
                            # Get reference image
                            ref_url = db.get_img_ref_url(session)
                            if ref_url:
                                st.image(ref_url, width=300)
                            
                            # Button to select session
                            if st.button(f"Select {session}", key=f"select_{session}"):
                                db.select_session(session)
                                st.success(f"Selected session: {session}")
                                st.rerun()
                        
                        st.write("---")
                
                if not active_sessions:
                    st.info("No active sessions available.")
            
            with col2:
                st.write("### Completed Sessions")
                completed_sessions = []
                
                for session in session_names:
                    if db.is_session_finalized(session):
                        completed_sessions.append(session)
                        
                        # Create a card for each completed session
                        with st.container():
                            st.write(f"**{session}**")
                            
                            # Get reference image
                            ref_url = db.get_img_ref_url(session)
                            if ref_url:
                                st.image(ref_url, width=300)
                            
                            # Get winner information
                            db = db.firestore.client()
                            session_doc = db.collection("sessions").document(session).get()
                            
                            if session_doc.exists:
                                session_data = session_doc.to_dict()
                                winner = session_data.get("winner", "Unknown")
                                winner_votes = session_data.get("winner_votes", 0)
                                
                                st.write(f"🏆 Winner: **{winner}** with {winner_votes} votes")
                            
                            # Button to view results
                            if st.button(f"View Results", key=f"view_{session}"):
                                db.select_session(session)
                                st.success(f"Selected session: {session}")
                                st.rerun()
                        
                        st.write("---")
                
                if not completed_sessions:
                    st.info("No completed sessions available.")
        else:
            # Pour les utilisateurs normaux, afficher uniquement la session active
            # et ne pas permettre de la changer
            current_session = db.get_selected_session()
            
            if current_session:
                st.subheader("Current Session")
                
                # Afficher les informations sur la session actuelle
                st.write(f"**{current_session}**")
                
                # Get reference image
                ref_url = db.get_img_ref_url(current_session)
                if ref_url:
                    st.image(ref_url, width=400)
                
                # Vérifier si la session est finalisée
                if db.is_session_finalized(current_session):
                    # Get winner information
                    db = db.firestore.client()
                    session_doc = db.collection("sessions").document(current_session).get()
                    
                    if session_doc.exists:
                        session_data = session_doc.to_dict()
                        winner = session_data.get("winner", "Unknown")
                        winner_votes = session_data.get("winner_votes", 0)
                        
                        st.write(f"🏆 Winner: **{winner}** with {winner_votes} votes")
                    
                    # Button to view results
                    if st.button("View Results"):
                        st.switch_page("pages/07_Results.py")
                else:
                    # Afficher les instructions pour participer
                    st.write("""
                    ### How to participate:
                    1. Go to the 'Prompt' page to generate your image
                    2. Submit your best creation to the gallery
                    3. Vote for other participants' images in the 'Gallery' page
                    """)
                    
                    # Afficher le temps restant si disponible
                    end_time = db.get_session_end_time(current_session)
                    if end_time:
                        now = datetime.now()
                        
                        if now < end_time:
                            time_remaining = end_time - now
                            days = time_remaining.days
                            hours, remainder = divmod(time_remaining.seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            
                            st.write(f"**Time Remaining:** {days} days, {hours} hours, {minutes} minutes")
                            
                            # Progress bar
                            total_seconds = (end_time - now).total_seconds()
                            max_seconds = 7 * 24 * 60 * 60  # 1 week in seconds
                            progress = 1 - (total_seconds / max_seconds)
                            st.progress(min(max(progress, 0), 1))
                        else:
                            st.warning("Voting period has ended")
            else:
                # Si aucune session n'est sélectionnée, afficher un message
                st.info("No active session available. Please wait for the administrator to start a new session.")
    else:
        st.warning("No sessions available. Please contact the administrator.")
    
    # Admin section
    if st.session_state["pseudo"] == "alex_lav":
        st.subheader("Admin Controls")
        
        # Get current session
        current_session = db.get_selected_session()
        
        if current_session:
            st.write(f"Current session: **{current_session}**")
            
            # Check if session is finalized
            is_finalized = db.is_session_finalized(current_session)
            
            if not is_finalized:
                # Button to finalize session
                if st.button("Finalize Session"):
                    if db.finalize_session(current_session):
                        st.success(f"Session {current_session} finalized!")
                        st.rerun()
                    else:
                        st.error("Error finalizing session.")
            else:
                st.info(f"Session {current_session} is already finalized.")
        else:
            st.info("No session selected.")
        
        # Add session management controls
        st.subheader("Session Management")
        
        # Create new session
        with st.expander("Create New Session"):
            new_session_name = st.text_input("Session Name")
            
            # Option pour choisir entre URL et upload
            image_source = st.radio("Reference Image Source", ["Upload Image", "Image URL"])
            
            ref_image_url = None
            uploaded_file = None
            
            if image_source == "Image URL":
                ref_image_url = st.text_input("Reference Image URL")
            else:  # Upload Image
                uploaded_file = st.file_uploader("Upload Reference Image", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    # Afficher l'aperçu de l'image
                    st.image(uploaded_file, caption="Preview", width=300)
            
            if st.button("Create Session") and new_session_name:
                if image_source == "Image URL" and ref_image_url:
                    # Créer une session avec URL
                    if db.create_session(new_session_name, ref_image_url):
                        st.success(f"Session {new_session_name} created!")
                        st.rerun()
                    else:
                        st.error("Error creating session.")
                elif image_source == "Upload Image" and uploaded_file is not None:
                    # Uploader l'image et créer une session
                    with st.spinner("Uploading image..."):
                        # Convertir le fichier uploadé en bytes
                        file_bytes = uploaded_file.getvalue()
                        
                        # Uploader l'image vers Firebase Storage
                        ref_image_url = db.upload_image_to_storage(file_bytes, f"reference_images/{new_session_name}_{uploaded_file.name}")
                        
                        if ref_image_url:
                            # Créer la session avec l'URL de l'image uploadée
                            if db.create_session(new_session_name, ref_image_url):
                                st.success(f"Session {new_session_name} created with uploaded image!")
                                st.rerun()
                            else:
                                st.error("Error creating session.")
                        else:
                            st.error("Error uploading image.")
                else:
                    st.warning("Please provide a session name and either an image URL or upload an image.")
        
        # Set session end time
        with st.expander("Set Session End Time"):
            end_date = st.date_input("End Date")
            end_time = st.time_input("End Time")
            
            # Combine date and time
            end_datetime = datetime.combine(end_date, end_time)
            
            if st.button("Set End Time") and current_session:
                if db.set_session_end_time(current_session, end_datetime):
                    st.success(f"End time for session {current_session} set to {end_datetime}!")
                    st.rerun()
                else:
                    st.error("Error setting end time.")

# Footer
st.markdown("""
---
<div style="text-align: center; color: gray; font-size: 0.8em;">
ESCP AI Champions - Battle of Prompt | April 4th, 2025 | ESCP Business School
</div>
""", unsafe_allow_html=True)
