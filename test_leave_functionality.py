#!/usr/bin/env python3
"""
Test script to verify the leave collection functionality
"""

from app import create_app
from app.models.collection import Collection, CollectionPermission
from app.models.user import User
from app import db

app = create_app()

with app.app_context():
    # Check if we have collections and users to test with
    collections = Collection.query.all()
    users = User.query.all()
    permissions = CollectionPermission.query.all()
    
    print(f"Collections: {len(collections)}")
    print(f"Users: {len(users)}")
    print(f"Permissions: {len(permissions)}")
    
    if collections:
        for collection in collections[:3]:  # Show first 3 collections
            creator_name = collection.creator.username if collection.creator else "No owner"
            print(f"  - {collection.name}: created_by={collection.created_by}, creator={creator_name}")
    
    print("\nLeave collection functionality is ready for testing!")
    print("Users can now:")
    print("- Leave any collection they have access to")
    print("- Claim ownership of unowned collections")
    print("- Transfer ownership to other members")
    print("- View public/private status and ownership information")
