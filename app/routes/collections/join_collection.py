from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission


@login_required
def join_collection(id):
    """Allow users to join public collections with read permissions"""
    collection = Collection.query.get_or_404(id)
    
    # Check if collection is public
    if not collection.is_public:
        flash('This collection is private and cannot be joined directly.')
        return redirect(url_for('main.dashboard'))
    
    # Check if user already has permission
    existing_permission = CollectionPermission.query.filter_by(
        user_id=current_user.id,
        collection_id=id
    ).first()
    
    if existing_permission:
        flash('You already have access to this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    # Check if user is the creator
    if collection.created_by == current_user.id:
        flash('You are the creator of this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    try:
        # Add read permission for the user
        permission = CollectionPermission(
            user_id=current_user.id,
            collection_id=id,
            permission_level='read'
        )
        db.session.add(permission)
        db.session.commit()
        
        flash(f'Successfully joined "{collection.name}" with read access!')
        return redirect(url_for('collections.view_collection', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error joining collection: {str(e)}')
        return redirect(url_for('main.dashboard'))


def register_route(app):
    """Register the join_collection route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/join', 'collections.join_collection', join_collection, methods=['POST'])
