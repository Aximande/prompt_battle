import firebase_admin
from firebase_admin import credentials, initialize_app, storage, db, firestore, auth
import streamlit as st
import os
import base64
import json
from datetime import datetime

import threading

callback_done = threading.Event()


@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        # Vérifier si nous sommes sur Streamlit Cloud (en vérifiant une variable d'environnement)
        if os.environ.get('STREAMLIT_SHARING', '') == 'true':
            # Sur Streamlit Share, utiliser les secrets
            try:
                if "FIREBASE_CREDENTIALS_BASE64" in st.secrets:
                    firebase_json = base64.b64decode(st.secrets["FIREBASE_CREDENTIALS_BASE64"]).decode('utf-8')
                    firebase_config = json.loads(firebase_json)
                    cred = credentials.Certificate(firebase_config)
                    # Initialiser avec l'accès au stockage
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': 'prompt-battle-9b72d.appspot.com'
                    })
                else:
                    st.error("Firebase credentials not found in secrets")
            except Exception as e:
                st.error(f"Error initializing Firebase: {e}")
        else:
            # En local, utiliser le fichier JSON
            json_path = "auth_firebase/prompt-battle-9b72d-firebase-adminsdk-lhuc9-cc4c55a33e.json"
            if os.path.exists(json_path):
                cred = credentials.Certificate(json_path)
                # Initialiser avec l'accès au stockage
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'prompt-battle-9b72d.appspot.com'
                })
            else:
                st.error(f"Firebase credentials file not found at {json_path}")


def add_image(session_name, username, img_url, permanent_url, prompt, style="", size="", check_duplicate=True):
    """
    Add an image to the main gallery
    
    Args:
        session_name (str): Session name
        username (str): Username
        img_url (str): Temporary image URL
        permanent_url (str): Permanent image URL
        prompt (str): Prompt used to generate the image
        style (str): Style used
        size (str): Image format
        check_duplicate (bool): Check if user has already submitted an image
    
    Returns:
        bool: True if image was added, False otherwise
    """
    db = firestore.client()
    
    # Check if user has already submitted an image for this session
    if check_duplicate:
        doc = db.collection("sessions").document(session_name).collection("images").document(username).get()
        if doc.exists:
            st.warning(f"You have already submitted an image for this session. Your new image will replace the old one.")
            # Option: Return False here to prevent replacement
            # return False
    
    # Add the image
    db.collection("sessions").document(session_name).collection("images").document(
        username
    ).set({
        "img_url": permanent_url,  # Use permanent URL
        "temp_url": img_url,       # Keep temporary URL for reference
        "prompt": prompt,
        "style": style,
        "size": size,
        "timestamp": datetime.now().isoformat()
    })
    
    return True


def get_all_images_for_session(session_name):
    """
    Récupère toutes les images pour une session donnée
    """
    db = firestore.client()
    imgs = db.collection("sessions").document(session_name).collection("images").get()
    
    all_images = []
    for img in imgs:
        usr = img.id
        img_data = img.to_dict()
        
        # Vérifier que les clés nécessaires existent
        if "img_url" in img_data and "prompt" in img_data:
            all_images.append({
                "title": usr,
                "text": img_data.get("prompt", ""),
                "img": img_data.get("img_url", ""),
                "style": img_data.get("style", ""),
                "timestamp": img_data.get("timestamp", "")
            })
    
    # Trier par timestamp si disponible
    all_images.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return all_images


def get_all_session_names():
    db = firestore.client()
    docs = db.collection("sessions").get()
    names = []
    for doc in docs:
        names.append(doc.id)
        # print(f"{doc.id} => {doc.to_dict()}")
    return names


def select_session(session_name):
    db = firestore.client()
    db.collection("admin").document("lavaleexx").set(
        {"selected_session": session_name}, merge=True
    )


def get_selected_session():
    db = firestore.client()
    try:
        doc = db.collection("admin").document("lavaleexx").get()
        if doc.exists:
            doc_dict = doc.to_dict()
            if doc_dict and "selected_session" in doc_dict:
                return doc_dict["selected_session"]
    except Exception as e:
        st.error(f"Error getting selected session: {e}")
    return ""


def get_img_ref_url(session_name):
    db = firestore.client()
    if not session_name:
        return None
        
    doc = db.collection("sessions").document(session_name).get()
    
    if not doc.exists:
        return None
        
    doc_dict = doc.to_dict()
    if not doc_dict or "img_ref_url" not in doc_dict:
        return None
        
    return doc_dict["img_ref_url"]


