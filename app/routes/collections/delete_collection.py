from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection
from ...utils.helpers import has_collection_permission


@login_required
def delete_collection(id):
    collection = Collection.query.get_or_404(id)
    
    # Allow deletion if user is owner, admin, or if collection is unowned and user has admin permission
    can_delete = (
        (collection.created_by and collection.created_by == current_user.id) or 
        current_user.is_admin or
        (not collection.created_by and has_collection_permission(current_user, collection, 'admin'))
    )
    
    if not can_delete:
        flash('You do not have permission to delete this collection.')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(collection)
    db.session.commit()
    
    flash('Collection deleted successfully!')
    return redirect(url_for('main.dashboard'))


def register_route(app):
    """Register the delete_collection route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/delete', 'collections.delete_collection', delete_collection)
