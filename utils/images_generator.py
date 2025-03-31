# import replicate
from openai import OpenAI
import os
import streamlit as st
import urllib.request
import json
import tempfile
import firebase_admin
from firebase_admin import storage
import uuid
import requests
from io import BytesIO
import base64
from firebase_admin.credentials import Certificate

# Initialize OpenAI client with API key from Streamlit secrets or environment variable
DEBUG = False

if not firebase_admin._apps:
    try:
        # Essayer d'obtenir les credentials depuis les secrets Streamlit
        if "FIREBASE_CREDENTIALS_BASE64" in st.secrets:
            firebase_json = base64.b64decode(st.secrets["FIREBASE_CREDENTIALS_BASE64"]).decode('utf-8')
            firebase_config = json.loads(firebase_json)
            cred = Certificate(firebase_config)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'prompt-battle-9b72d.appspot.com'
            })
        else:
            # En local, utiliser le fichier JSON
            json_path = "auth_firebase/prompt-battle-9b72d-firebase-adminsdk-lhuc9-cc4c55a33e.json"
            if os.path.exists(json_path):
                cred = Certificate(json_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'prompt-battle-9b72d.appspot.com'
                })
            else:
                st.error(f"Firebase credentials file not found at {json_path}")
    except Exception as e:
        st.error(f"Error initializing Firebase in images_generator: {e}")

def get_openai_client():
    if DEBUG:
        st.write("Attempting to get OpenAI client")
    
    api_key = None
    
    # Essayer d'obtenir la clé depuis les secrets Streamlit
    try:
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            if DEBUG:
                st.write("API key found in secrets")
                # Afficher les premiers caractères de la clé pour vérifier
                st.write(f"API key starts with: {api_key[:4]}...")
    except Exception as e:
        if DEBUG:
            st.error(f"Error accessing secrets: {e}")
    
    # Si pas trouvé, essayer depuis les variables d'environnement
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and DEBUG:
            st.write("API key found in environment variables")
    
    # Si toujours pas trouvé, afficher un message d'erreur
    if not api_key:
        st.error("OpenAI API key not found. Please add it to your secrets.toml file or set the OPENAI_API_KEY environment variable.")
        return None
    
    try:
        if DEBUG:
            st.write("Initializing OpenAI client")
        # Créer le client avec seulement l'argument api_key
        client = OpenAI(api_key=api_key)
        if DEBUG:
            st.write("OpenAI client initialized successfully")
        return client
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {e}")
        if DEBUG:
            import traceback
            st.error(traceback.format_exc())
        return None

def generate_image_openai(prompt, style="vivid", quality="standard", size="1024x1024", author=""):
    """
    Generate an image with DALL-E 3
    
    Args:
        prompt (str): Text description of the desired image
        style (str): 'vivid' for hyper-realistic images or 'natural' for more natural-looking images
        quality (str): 'standard' or 'hd' for higher quality
        size (str): Image size ('1024x1024', '1792x1024', or '1024x1792')
        author (str): Username of the creator
    
    Returns:
        tuple: (temporary_url, permanent_url) of the generated image
    """
    try:
        # Obtenir la clé API
        api_key = None
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except Exception as e:
            st.error(f"Error accessing secrets: {e}")
        
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            st.error("OpenAI API key not found")
            return None, None
        
        # Initialiser le client directement ici avec seulement l'argument api_key
        client = OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Store the image permanently in Firebase with metadata
        permanent_url = store_image_in_firebase(image_url, prompt, style, size, author)
        
        return image_url, permanent_url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None, None

def store_image_in_firebase(image_url, prompt, style="", size="", author=""):
    """
    Download image from OpenAI URL and store it permanently in Firebase Storage
    
    Args:
        image_url (str): Temporary URL from OpenAI
        prompt (str): The prompt used to generate the image
        style (str): Style used for generation (vivid/natural)
        size (str): Size format of the image
        author (str): Username of the creator
        
    Returns:
        str: Permanent URL to the stored image
    """
    try:
        if DEBUG:
            st.write("Tentative de stockage de l'image dans Firebase...")
        
        # Download the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            st.error(f"Failed to download image: HTTP {response.status_code}")
            return None
            
        if DEBUG:
            st.write("Image téléchargée avec succès")
        image_data = BytesIO(response.content)
        
        # Generate a unique filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dalle_image_{timestamp}_{uuid.uuid4()}.png"
        
        if DEBUG:
            st.write(f"Nom de fichier généré: {filename}")
        
        # Get Firebase Storage bucket with explicit name
        bucket = storage.bucket(name="prompt-battle-9b72d.appspot.com")
        if DEBUG:
            st.write(f"Bucket obtenu: {bucket.name}")
        
        # Create a new blob and upload the image data
        blob = bucket.blob(f"images/{filename}")
        if DEBUG:
            st.write(f"Chemin du blob: images/{filename}")
        
        # Ajouter des métadonnées à l'image
        metadata = {
            'prompt': prompt,
            'style': style,
            'size': size,
            'author': author,
            'created_at': datetime.now().isoformat(),
            'generated_by': 'DALL-E 3'
        }
        blob.metadata = metadata
        
        # Upload the file with metadata
        blob.upload_from_file(image_data, content_type="image/png")
        if DEBUG:
            st.write("Upload réussi avec métadonnées")
        
        # Make the blob publicly accessible
        blob.make_public()
        if DEBUG:
            st.write("Blob rendu public")
        
        # Return the public URL
        if DEBUG:
            st.write(f"URL publique: {blob.public_url}")
        return blob.public_url
        
    except Exception as e:
        st.error(f"Error storing image in Firebase: {e}")
        if DEBUG:
            import traceback
            st.error(traceback.format_exc())
        return None

def save_img(img_url, file_path):
    # Takes an image URL as input and saves it to file_path
    if img_url:
        try:
            urllib.request.urlretrieve(img_url, file_path)
        except Exception as e:
            st.error(f"Error saving image: {e}")

def check_firebase_initialization():
    """
    Check if Firebase is properly initialized
    """
    try:
        # Get the bucket
        bucket = storage.bucket()
        
        # Store the bucket name in session state for debug purposes
        st.session_state["firebase_bucket"] = bucket.name
        
        return True
    except Exception as e:
        st.error(f"Error initializing Firebase Storage: {e}")
        return False
