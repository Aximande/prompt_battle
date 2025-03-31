# import replicate
from openai import OpenAI
import os
import streamlit as st

import urllib.request
import json

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


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
