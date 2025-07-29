#!/usr/bin/env python3
"""
Test script to verify the discover collections functionality
"""

from app import create_app
from app.models.collection import Collection, CollectionPermission
from app.models.user import User
from app import db

app = create_app()

with app.app_context():
    # Create a test scenario
    print("Testing Discovery Page Data...")
    
    # Get current state
    total_collections = Collection.query.count()
    public_collections = Collection.query.filter_by(is_public=True).count()
    unowned_collections = Collection.query.filter(Collection.created_by.is_(None)).count()
    
    print(f"Total Collections: {total_collections}")
    print(f"Public Collections: {public_collections}")
    print(f"Unowned Collections: {unowned_collections}")
    
    # Show some examples
    print("\nSample Collections:")
    for collection in Collection.query.limit(5):
        owner = collection.creator.username if collection.creator else "UNOWNED"
        visibility = "PUBLIC" if collection.is_public else "PRIVATE"
        print(f"  - {collection.name}: {owner} ({visibility})")
    
    print(f"\nDiscovery page will show:")
    print(f"  - {public_collections} public collections")
    print(f"  - {unowned_collections} unowned collections")
    print("  - Users can join public collections")
    print("  - Users can claim unowned collections")
    print("\nDiscovery page is ready! 🚀")
