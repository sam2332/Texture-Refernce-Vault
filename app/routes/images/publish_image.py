from flask import redirect, url_for, flash
from flask_login import login_required, current_user
import os
from ... import db
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission


@login_required
def publish_image(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to publish images in this collection.')
        return redirect(url_for('images.view_image', id=id))
    
    if not image.original_filepath:
        flash('No original filepath specified for this image.')
        return redirect(url_for('images.view_image', id=id))
    
    try:
        # Get current version data and write to original filepath
        current_version = ImageVersion.query.filter_by(image_id=id, is_current=True).first()
        if current_version and current_version.data:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(image.original_filepath), exist_ok=True)
            
            # Write data to original filepath
            with open(image.original_filepath, 'wb') as f:
                f.write(current_version.data)
            
            image.is_published = True
            db.session.commit()
            flash('Image published successfully!')
        else:
            flash('No current version found.')
    except Exception as e:
        flash(f'Error publishing image: {str(e)}')
    
    return redirect(url_for('images.view_image', id=id))


def register_route(app):
    """Register the publish_image route with the Flask app"""
    app.add_url_rule('/image/<int:id>/publish', 'images.publish_image', publish_image)
