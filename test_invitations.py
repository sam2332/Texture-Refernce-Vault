#!/usr/bin/env python3
"""
Test script to create a sample invitation for testing the dashboard banner
"""

from app import create_app
from app.models import User, Collection, CollectionInvitation
from app import db

def create_test_invitation():
    app = create_app()
    with app.app_context():
        # Get or create a test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(username='testuser', email='test@example.com')
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("Created test user: test@example.com")
        
        # Get first collection
        collection = Collection.query.first()
        if not collection:
            collection = Collection(
                name='Test Collection',
                description='A test collection for testing invitations',
                created_by=test_user.id
            )
            db.session.add(collection)
            db.session.commit()
            print("Created test collection")
        
        # Create invitation for a different email
        invitation_email = 'invited@example.com'
        existing_invitation = CollectionInvitation.query.filter_by(
            email=invitation_email,
            collection_id=collection.id,
            accepted_at=None
        ).first()
        
        if not existing_invitation:
            invitation = CollectionInvitation(
                collection_id=collection.id,
                invited_by=test_user.id,
                email=invitation_email,
                permission_level='read'
            )
            db.session.add(invitation)
            db.session.commit()
            print(f"Created invitation for {invitation_email} to collection '{collection.name}'")
            print(f"Invitation token: {invitation.token}")
            print(f"Accept URL: http://127.0.0.1:5000/collections/accept_invitation/{invitation.token}")
        else:
            print(f"Invitation already exists for {invitation_email}")
            print(f"Invitation token: {existing_invitation.token}")
            print(f"Accept URL: http://127.0.0.1:5000/collections/accept_invitation/{existing_invitation.token}")
        
        # List all users and invitations
        print("\n--- All Users ---")
        users = User.query.all()
        for user in users:
            print(f"  - {user.username} ({user.email}) - Admin: {user.is_admin}")
        
        print("\n--- All Invitations ---")
        invitations = CollectionInvitation.query.all()
        for inv in invitations:
            print(f"  - {inv.email} to '{inv.collection.name}' (Token: {inv.token[:8]}...) - Accepted: {inv.accepted_at is not None}")

if __name__ == '__main__':
    create_test_invitation()