def _delete_collection(coll_ref, batch_size):
    if batch_size == 0:
        return

    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return _delete_collection(coll_ref, batch_size)


def clear_session(session_name):
    """
    Clear all votes and images for a session
    
    Args:
        session_name (str): Session name
        
    Returns:
        bool: True if session was cleared successfully
    """
    db = firestore.client()
    
    try:
        # Delete all votes
        votes_ref = db.collection("sessions").document(session_name).collection("votes")
        delete_collection(votes_ref, 100)
        
        # Reset session status
        session_ref = db.collection("sessions").document(session_name)
        session_ref.update({
            "finalized": False,
            "winner": "",
            "winner_votes": 0,
            "finalized_at": ""
        })
        
        return True
    except Exception as e:
        st.error(f"Error clearing session: {e}")
        return False


def delete_collection(coll_ref, batch_size):
    """
    Helper function to delete a collection
    
    Args:
        coll_ref: Collection reference
        batch_size (int): Batch size for deletion
    """
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    
    for doc in docs:
        doc.reference.delete()
        deleted += 1
        
    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


# def get_selection_watch():
#     # Create an Event for notifying main thread.
#     db = firestore.client()
#     callback_done = threading.Event()

#     # Create a callback on_snapshot function to capture changes
#     def on_snapshot(doc_snapshot, changes, read_time):
#         for doc in doc_snapshot:
#             st.session_state["selected_session_db"] = doc.to_dict()["selected_session"]
#         callback_done.set()

#     doc_ref = db.collection("admin").document("lavaleexx")

#     # Watch the document
#     return callback_done, doc_ref.on_snapshot(on_snapshot)


