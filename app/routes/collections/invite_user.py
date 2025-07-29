from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ... import db
from ...models.collection import Collection, CollectionPermission
from ...models.user import User
from ...models.invitation import CollectionInvitation


@login_required
def invite_user(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    email = request.form['email'].strip().lower()
    permission_level = request.form['permission_level']
    
    # Check if user already has permission
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        existing_permission = CollectionPermission.query.filter_by(
            user_id=existing_user.id,
            collection_id=id
        ).first()
        if existing_permission:
            flash('User already has permission to this collection.')
            return redirect(url_for('collections.manage_permissions', id=id))
    
    # Check if invitation already exists
    existing_invitation = CollectionInvitation.query.filter_by(
        email=email,
        collection_id=id,
        accepted_at=None
    ).first()
    
    if existing_invitation:
        # Update existing invitation
        existing_invitation.permission_level = permission_level
        existing_invitation.invited_by = current_user.id
        existing_invitation.created_at = datetime.utcnow()
        existing_invitation.expires_at = datetime.utcnow() + timedelta(days=7)
        flash('Invitation updated and resent!')
    else:
        # Create new invitation
        invitation = CollectionInvitation(
            collection_id=id,
            invited_by=current_user.id,
            email=email,
            permission_level=permission_level
        )
        db.session.add(invitation)
        flash('Invitation sent successfully!')
    
    try:
        db.session.commit()
        # TODO: Send email notification here
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending invitation: {str(e)}')
    
    return redirect(url_for('collections.manage_permissions', id=id))


def register_route(app):
    """Register the invite_user route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/invite', 'collections.invite_user', invite_user, methods=['POST'])
