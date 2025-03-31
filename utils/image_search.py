import firebase_admin
from firebase_admin import storage

def search_images_by_author(author_name):
    """
    Recherche toutes les images créées par un auteur spécifique
    """
    bucket = storage.bucket(name="prompt-battle-9b72d.appspot.com")
    blobs = bucket.list_blobs(prefix="images/")
    
    matching_images = []
    for blob in blobs:
        blob.reload()  # Recharge les métadonnées
        if blob.metadata and blob.metadata.get('author') == author_name:
            matching_images.append({
                'url': blob.public_url,
                'prompt': blob.metadata.get('prompt', ''),
                'created_at': blob.metadata.get('created_at', ''),
                'style': blob.metadata.get('style', '')
            })
    
    return matching_images

def search_images_by_style(style_name):
    """
    Recherche toutes les images créées avec un style spécifique
    """
    bucket = storage.bucket(name="prompt-battle-9b72d.appspot.com")
    blobs = bucket.list_blobs(prefix="images/")
    
    matching_images = []
    for blob in blobs:
        blob.reload()
        if blob.metadata and blob.metadata.get('style') == style_name:
            matching_images.append({
                'url': blob.public_url,
                'prompt': blob.metadata.get('prompt', ''),
                'author': blob.metadata.get('author', ''),
                'created_at': blob.metadata.get('created_at', '')
            })
    
    return matching_images 