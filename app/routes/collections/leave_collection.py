from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission


@login_required
def leave_collection(id):
    """Allow users to leave any collection, including their own"""
    collection = Collection.query.get_or_404(id)
    
    # Check if user has any relationship to this collection
    is_creator = collection.created_by == current_user.id
    user_permission = CollectionPermission.query.filter_by(
        user_id=current_user.id,
        collection_id=id
    ).first()
    
    if not is_creator and not user_permission:
        flash('You are not a member of this collection.')
        return redirect(url_for('main.dashboard'))
    
    try:
        if is_creator:
            # Owner is leaving - make collection unowned
            collection.created_by = None
            flash(f'You have left "{collection.name}". The collection is now unowned and can be claimed by other members.')
        
        # Remove user's permission if they have one
        if user_permission:
            db.session.delete(user_permission)
            if not is_creator:
                flash(f'You have left "{collection.name}".')
        
        db.session.commit()
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error leaving collection: {str(e)}')
        return redirect(url_for('collections.view_collection', id=id))


def register_route(app):
    """Register the leave_collection route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/leave', 'collections.leave_collection', leave_collection, methods=['POST'])
