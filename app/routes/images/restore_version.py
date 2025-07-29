from flask import redirect, url_for, flash
from flask_login import login_required, current_user
import os
import tempfile
from ... import db
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission, get_image_dimensions


@login_required
def restore_version(version_id):
    """Restore a previous version by creating a new version with the old data"""
    version = ImageVersion.query.get_or_404(version_id)
    image = version.image
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to restore versions in this collection.')
        return redirect(url_for('images.view_image', id=image.id))
    
    if version.is_current:
        flash('This version is already the current version.')
        return redirect(url_for('images.view_image', id=image.id))
    
    if not version.data:
        flash('Version data not found.')
        return redirect(url_for('images.view_image', id=image.id))
    
    try:
        # Get next version number
        last_version = ImageVersion.query.filter_by(image_id=image.id).order_by(ImageVersion.version_number.desc()).first()
        next_version = (last_version.version_number + 1) if last_version else 1
        
        # Mark all previous versions as not current
        ImageVersion.query.filter_by(image_id=image.id).update({'is_current': False})
        
        # Create new version with the restored data
        new_version = ImageVersion(
            image_id=image.id,
            version_number=next_version,
            filepath=version.filepath,  # Keep reference to original filepath
            uploaded_by=current_user.id,
            data=version.data,  # Copy the data from the old version
            is_current=True
        )
        
        db.session.add(new_version)
        
        # Update image metadata (dimensions might be different if restoring to older version)
        # We'll use a temporary file to get dimensions
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as temp_file:
            temp_file.write(version.data)
            temp_file.flush()
            
            width, height = get_image_dimensions(temp_file.name)
            image.width = width
            image.height = height
            image.file_size = len(version.data)
            
            # Clean up temp file
            os.unlink(temp_file.name)
        
        # Mark image as unpublished since we have a new version
        image.is_published = False
        
        db.session.commit()
        
        flash(f'Version {version.version_number} has been restored as version {next_version}!')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring version: {str(e)}')
    
    return redirect(url_for('images.view_image', id=image.id))


def register_route(app):
    """Register the restore_version route with the Flask app"""
    app.add_url_rule('/image/version/<int:version_id>/restore', 'images.restore_version', restore_version)
