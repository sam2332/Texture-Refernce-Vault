from flask import request, redirect, url_for, flash, render_template
from datetime import datetime
from ... import db
from ...models.collection import CollectionPermission
from ...models.user import User
from ...models.invitation import CollectionInvitation


def accept_invitation_register(token):
    invitation = CollectionInvitation.query.filter_by(token=token).first_or_404()
    
    if invitation.is_expired or invitation.is_accepted:
        flash('This invitation is no longer valid.')
        return redirect(url_for('main.index'))
    
    # Check if user with this email already exists
    existing_user = User.query.filter_by(email=invitation.email).first()
    if existing_user:
        flash('An account with this email already exists. Please log in instead.')
        return redirect(url_for('auth.login'))
    
    username = request.form['username']
    password = request.form['password']
    
    # Create new user
    try:
        user = User(
            username=username,
            email=invitation.email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create permission
        permission = CollectionPermission(
            user_id=user.id,
            collection_id=invitation.collection_id,
            permission_level=invitation.permission_level
        )
        db.session.add(permission)
        
        # Mark invitation as accepted
        invitation.accepted_at = datetime.utcnow()
        invitation.accepted_by = user.id
        
        db.session.commit()
        
        flash('Account created and invitation accepted successfully! Please log in.')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating account: {str(e)}')
        return render_template('accept_invitation.html', invitation=invitation)


def register_route(app):
    """Register the accept_invitation_register route with the Flask app"""
    app.add_url_rule('/collection/accept_invitation/<token>/register', 'collections.accept_invitation_register', accept_invitation_register, methods=['POST'])
