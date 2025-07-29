from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import shutil
import uuid
import mimetypes
from .. import db
from ..models.collection import Collection
from ..models.image import TextureImage, ImageVersion
from ..utils.helpers import has_collection_permission, allowed_file, get_image_dimensions

images_bp = Blueprint('images', __name__)

@images_bp.route('/collection/<int:id>/upload', methods=['GET', 'POST'])
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

@images_bp.route('/<int:id>')
@login_required
def view_image(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this image.')
        return redirect(url_for('main.dashboard'))
    
    versions = ImageVersion.query.filter_by(image_id=id).order_by(ImageVersion.version_number.desc()).all()
    return render_template('view_image.html', image=image, collection=collection, versions=versions)

@images_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_image(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to edit images in this collection.')
        return redirect(url_for('images.view_image', id=id))
    
    if request.method == 'POST':
        # Update image metadata
        image.filename = request.form.get('filename', image.filename)
        image.original_filepath = request.form.get('original_filepath', image.original_filepath)
        
        db.session.commit()
        flash('Image updated successfully!')
        return redirect(url_for('images.view_image', id=id))
    
    return render_template('edit_image.html', image=image, collection=collection)

@images_bp.route('/<int:id>/upload_version', methods=['POST'])
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
    
    db.session.commit()
    
    flash('New version uploaded successfully!')
    return redirect(url_for('images.view_image', id=id))

@images_bp.route('/<int:id>/publish')
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

@images_bp.route('/<int:id>/serve')
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

@images_bp.route('/version/<int:version_id>/serve')
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
