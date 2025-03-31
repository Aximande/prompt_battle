import html
from utils.image_search import search_images_by_author
from datetime import datetime

def export_user_gallery(username):
    """
    Export all images from a user with their metadata
    """
    images = search_images_by_author(username)
    
    # Properly escape username for HTML display
    escaped_username = html.escape(username)
    
    # Create HTML document with explicit UTF-8 encoding
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gallery of {escaped_username}</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; margin: 20px; background-color: #f5f5f5; }}
            h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            .gallery {{ display: flex; flex-wrap: wrap; justify-content: center; }}
            .image-card {{ 
                margin: 15px; 
                width: 300px; 
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                background-color: white;
                transition: transform 0.3s ease;
            }}
            .image-card:hover {{ 
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }}
            .image-container {{ 
                height: 300px;
                overflow: hidden;
            }}
            img {{ 
                width: 100%; 
                height: 100%;
                object-fit: cover;
                transition: transform 0.5s ease;
            }}
            .image-card:hover img {{ 
                transform: scale(1.05);
            }}
            .image-info {{ padding: 15px; }}
            .prompt {{ 
                font-size: 14px; 
                color: #555; 
                margin-bottom: 10px;
                max-height: 80px;
                overflow: auto;
            }}
            .metadata {{ 
                display: flex; 
                justify-content: space-between;
                font-size: 12px;
                color: #888;
            }}
            .header {{
                background-color: #4285f4;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Gallery of {escaped_username}</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}</p>
        </div>
        <div class="gallery">
    """
    
    for img in images:
        # Format date for display
        date_str = img['created_at']
        try:
            date_obj = datetime.fromisoformat(date_str)
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = date_str
            
        # Escape prompt for HTML display
        escaped_prompt = html.escape(img['prompt'])
        
        html_content += f"""
        <div class="image-card">
            <div class="image-container">
                <img src="{img['url']}" alt="Generated image">
            </div>
            <div class="image-info">
                <div class="prompt">{escaped_prompt}</div>
                <div class="metadata">
                    <span>Style: {img['style']}</span>
                    <span>{formatted_date}</span>
                </div>
            </div>
        </div>
        """
    
    html_content += """
        </div>
        <footer style="text-align: center; margin-top: 30px; color: #888; font-size: 12px;">
            Created with ESCP AI Champions - Prompt Battle
        </footer>
    </body>
    </html>
    """
    
    return html_content 