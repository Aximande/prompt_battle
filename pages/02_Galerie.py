import streamlit as st
from google.cloud import firestore
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# This line must be the first Streamlit command
st.set_page_config(page_title="ESCP AI Champions - Gallery", layout="wide")

from PIL import Image
from streamlit_carousel import carousel
import db_manager as db
import math
from utils.session_utils import pseudo_dialog

db.initialize_firebase()

st.sidebar.image(
    Image.open("static/ESCP_LOGO_CMJN.png"),
    width=150,
)

if "pseudo" not in st.session_state or st.session_state["pseudo"] == "":
    st.warning("Please set your username on the home page first.")
    st.stop()

if st.sidebar.button("Reload"):
    st.rerun()

# Admin controls in sidebar
if st.session_state["pseudo"] == "alex_lav":
    st.sidebar.subheader("Admin Controls")
    
    # Session selection dropdown
    names = [""] + db.get_all_session_names()
    
    # Check if the selected_session exists in names
    if "selected_session" in st.session_state and st.session_state["selected_session"] not in names:
        st.session_state["selected_session"] = ""  # Reset to empty if not found
    
    # Find the correct index, defaulting to 0 if not found
    default_index = 0
    if "selected_session" in st.session_state:
        try:
            default_index = names.index(st.session_state["selected_session"])
        except ValueError:
            default_index = 0
    
    selected_session = st.sidebar.selectbox(
        "Available sessions",
        names,
        index=default_index,
    )
    
    if selected_session != st.session_state.get("selected_session", ""):
        st.session_state["selected_session"] = selected_session
        db.select_session(selected_session)
        st.sidebar.success(f"Switched to session: {selected_session}")
        st.rerun()

    # Button to restart session
    if st.sidebar.button("Restart session"):
        session_name = db.get_selected_session()
        if session_name:
            # Add confirmation to prevent accidental restarts
            confirm = st.sidebar.checkbox("Confirm restart (this will clear all votes)")
            if confirm:
                db.clear_session(session_name)
                st.sidebar.success(f"Session {session_name} restarted!")
                st.rerun()
        else:
            st.sidebar.error("No session selected")
    
    # Button to change reference image
    with st.sidebar.expander("Change Reference Image"):
        image_source = st.radio("New Reference Image Source", ["Upload Image", "Image URL"])
        
        new_ref_url = None
        uploaded_file = None
        
        if image_source == "Image URL":
            new_ref_url = st.text_input("New Reference Image URL")
        else:  # Upload Image
            uploaded_file = st.file_uploader("Upload New Reference Image", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                # Afficher l'aperçu de l'image
                st.image(uploaded_file, caption="Preview", width=200)
        
        if st.button("Update Reference Image"):
            session_name = db.get_selected_session()
            if session_name:
                if image_source == "Image URL" and new_ref_url:
                    # Mettre à jour avec URL
                    if db.update_reference_image(session_name, new_ref_url=new_ref_url):
                        st.success(f"Reference image updated for session {session_name}")
                        st.rerun()
                    else:
                        st.error("Error updating reference image")
                elif image_source == "Upload Image" and uploaded_file is not None:
                    # Mettre à jour avec image uploadée
                    with st.spinner("Uploading image..."):
                        # Convertir le fichier uploadé en bytes
                        file_bytes = uploaded_file.getvalue()
                        
                        # Mettre à jour l'image de référence
                        if db.update_reference_image(session_name, uploaded_file=file_bytes):
                            st.success(f"Reference image updated for session {session_name}")
                            st.rerun()
                        else:
                            st.error("Error updating reference image")
                else:
                    st.warning("Please provide either an image URL or upload an image.")
            else:
                st.error("No session selected")
    
    # Button to finalize session
    if st.sidebar.button("Finalize Session"):
        session_name = db.get_selected_session()
        if session_name:
            if not db.is_session_finalized(session_name):
                if db.finalize_session(session_name):
                    st.sidebar.success(f"Session {session_name} finalized!")
                    st.rerun()
                else:
                    st.sidebar.error("Error finalizing session")
            else:
                st.sidebar.info(f"Session {session_name} is already finalized")
        else:
            st.sidebar.error("No session selected")

session_name = db.get_selected_session()
st.session_state["selected_session"] = session_name

# Main content
st.title("Image Gallery & Voting")

# Add refresh button
if st.button("Refresh Gallery"):
    st.rerun()

# Initialiser votes comme un dictionnaire vide par défaut
votes = {}

# Get selected session
if not session_name:
    st.warning("No session selected. Please choose a session on the home page.")
else:
    st.header(f"Session: {session_name}")
    
    # Create a layout with the reference image prominently displayed
    col_ref, col_info = st.columns([1, 2])
    
    with col_ref:
        # Get reference image
        ref_url = db.get_img_ref_url(session_name)
        if ref_url:
            st.subheader("Reference Image")
            st.image(ref_url, use_container_width=True)
            
            # Add session information below the reference image
            st.write("### Challenge")
            st.write("Create an image that best matches this reference image.")
            
            # Add voting information
            st.write("### Voting")
            st.write("Vote for the image you think best matches the reference image.")
            st.write("You can only vote for one image, but you can change your vote at any time.")
            
            # Add time remaining if end time is set
            end_time = db.get_session_end_time(session_name)
            if end_time:
                now = datetime.now()
                
                if now < end_time:
                    time_remaining = end_time - now
                    days = time_remaining.days
                    hours, remainder = divmod(time_remaining.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    st.write("### Time Remaining")
                    st.write(f"{days} days, {hours} hours, {minutes} minutes")
                    
                    # Progress bar
                    total_seconds = (end_time - now).total_seconds()
                    max_seconds = 7 * 24 * 60 * 60  # 1 week in seconds
                    progress = 1 - (total_seconds / max_seconds)
                    st.progress(min(max(progress, 0), 1))
                else:
                    st.warning("Voting period has ended")
    
    with col_info:
        # Get all images for this session
        images = db.get_all_images_for_session(session_name)
        
        if not images:
            st.info("No images have been submitted for this session yet.")
        else:
            # Utiliser directement toutes les images sans filtrage
            filtered_images = images
            
            # Get votes for this session
            votes = db.get_votes_for_session(session_name)
            
            # Get current user's vote
            current_user_vote = db.get_user_vote(session_name, st.session_state["pseudo"])
            
            # Add vote counts to images
            for img in filtered_images:
                img["votes"] = votes.get(img["title"], 0)
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Gallery View", "Leaderboard", "Carousel View"])
            
            with tab1:
                # Display images in a grid
                st.subheader("Gallery")
                
                # Create a grid of images
                cols = st.columns(2)  # Reduce to 2 columns for larger images
                for i, img_data in enumerate(filtered_images):
                    with cols[i % 2]:
                        # Create a container for the image card
                        with st.container():
                            # Add CSS class based on whether this image has been voted for
                            card_class = "image-card voted-image" if current_user_vote == img_data["title"] else "image-card"
                            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                            
                            # Display image
                            st.image(img_data["img"], use_container_width=True)
                            
                            # Show author and votes
                            author = img_data["title"]
                            vote_count = img_data["votes"]
                            
                            # Don't allow voting for your own image
                            if author == st.session_state["pseudo"]:
                                st.write(f"**Your Image** - {vote_count} votes")
                            else:
                                st.write(f"**{author}** - {vote_count} votes")
                                
                                # Check if user already voted for this image
                                if current_user_vote == author:
                                    if st.button(f"✓ Unvote", key=f"unvote_{i}", help="Remove your vote"):
                                        # Remove vote
                                        if db.remove_vote(session_name, st.session_state["pseudo"]):
                                            st.success("Vote removed!")
                                            st.rerun()
                                else:
                                    # Only show vote button if not already voted for this image
                                    button_text = "Vote for this image" if not current_user_vote else "Change vote to this image"
                                    if st.button(f"🗳️ {button_text}", key=f"vote_{i}", help="Cast your vote for this image"):
                                        # Add vote
                                        if db.add_vote(session_name, st.session_state["pseudo"], author):
                                            st.success(f"Voted for {author}!")
                                            st.rerun()
                            
                            # Show prompt
                            st.write(f"Prompt: {img_data['text'][:100]}...")
                            
                            # Close the container div
                            st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                # Display leaderboard
                st.subheader("Leaderboard")
                
                # Create dataframe for leaderboard
                leaderboard_data = []
                for img in filtered_images:
                    is_current_user = img["title"] == st.session_state["pseudo"]
                    is_voted_for = img["title"] == current_user_vote
                    
                    leaderboard_data.append({
                        "Author": img["title"],
                        "Votes": img["votes"],
                        "Is You": is_current_user,
                        "You Voted For": is_voted_for
                    })
                
                # Sort by votes
                leaderboard_df = pd.DataFrame(leaderboard_data).sort_values("Votes", ascending=False)
                
                # Create a copy of the dataframe with only the columns we want to display
                display_df = leaderboard_df[["Author", "Votes"]].copy()
                
                # Highlight current user
                def highlight_user(row):
                    # Get the index of this row
                    idx = row.name
                    # Check if this row corresponds to the current user
                    if leaderboard_df.loc[idx, "Is You"]:
                        return ["background-color: rgba(0, 255, 0, 0.2)"] * len(row)
                    # Check if this row corresponds to the image the user voted for
                    elif leaderboard_df.loc[idx, "You Voted For"]:
                        return ["background-color: rgba(0, 0, 255, 0.2)"] * len(row)
                    return [""] * len(row)
                
                # Display styled dataframe
                st.dataframe(
                    display_df.style.apply(highlight_user, axis=1),
                    use_container_width=True
                )
                
                # Create a bar chart of votes
                if len(leaderboard_data) > 0:
                    st.subheader("Vote Distribution")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    # Only show top 10 if there are many participants
                    chart_data = leaderboard_df.head(10) if len(leaderboard_df) > 10 else leaderboard_df
                    
                    # Create bar chart
                    bars = sns.barplot(x="Author", y="Votes", data=chart_data, ax=ax)
                    
                    # Rotate x labels for better readability
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    
                    # Highlight bars
                    for i, (idx, row) in enumerate(chart_data.iterrows()):
                        if row["Is You"]:
                            bars.patches[i].set_facecolor("lightgreen")
                        elif row["You Voted For"]:
                            bars.patches[i].set_facecolor("lightblue")
                    
                    st.pyplot(fig)
            
            with tab3:
                # Display carousel view
                st.subheader("Carousel View")
                
                # Ensure items are in the correct format for carousel
                carousel_items = []
                for item in filtered_images:
                    # Make sure each item has the correct format for the carousel
                    carousel_item = {
                        "title": item.get("title", ""),
                        "text": item.get("text", ""),
                        "img": item.get("img", "")
                    }
                    carousel_items.append(carousel_item)
                
                # Display carousel only if there are items
                if carousel_items:
                    try:
                        carousel(items=carousel_items, width=0.9)
                    except Exception as e:
                        st.error(f"Error displaying carousel: {e}")
                        # Display images in grid mode as an alternative
                        for item in carousel_items:
                            st.image(item["img"])
                            st.write(item["title"])
                else:
                    st.warning("No images to display in the carousel.")

# Add debug mode
debug_mode = st.sidebar.checkbox("Debug Mode")

# Display debug information if enabled
if debug_mode:
    st.sidebar.subheader("Debug Information")
    st.sidebar.write(f"Session: {session_name}")
    st.sidebar.write(f"Current user: {st.session_state['pseudo']}")
    st.sidebar.write(f"Current vote: {current_user_vote}")
    
    # Get raw data
    db = firestore.client()
    
    st.sidebar.subheader("Images in Firestore")
    raw_data = db.collection("sessions").document(session_name).collection("images").get()
    for doc in raw_data:
        st.sidebar.write(f"ID: {doc.id}")
        st.sidebar.json(doc.to_dict())
    
    st.sidebar.subheader("Votes in Firestore")
    raw_votes = db.collection("sessions").document(session_name).collection("votes").get()
    for doc in raw_votes:
        st.sidebar.write(f"Voter: {doc.id}")
        st.sidebar.json(doc.to_dict())

# Add voting status in sidebar
if "pseudo" in st.session_state and session_name:
    current_user_vote = db.get_user_vote(session_name, st.session_state["pseudo"])
    
    if current_user_vote:
        st.sidebar.success(f"You voted for: {current_user_vote}")
    else:
        st.sidebar.warning("You haven't voted yet")

# Display time remaining if end time is set
end_time = db.get_session_end_time(session_name)
if end_time:
    now = datetime.now()
    
    if now < end_time:
        time_remaining = end_time - now
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        st.sidebar.subheader("Time Remaining")
        st.sidebar.write(f"{days} days, {hours} hours, {minutes} minutes")
        
        # Progress bar
        total_seconds = (end_time - now).total_seconds()
        max_seconds = 7 * 24 * 60 * 60  # 1 week in seconds
        progress = 1 - (total_seconds / max_seconds)
        st.sidebar.progress(min(max(progress, 0), 1))
    else:
        st.sidebar.warning("Voting period has ended")

# Vérifier que votes est défini avant de l'utiliser
if 'votes' in locals():
    total_votes = sum(votes.values())
    st.sidebar.metric("Total Votes", total_votes)

    # Store previous votes in session state
    if "previous_votes" not in st.session_state:
        st.session_state["previous_votes"] = {}

    # Compare current votes with previous votes
    for author, count in votes.items():
        previous = st.session_state["previous_votes"].get(author, 0)
        if count > previous:
            st.sidebar.write(f"📈 {author}: +{count - previous}")

    # Update previous votes
    st.session_state["previous_votes"] = votes
else:
    # Si votes n'est pas défini, initialiser avec un compteur à zéro
    st.sidebar.metric("Total Votes", 0)

# Add custom CSS for voting buttons
st.markdown("""
<style>
.vote-button {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 12px;
}
.unvote-button {
    background-color: #f44336;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 12px;
}
.image-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 20px;
}
.voted-image {
    border: 4px solid #4CAF50;
}
</style>
""", unsafe_allow_html=True)

# Debug information about voting
if debug_mode:
    st.sidebar.subheader("Voting Debug")
    st.sidebar.write(f"Current user: {st.session_state.get('pseudo', 'Not set')}")
    st.sidebar.write(f"Current vote: {current_user_vote}")
    st.sidebar.write(f"Total votes: {sum(votes.values())}")
    st.sidebar.write(f"Votes by author: {votes}")
    
    # Check if the current user's vote is correctly recorded
    if current_user_vote:
        vote_doc = db.firestore.client().collection("sessions").document(session_name).collection("votes").document(st.session_state["pseudo"]).get()
        if vote_doc.exists:
            st.sidebar.write("Vote document exists in Firestore")
            st.sidebar.json(vote_doc.to_dict())
        else:
            st.sidebar.error("Vote document does not exist in Firestore!")

# Add debug information about packages
if debug_mode:
    st.sidebar.subheader("Package Information")
    try:
        import pkg_resources
        carousel_version = pkg_resources.get_distribution("streamlit-carousel").version
        st.sidebar.write(f"streamlit-carousel version: {carousel_version}")
    except Exception as e:
        st.sidebar.error(f"Error getting package info: {e}")
