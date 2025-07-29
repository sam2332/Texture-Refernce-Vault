from flask import redirect, url_for, flash, Response
from flask_login import login_required, current_user
import mimetypes
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission


@login_required
def serve_version(version_id):
    """Serve a specific version of an image"""
    version = ImageVersion.query.get_or_404(version_id)
    image = version.image
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this image.')
        return redirect(url_for('main.dashboard'))
    
    if version.data:
        # Determine MIME type from filename
        mime_type, _ = mimetypes.guess_type(image.filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        return Response(version.data, mimetype=mime_type)
    else:
        flash('Version data not found.')
        return redirect(url_for('images.view_image', id=image.id))


def register_route(app):
    """Register the serve_version route with the Flask app"""
    app.add_url_rule('/image/version/<int:version_id>/serve', 'images.serve_version', serve_version)
