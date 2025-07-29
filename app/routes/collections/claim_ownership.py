from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission


@login_required
def claim_ownership(id):
    """Allow members to claim ownership of unowned collections"""
    collection = Collection.query.get_or_404(id)
    
    # Check if collection is unowned
    if collection.created_by is not None:
        flash('This collection already has an owner.')
        return redirect(url_for('collections.view_collection', id=id))
    
    # Check if user has permission to the collection
    user_permission = CollectionPermission.query.filter_by(
        user_id=current_user.id,
        collection_id=id
    ).first()
    
    if not user_permission:
        flash('You must be a member of this collection to claim ownership.')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Set user as the new owner
        collection.created_by = current_user.id
        
        # Upgrade user's permission to admin if it's not already
        if user_permission.permission_level != 'admin':
            user_permission.permission_level = 'admin'
        
        db.session.commit()
        flash(f'You are now the owner of "{collection.name}"!')
        return redirect(url_for('collections.view_collection', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error claiming ownership: {str(e)}')
        return redirect(url_for('collections.view_collection', id=id))


def register_route(app):
    """Register the claim_ownership route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/claim_ownership', 'collections.claim_ownership', claim_ownership, methods=['POST'])
