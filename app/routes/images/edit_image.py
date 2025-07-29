from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.image import TextureImage
from ...utils.helpers import has_collection_permission


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


def register_route(app):
    """Register the edit_image route with the Flask app"""
    app.add_url_rule('/image/<int:id>/edit', 'images.edit_image', edit_image, methods=['GET', 'POST'])
