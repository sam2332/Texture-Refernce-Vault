from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from ... import db
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission, allowed_file, get_image_dimensions


@login_required
def upload_version(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to upload versions to this collection.')
        return redirect(url_for('images.view_image', id=id))
    
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('images.view_image', id=id))
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file')
        return redirect(url_for('images.view_image', id=id))
    
    from flask import current_app
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    
    # Read file data before saving
    file_data = file.read()
    file.seek(0)  # Reset file pointer
    
    file.save(filepath)
    
    # Get next version number
    last_version = ImageVersion.query.filter_by(image_id=id).order_by(ImageVersion.version_number.desc()).first()
    next_version = (last_version.version_number + 1) if last_version else 1
    
    # Mark all previous versions as not current
    ImageVersion.query.filter_by(image_id=id).update({'is_current': False})
    
    # Create new version
    version = ImageVersion(
        image_id=id,
        version_number=next_version,
        filepath=filepath,
        uploaded_by=current_user.id,
        data=file_data,
        is_current=True
    )
    
    db.session.add(version)
    
    # Update image with new dimensions and filepath
    width, height = get_image_dimensions(filepath)
    image.current_filepath = filepath
    image.width = width
    image.height = height
    image.file_size = len(file_data)
    
    # Mark image as unpublished since we have a new version
    image.is_published = False
    
    db.session.commit()
    
    flash('New version uploaded successfully!')
    return redirect(url_for('images.view_image', id=id))


def register_route(app):
    """Register the upload_version route with the Flask app"""
    app.add_url_rule('/image/<int:id>/upload_version', 'images.upload_version', upload_version, methods=['POST'])
