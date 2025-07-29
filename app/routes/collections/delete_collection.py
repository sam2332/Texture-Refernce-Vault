from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission
from ...models.invitation import CollectionInvitation
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
    
    try:
        # Delete related records first to avoid foreign key constraint issues
        # Delete collection permissions
        CollectionPermission.query.filter_by(collection_id=collection.id).delete()
        
        # Delete collection invitations
        CollectionInvitation.query.filter_by(collection_id=collection.id).delete()
        
        # Delete the collection itself (images will be cascade deleted)
        db.session.delete(collection)
        db.session.commit()
        
        flash('Collection deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting collection: {str(e)}')
    
    return redirect(url_for('main.dashboard'))


def register_route(app):
    """Register the delete_collection route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/delete', 'collections.delete_collection', delete_collection)
