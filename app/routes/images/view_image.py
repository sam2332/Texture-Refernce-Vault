from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ...models.image import TextureImage, ImageVersion
from ...utils.helpers import has_collection_permission


@login_required
def view_image(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this image.')
        return redirect(url_for('main.dashboard'))
    
    versions = ImageVersion.query.filter_by(image_id=id).order_by(ImageVersion.version_number.desc()).all()
    return render_template('view_image.html', image=image, collection=collection, versions=versions)


def register_route(app):
    """Register the view_image route with the Flask app"""
    app.add_url_rule('/image/<int:id>', 'images.view_image', view_image)
