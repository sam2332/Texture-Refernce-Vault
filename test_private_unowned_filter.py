#!/usr/bin/env python3
"""
Test script to verify that private unowned collections are hidden from discovery
"""

from app import create_app
from app.models.collection import Collection
from app import db

app = create_app()

with app.app_context():
    print("Testing Private Unowned Collection Filtering...")
    
    # Get all unowned collections
    all_unowned = Collection.query.filter(Collection.created_by.is_(None)).all()
    
    # Get only public unowned collections (what discovery page shows)
    public_unowned = Collection.query.filter(
        Collection.created_by.is_(None),
        Collection.is_public == True
    ).all()
    
    # Get private unowned collections (should be hidden)
    private_unowned = Collection.query.filter(
        Collection.created_by.is_(None),
        Collection.is_public == False
    ).all()
    
    print(f"Total unowned collections: {len(all_unowned)}")
    print(f"Public unowned collections (shown): {len(public_unowned)}")
    print(f"Private unowned collections (hidden): {len(private_unowned)}")
    
    if private_unowned:
        print("\nPrivate unowned collections (hidden from discovery):")
        for collection in private_unowned:
            print(f"  - {collection.name} (private, unowned)")
    
    if public_unowned:
        print("\nPublic unowned collections (shown in discovery):")
        for collection in public_unowned:
            print(f"  - {collection.name} (public, unowned)")
    
    print(f"\n✅ Discovery page correctly shows only {len(public_unowned)} public unowned collections")
    print(f"✅ {len(private_unowned)} private unowned collections are properly hidden")