def add_vote(session_name, voter_username, image_author):
    """
    Add or update a vote for an image
    
    Args:
        session_name (str): Session name
        voter_username (str): Username of the voter
        image_author (str): Username of the image author (image ID)
        
    Returns:
        bool: True if vote was added/updated successfully
    """
    db = firestore.client()
    
    try:
        # Create a document ID based on the voter's username
        vote_ref = db.collection("sessions").document(session_name).collection("votes").document(voter_username)
        
        # Set the vote data (overwriting any previous vote by this user)
        vote_ref.set({
            "voted_for": image_author,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    except Exception as e:
        st.error(f"Error adding vote: {e}")
        return False


def get_votes_for_session(session_name):
    """
    Get all votes for a session
    
    Args:
        session_name (str): Session name
        
    Returns:
        dict: Dictionary with image authors as keys and vote counts as values
    """
    db = firestore.client()
    
    try:
        # Get all votes for this session
        votes = db.collection("sessions").document(session_name).collection("votes").get()
        
        # Count votes for each image
        vote_counts = {}
        for vote in votes:
            vote_data = vote.to_dict()
            voted_for = vote_data.get("voted_for")
            
            if voted_for:
                if voted_for not in vote_counts:
                    vote_counts[voted_for] = 0
                vote_counts[voted_for] += 1
        
        return vote_counts
    except Exception as e:
        st.error(f"Error getting votes: {e}")
        return {}


def get_user_vote(session_name, username):
    """
    Get the current vote of a user for a session
    
    Args:
        session_name (str): Session name
        username (str): Username of the voter
        
    Returns:
        str: Username of the image author the user voted for, or None
    """
    db = firestore.client()
    
    try:
        vote_doc = db.collection("sessions").document(session_name).collection("votes").document(username).get()
        
        if vote_doc.exists:
            vote_data = vote_doc.to_dict()
            return vote_data.get("voted_for")
        
        return None
    except Exception as e:
        st.error(f"Error getting user vote: {e}")
        return None


def remove_vote(session_name, voter_username):
    """
    Remove a user's vote
    
    Args:
        session_name (str): Session name
        voter_username (str): Username of the voter
        
    Returns:
        bool: True if vote was removed successfully
    """
    db = firestore.client()
    
    try:
        vote_ref = db.collection("sessions").document(session_name).collection("votes").document(voter_username)
        vote_ref.delete()
        return True
    except Exception as e:
        st.error(f"Error removing vote: {e}")
        return False


def finalize_session(session_name):
    """
    Finalize a session and declare a winner
    
    Args:
        session_name (str): Session name
        
    Returns:
        bool: True if session was finalized successfully
    """
    db = firestore.client()
    
    try:
        # Get votes for this session
        votes = get_votes_for_session(session_name)
        
        # Find the winner
        winner = None
        max_votes = 0
        
        for author, vote_count in votes.items():
            if vote_count > max_votes:
                max_votes = vote_count
                winner = author
        
        # Update session with winner information
        session_ref = db.collection("sessions").document(session_name)
        session_ref.update({
            "finalized": True,
            "winner": winner,
            "winner_votes": max_votes,
            "finalized_at": datetime.now().isoformat()
        })
        
        return True
    except Exception as e:
        st.error(f"Error finalizing session: {e}")
        return False


def is_session_finalized(session_name):
    """
    Check if a session is finalized
    
    Args:
        session_name (str): Session name
        
    Returns:
        bool: True if session is finalized
    """
    db = firestore.client()
    
    try:
        session_doc = db.collection("sessions").document(session_name).get()
        
        if session_doc.exists:
            session_data = session_doc.to_dict()
            return session_data.get("finalized", False)
        
        return False
    except Exception as e:
        st.error(f"Error checking if session is finalized: {e}")
        return False


def get_session_end_time(session_name):
    """
    Get the end time for a session
    
    Args:
        session_name (str): Session name
        
    Returns:
        datetime: End time for the session, or None if not set
    """
    db = firestore.client()
    
    try:
        session_doc = db.collection("sessions").document(session_name).get()
        
        if session_doc.exists:
            session_data = session_doc.to_dict()
            end_time_str = session_data.get("end_time")
            
            if end_time_str:
                return datetime.fromisoformat(end_time_str)
        
        return None
    except Exception as e:
        st.error(f"Error getting session end time: {e}")
        return None


def set_session_end_time(session_name, end_time):
    """
    Set the end time for a session
    
    Args:
        session_name (str): Session name
        end_time (datetime): End time for the session
        
    Returns:
        bool: True if end time was set successfully
    """
    db = firestore.client()
    
    try:
        session_ref = db.collection("sessions").document(session_name)
        session_ref.update({
            "end_time": end_time.isoformat()
        })
        
        return True
    except Exception as e:
        st.error(f"Error setting session end time: {e}")
        return False


def update_reference_image(session_name, new_ref_url=None, uploaded_file=None):
    """
    Update the reference image URL for a session
    
    Args:
        session_name (str): Session name
        new_ref_url (str, optional): New reference image URL
        uploaded_file (bytes, optional): Uploaded image file
        
    Returns:
        bool: True if reference image was updated successfully
    """
    db = firestore.client()
    
    try:
        # Si un fichier a été uploadé, le stocker d'abord
        if uploaded_file is not None:
            # Uploader l'image vers Firebase Storage
            file_name = f"reference_images/{session_name}_updated_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            new_ref_url = upload_image_to_storage(uploaded_file, file_name)
            
            if not new_ref_url:
                return False
        
        # Mettre à jour l'URL de l'image de référence
        session_ref = db.collection("sessions").document(session_name)
        session_ref.update({
            "ref_url": new_ref_url
        })
        
        return True
    except Exception as e:
        st.error(f"Error updating reference image: {e}")
        return False


def upload_image_to_storage(file_bytes, destination_path):
    """
    Upload an image to Firebase Storage
    
    Args:
        file_bytes (bytes): Image file as bytes
        destination_path (str): Path in Firebase Storage
        
    Returns:
        str: Public URL of the uploaded image, or None if upload failed
    """
    try:
        # Get storage bucket
        bucket = storage.bucket()
        
        # Create a blob and upload the file
        blob = bucket.blob(destination_path)
        blob.upload_from_string(file_bytes, content_type="image/jpeg")
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Return the public URL
        return blob.public_url
    except Exception as e:
        st.error(f"Error uploading image to storage: {e}")
        return None


def create_session(session_name, ref_image_url):
    """
    Create a new session
    
    Args:
        session_name (str): Session name
        ref_image_url (str): URL of the reference image
        
    Returns:
        bool: True if session was created successfully
    """
    db = firestore.client()
    
    try:
        # Check if session already exists
        session_doc = db.collection("sessions").document(session_name).get()
        if session_doc.exists:
            st.error(f"Session {session_name} already exists")
            return False
        
        # Create session
        db.collection("sessions").document(session_name).set({
            "img_ref_url": ref_image_url,
            "ref_url": ref_image_url,  # Duplicate for compatibility
            "created_at": datetime.now().isoformat(),
            "finalized": False,
            "winner": "",
            "winner_votes": 0
        })
        
        # Set as selected session
        select_session(session_name)
        
        return True
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return False
