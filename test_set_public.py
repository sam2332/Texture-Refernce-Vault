#!/usr/bin/env python3
"""
Test script to set a collection as public for testing purposes
"""

from app import create_app
from app.models.collection import Collection
from app import db

app = create_app()

with app.app_context():
    # Get the first collection and make it public
    collection = Collection.query.first()
    if collection:
        collection.is_public = True
        db.session.commit()
        print(f"Set '{collection.name}' to public for testing")
    else:
        print("No collections found")
