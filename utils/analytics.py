import firebase_admin
from firebase_admin import storage
from datetime import datetime, timedelta

def get_user_statistics():
    """
    Génère des statistiques sur les utilisateurs et leurs images
    """
    bucket = storage.bucket(name="prompt-battle-9b72d.appspot.com")
    blobs = bucket.list_blobs(prefix="images/")
    
    user_stats = {}
    style_stats = {"vivid": 0, "natural": 0}
    size_stats = {"1024x1024": 0, "1792x1024": 0, "1024x1792": 0}
    
    # Pour l'activité récente
    today = datetime.now().date()
    today_count = 0
    week_count = 0
    
    for blob in blobs:
        blob.reload()
        if blob.metadata:
            author = blob.metadata.get('author', 'unknown')
            style = blob.metadata.get('style', '')
            size = blob.metadata.get('size', '')
            
            # Comptage par utilisateur
            if author not in user_stats:
                user_stats[author] = 0
            user_stats[author] += 1
            
            # Comptage par style
            if style in style_stats:
                style_stats[style] += 1
                
            # Comptage par format
            if size in size_stats:
                size_stats[size] += 1
            
            # Comptage par date
            if 'created_at' in blob.metadata:
                try:
                    created_date = datetime.fromisoformat(blob.metadata['created_at']).date()
                    if created_date == today:
                        today_count += 1
                    if today - created_date <= timedelta(days=7):
                        week_count += 1
                except (ValueError, TypeError):
                    pass
    
    return {
        "users": user_stats,
        "styles": style_stats,
        "sizes": size_stats,
        "total_images": sum(user_stats.values()),
        "today_count": today_count,
        "week_count": week_count
    } 