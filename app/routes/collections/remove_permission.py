from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission


@login_required
def remove_permission(id, permission_id):
    collection = Collection.query.get_or_404(id)
    permission = CollectionPermission.query.get_or_404(permission_id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    db.session.delete(permission)
    db.session.commit()
    
    flash('Permission removed successfully!')
    return redirect(url_for('collections.manage_permissions', id=id))


def register_route(app):
    """Register the remove_permission route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/remove_permission/<int:permission_id>', 'collections.remove_permission', remove_permission)
