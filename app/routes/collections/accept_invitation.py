from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from datetime import datetime
from ... import db
from ...models.collection import CollectionPermission
from ...models.invitation import CollectionInvitation


def accept_invitation(token):
    invitation = CollectionInvitation.query.filter_by(token=token).first_or_404()
    
    if invitation.is_expired:
        flash('This invitation has expired.')
        return redirect(url_for('main.index'))
    
    if invitation.is_accepted:
        flash('This invitation has already been accepted.')
        return redirect(url_for('main.index'))
    
    if current_user.is_authenticated:
        # User is logged in, check if email matches
        if current_user.email.lower() != invitation.email.lower():
            flash('This invitation is for a different email address.')
            return redirect(url_for('main.index'))
        
        # Accept the invitation
        try:
            # Check if user already has permission (edge case)
            existing_permission = CollectionPermission.query.filter_by(
                user_id=current_user.id,
                collection_id=invitation.collection_id
            ).first()
            
            if existing_permission:
                existing_permission.permission_level = invitation.permission_level
            else:
                permission = CollectionPermission(
                    user_id=current_user.id,
                    collection_id=invitation.collection_id,
                    permission_level=invitation.permission_level
                )
                db.session.add(permission)
            
            invitation.accepted_at = datetime.utcnow()
            invitation.accepted_by = current_user.id
            
            db.session.commit()
            flash('Invitation accepted successfully!')
            return redirect(url_for('collections.view_collection', id=invitation.collection_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error accepting invitation: {str(e)}')
            return redirect(url_for('main.index'))
    else:
        # User not logged in, redirect to register/login with invitation context
        return render_template('accept_invitation.html', invitation=invitation)


def register_route(app):
    """Register the accept_invitation route with the Flask app"""
    app.add_url_rule('/collection/accept_invitation/<token>', 'collections.accept_invitation', accept_invitation)
