# import replicate
from openai import OpenAI
import os
import streamlit as st

import urllib.request
import json

# Initialize OpenAI client with API key from Streamlit secrets or environment variable
def get_openai_client():
    api_key = None
    
    # Essayer d'obtenir la clé depuis les secrets Streamlit
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        pass
    
    # Si pas trouvé, essayer depuis les variables d'environnement
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    # Si toujours pas trouvé, afficher un message d'erreur
    if not api_key:
        st.error("OpenAI API key not found. Please add it to your secrets.toml file or set the OPENAI_API_KEY environment variable.")
        return None
    
    return OpenAI(api_key=api_key)

def generate_image_openai(prompt, style="vivid", quality="standard", size="1024x1024"):
    """
    Generate an image with DALL-E 3
    
    Args:
        prompt (str): Text description of the desired image
        style (str): 'vivid' for hyper-realistic images or 'natural' for more natural-looking images
        quality (str): 'standard' or 'hd' for higher quality
        size (str): Image size ('1024x1024', '1792x1024', or '1024x1792')
    
    Returns:
        str: URL of the generated image
    """
    client = get_openai_client()
    if not client:
        return None
        
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1,
        )
        
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None


########################
## images generation ###
########################


def save_img(img_url, file_path):
    # Takes an image URL as input and saves it to file_path
    if img_url:
        try:
            urllib.request.urlretrieve(img_url, file_path)
        except Exception as e:
            st.error(f"Error saving image: {e}")
