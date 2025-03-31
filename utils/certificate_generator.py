import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import streamlit as st
import os
from datetime import datetime
import requests
from io import BytesIO

def create_winner_certificate(winner_image_url, winner_name, prompt, votes, session_name):
    """
    Create a modern, professional winner certificate with ESCP branding
    
    Args:
        winner_image_url (str): URL of the winning image
        winner_name (str): Name of the winner
        prompt (str): Prompt used to generate the winning image
        votes (int): Number of votes received
        session_name (str): Name of the session
        
    Returns:
        bytes: Certificate image as bytes
    """
    try:
        # Dimensions du certificat (format paysage)
        width, height = 1500, 1000
        
        # Créer une image de fond avec un dégradé ou utiliser une image de fond
        background_path = "static/certificate_background.jpg"
        if os.path.exists(background_path):
            # Utiliser une image de fond existante
            certificate = Image.open(background_path).resize((width, height), Image.LANCZOS)
        else:
            # Créer un fond avec un dégradé bleu foncé à bleu clair
            certificate = Image.new('RGB', (width, height), color=(0, 32, 96))
            
            # Ajouter un effet de dégradé ou une texture
            overlay = Image.new('RGB', (width, height), color=(0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            
            # Créer un dégradé simple
            for y in range(height):
                color_value = int(180 * (y / height)) + 20
                draw_overlay.line([(0, y), (width, y)], fill=(color_value//3, color_value//2, color_value))
            
            # Fusionner avec l'image principale avec une opacité réduite
            certificate = Image.blend(certificate, overlay, alpha=0.5)
            
            # Ajouter un effet de vignette (assombrir les bords)
            mask = Image.new('L', (width, height), 255)
            draw_mask = ImageDraw.Draw(mask)
            
            # Dessiner un rectangle avec des coins arrondis
            padding = 50
            draw_mask.rectangle([(padding, padding), (width-padding, height-padding)], 
                               fill=255, outline=0, width=padding)
            
            # Appliquer un flou au masque
            mask = mask.filter(ImageFilter.GaussianBlur(padding/2))
            
            # Créer une version assombrie de l'image
            darkened = ImageEnhance.Brightness(certificate).enhance(0.7)
            
            # Appliquer le masque
            certificate.paste(darkened, (0, 0), mask)
        
        # Télécharger l'image gagnante
        response = requests.get(winner_image_url)
        if response.status_code != 200:
            st.error(f"Failed to download winner image: HTTP {response.status_code}")
            return None
            
        winner_img = Image.open(io.BytesIO(response.content))
        
        # Redimensionner l'image gagnante pour qu'elle s'intègre bien dans le certificat
        winner_size = 400
        winner_img = winner_img.resize((winner_size, winner_size), Image.LANCZOS)
        
        # Créer un masque circulaire pour l'image gagnante
        mask = Image.new('L', (winner_size, winner_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, winner_size, winner_size), fill=255)
        
        # Appliquer un flou au masque pour adoucir les bords
        mask = mask.filter(ImageFilter.GaussianBlur(1))
        
        # Créer une image temporaire pour l'image gagnante avec un fond transparent
        winner_img_with_mask = Image.new('RGBA', (winner_size, winner_size), (0, 0, 0, 0))
        winner_img_with_mask.paste(winner_img, (0, 0), mask)
        
        # Ajouter une bordure blanche autour de l'image gagnante
        border_size = 10
        bordered_size = winner_size + 2*border_size
        bordered_img = Image.new('RGBA', (bordered_size, bordered_size), (255, 255, 255, 255))
        bordered_img.paste(winner_img_with_mask, (border_size, border_size), winner_img_with_mask)
        
        # Charger le logo ESCP
        logo_path = "static/ESCP_LOGO_CMJN.png"
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            # Redimensionner le logo
            logo_width = 200
            logo_height = int(logo.height * logo_width / logo.width)
            logo = logo.resize((logo_width, logo_height), Image.LANCZOS)
            
            # Créer un masque pour le logo si nécessaire
            if logo.mode == 'RGBA':
                logo_mask = logo.split()[3]  # Utiliser le canal alpha comme masque
            else:
                logo_mask = None
            
            # Positionner le logo en haut à droite
            logo_position = (width - logo_width - 50, 50)
            certificate.paste(logo, logo_position, logo_mask)
        
        # Charger le logo AI Champions ou une autre image
        ai_logo_path = "static/ai_champions_logo.png"
        if os.path.exists(ai_logo_path):
            ai_logo = Image.open(ai_logo_path)
            # Redimensionner le logo
            ai_logo_width = 150
            ai_logo_height = int(ai_logo.height * ai_logo_width / ai_logo.width)
            ai_logo = ai_logo.resize((ai_logo_width, ai_logo_height), Image.LANCZOS)
            
            # Créer un masque pour le logo si nécessaire
            if ai_logo.mode == 'RGBA':
                ai_logo_mask = ai_logo.split()[3]  # Utiliser le canal alpha comme masque
            else:
                ai_logo_mask = None
            
            # Positionner le logo en haut à gauche
            ai_logo_position = (50, 50)
            certificate.paste(ai_logo, ai_logo_position, ai_logo_mask)
        
        # Créer un contexte de dessin
        draw = ImageDraw.Draw(certificate)
        
        # Essayer de charger des polices élégantes
        try:
            title_font = ImageFont.truetype("static/fonts/Montserrat-Bold.ttf", 60)
            subtitle_font = ImageFont.truetype("static/fonts/Montserrat-SemiBold.ttf", 40)
            text_font = ImageFont.truetype("static/fonts/Montserrat-Regular.ttf", 30)
            small_font = ImageFont.truetype("static/fonts/Montserrat-Regular.ttf", 20)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Ajouter un titre élégant
        title_y = 150
        draw.text((width//2, title_y), "CERTIFICATE OF ACHIEVEMENT", 
                 fill=(255, 255, 255), font=title_font, anchor="mm")
        
        # Ajouter une ligne décorative sous le titre
        line_y = title_y + 40
        line_width = 600
        line_height = 3
        draw.rectangle([(width//2 - line_width//2, line_y), 
                       (width//2 + line_width//2, line_y + line_height)], 
                      fill=(255, 215, 0))  # Or
        
        # Ajouter le sous-titre
        draw.text((width//2, line_y + 50), "ESCP AI Champions - Battle of Prompt", 
                 fill=(255, 255, 255), font=subtitle_font, anchor="mm")
        
        # Positionner l'image gagnante
        img_position = (width//2 - bordered_size//2, line_y + 120)
        certificate.paste(bordered_img, img_position, bordered_img)
        
        # Ajouter le nom du gagnant avec un style élégant
        winner_y = img_position[1] + bordered_size + 50
        draw.text((width//2, winner_y), f"Congratulations to", 
                 fill=(255, 255, 255), font=text_font, anchor="mm")
        
        # Nom du gagnant en plus grand et en or
        draw.text((width//2, winner_y + 50), f"{winner_name}", 
                 fill=(255, 215, 0), font=subtitle_font, anchor="mm")
        
        # Ajouter les informations sur la session
        info_y = winner_y + 100
        draw.text((width//2, info_y), f"Winner of session: {session_name}", 
                 fill=(255, 255, 255), font=text_font, anchor="mm")
        
        # Ajouter le nombre de votes
        draw.text((width//2, info_y + 40), f"with {votes} votes", 
                 fill=(255, 255, 255), font=text_font, anchor="mm")
        
        # Ajouter la date
        current_date = datetime.now().strftime("%B %d, %Y")
        draw.text((width//2, info_y + 80), f"Date: {current_date}", 
                 fill=(255, 255, 255), font=text_font, anchor="mm")
        
        # Ajouter le prompt utilisé
        prompt_text = f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}"
        draw.text((width//2, height - 100), prompt_text, 
                 fill=(200, 200, 200), font=small_font, anchor="mm")
        
        # Ajouter un pied de page
        draw.text((width//2, height - 50), "ESCP Business School - AI Champions", 
                 fill=(200, 200, 200), font=small_font, anchor="mm")
        
        # Convertir en bytes
        img_byte_arr = io.BytesIO()
        certificate.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
        
    except Exception as e:
        st.error(f"Error creating certificate: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None 