from flask import redirect, url_for, flash, Response
from flask_login import login_required, current_user
import mimetypes
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission


@login_required
def serve_image(id):
    """Serve the current version of an image"""
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this image.')
        return redirect(url_for('main.dashboard'))
    
    # Get current version
    current_version = ImageVersion.query.filter_by(image_id=id, is_current=True).first()
    if current_version and current_version.data:
        # Determine MIME type from filename
        mime_type, _ = mimetypes.guess_type(image.filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        return Response(current_version.data, mimetype=mime_type)
    else:
        flash('Image data not found.')
        return redirect(url_for('images.view_image', id=id))


def register_route(app):
    """Register the serve_image route with the Flask app"""
    app.add_url_rule('/image/<int:id>/serve', 'images.serve_image', serve_image)
