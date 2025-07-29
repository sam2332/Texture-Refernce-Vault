from PIL import Image
from flask import current_app
from ..models.collection import CollectionPermission

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])

def get_image_dimensions(filepath):
    """Get image dimensions from file"""
    try:
        with Image.open(filepath) as img:
            return img.size
    except:
        return None, None

def has_collection_permission(user, collection, required_level='read'):
    """Check if user has required permission level for collection"""
    if user.is_admin:
        return True
    if collection.created_by == user.id:
        return True
    
    permission = CollectionPermission.query.filter_by(
        user_id=user.id, 
        collection_id=collection.id
    ).first()
    
    if not permission:
        return False
    
    levels = {'read': 1, 'write': 2, 'admin': 3}
    return levels.get(permission.permission_level, 0) >= levels.get(required_level, 0)
