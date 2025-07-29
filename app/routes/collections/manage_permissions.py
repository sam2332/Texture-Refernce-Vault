from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ...models.collection import Collection, CollectionPermission
from ...models.user import User
from ...models.invitation import CollectionInvitation
from ...utils.helpers import has_collection_permission


@login_required
def manage_permissions(id):
    collection = Collection.query.get_or_404(id)
    
    # Allow permission management if user is owner, admin, or if collection is unowned and user has admin permission
    can_manage = (
        (collection.created_by and collection.created_by == current_user.id) or 
        current_user.is_admin or
        (not collection.created_by and has_collection_permission(current_user, collection, 'admin'))
    )
    
    if not can_manage:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    users = User.query.all() if current_user.is_admin else None
    permissions = CollectionPermission.query.filter_by(collection_id=id).all()
    invitations = CollectionInvitation.query.filter_by(collection_id=id, accepted_at=None).all()
    
    return render_template('manage_permissions.html', 
                         collection=collection, 
                         users=users, 
                         permissions=permissions,
                         invitations=invitations)


def register_route(app):
    """Register the manage_permissions route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/permissions', 'collections.manage_permissions', manage_permissions, methods=['GET', 'POST'])
