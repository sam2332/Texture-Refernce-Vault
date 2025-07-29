from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection, CollectionPermission
from ...models.user import User


@login_required
def transfer_ownership(id):
    """Allow collection owner to transfer ownership to another member"""
    collection = Collection.query.get_or_404(id)
    
    # Only current owner can transfer ownership
    if collection.created_by != current_user.id:
        flash('You must be the owner to transfer ownership.')
        return redirect(url_for('collections.view_collection', id=id))
    
    new_owner_id = request.form.get('new_owner_id')
    if not new_owner_id:
        flash('Please select a new owner.')
        return redirect(url_for('collections.manage_permissions', id=id))
    
    try:
        new_owner_id = int(new_owner_id)
        
        # Check if the new owner has permission to the collection
        new_owner_permission = CollectionPermission.query.filter_by(
            user_id=new_owner_id,
            collection_id=id
        ).first()
        
        if not new_owner_permission:
            flash('The selected user is not a member of this collection.')
            return redirect(url_for('collections.manage_permissions', id=id))
        
        # Get the new owner user object for the flash message
        new_owner = User.query.get(new_owner_id)
        if not new_owner:
            flash('Selected user not found.')
            return redirect(url_for('collections.manage_permissions', id=id))
        
        # Transfer ownership
        collection.created_by = new_owner_id
        
        # Ensure new owner has admin permissions
        new_owner_permission.permission_level = 'admin'
        
        # Add current owner as a regular member with admin permissions
        current_owner_permission = CollectionPermission(
            user_id=current_user.id,
            collection_id=id,
            permission_level='admin'
        )
        db.session.add(current_owner_permission)
        
        db.session.commit()
        flash(f'Ownership of "{collection.name}" has been transferred to {new_owner.username}.')
        return redirect(url_for('collections.view_collection', id=id))
        
    except ValueError:
        flash('Invalid user selection.')
        return redirect(url_for('collections.manage_permissions', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error transferring ownership: {str(e)}')
        return redirect(url_for('collections.manage_permissions', id=id))


def register_route(app):
    """Register the transfer_ownership route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/transfer_ownership', 'collections.transfer_ownership', transfer_ownership, methods=['POST'])
