from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ...models.collection import Collection
from ...models.image import TextureImage
from ...utils.helpers import has_collection_permission


@login_required
def view_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this collection.')
        return redirect(url_for('main.dashboard'))
    
    images = TextureImage.query.filter_by(collection_id=id).all()
    return render_template('view_collection.html', 
                         collection=collection, 
                         images=images, 
                         has_collection_permission=has_collection_permission)


def register_route(app):
    """Register the view_collection route with the Flask app"""
    app.add_url_rule('/collection/<int:id>', 'collections.view_collection', view_collection)
