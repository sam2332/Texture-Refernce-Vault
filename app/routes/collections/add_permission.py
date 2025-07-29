from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission


@login_required
def add_permission(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    user_id = request.form['user_id']
    permission_level = request.form['permission_level']
    
    # Check if permission already exists
    existing = CollectionPermission.query.filter_by(
        user_id=user_id, 
        collection_id=id
    ).first()
    
    if existing:
        existing.permission_level = permission_level
        flash('Permission updated successfully!')
    else:
        permission = CollectionPermission(
            user_id=user_id,
            collection_id=id,
            permission_level=permission_level
        )
        db.session.add(permission)
        flash('Permission added successfully!')
    
    db.session.commit()
    return redirect(url_for('collections.manage_permissions', id=id))


def register_route(app):
    """Register the add_permission route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/add_permission', 'collections.add_permission', add_permission, methods=['POST'])
