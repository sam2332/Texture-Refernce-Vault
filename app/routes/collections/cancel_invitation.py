from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection
from ...models.invitation import CollectionInvitation


@login_required
def cancel_invitation(id, invitation_id):
    collection = Collection.query.get_or_404(id)
    invitation = CollectionInvitation.query.get_or_404(invitation_id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage invitations for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    db.session.delete(invitation)
    db.session.commit()
    
    flash('Invitation cancelled successfully!')
    return redirect(url_for('collections.manage_permissions', id=id))


def register_route(app):
    """Register the cancel_invitation route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/cancel_invitation/<int:invitation_id>', 'collections.cancel_invitation', cancel_invitation)
