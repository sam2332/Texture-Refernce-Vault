from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from ... import db
from ...models.collection import Collection
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission, allowed_file, get_image_dimensions


@login_required
def upload_image(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to upload to this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            from flask import current_app
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Read file data before saving
            file_data = file.read()
            file.seek(0)  # Reset file pointer
            
            file.save(filepath)
            
            # Get image dimensions
            width, height = get_image_dimensions(filepath)
            
            # Create image record
            image = TextureImage(
                filename=filename,
                original_filepath=request.form.get('original_path', ''),
                current_filepath=filepath,
                width=width,
                height=height,
                file_size=len(file_data),
                collection_id=id,
                uploaded_by=current_user.id
            )
            
            db.session.add(image)
            db.session.commit()
            
            # Create initial version
            version = ImageVersion(
                image_id=image.id,
                version_number=1,
                filepath=filepath,
                uploaded_by=current_user.id,
                data=file_data,
                is_current=True
            )
            
            db.session.add(version)
            db.session.commit()
            
            flash('Image uploaded successfully!')
            return redirect(url_for('collections.view_collection', id=id))
        else:
            flash('Invalid file type. Please upload an image file.')
    
    return render_template('upload_image.html', collection=collection)


def register_route(app):
    """Register the upload_image route with the Flask app"""
    app.add_url_rule('/image/collection/<int:id>/upload', 'images.upload_image', upload_image, methods=['GET', 'POST'])
