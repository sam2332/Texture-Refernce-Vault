#!/usr/bin/env python3
"""
Test script to verify that image data field functionality works correctly
"""

from app import create_app, db
from app.models.image import TextureImage, ImageVersion
from app.models.collection import Collection
from app.models.user import User
import os

def test_image_data():
    app = create_app()
    with app.app_context():
        # Create a test user if none exists
        user = User.query.first()
        if not user:
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            print("Created test user")
        
        # Create a test collection if none exists
        collection = Collection.query.first()
        if not collection:
            collection = Collection(
                name='Test Collection',
                description='Test collection for image data testing',
                created_by=user.id
            )
            db.session.add(collection)
            db.session.commit()
            print("Created test collection")
        
        # Test creating an image with data
        test_data = b"fake image data for testing"
        
        # Create image record
        image = TextureImage(
            filename='test_image.jpg',
            original_filepath='/path/to/test_image.jpg',
            current_filepath='/uploads/test_image.jpg',
            width=1920,
            height=1080,
            file_size=len(test_data),
            collection_id=collection.id,
            uploaded_by=user.id
        )
        
        db.session.add(image)
        db.session.commit()
        print(f"Created test image with ID: {image.id}")
        
        # Create version with data
        version = ImageVersion(
            image_id=image.id,
            version_number=1,
            filepath='/uploads/test_image.jpg',
            uploaded_by=user.id,
            data=test_data,
            is_current=True
        )
        
        db.session.add(version)
        db.session.commit()
        print(f"Created test version with ID: {version.id}")
        
        # Verify data was stored correctly
        stored_version = ImageVersion.query.get(version.id)
        if stored_version.data == test_data:
            print("✓ Image data stored and retrieved correctly!")
        else:
            print("✗ Image data not stored correctly")
        
        print(f"Data length: {len(stored_version.data)} bytes")
        
        # Clean up test data
        db.session.delete(version)
        db.session.delete(image)
        db.session.commit()
        print("Cleaned up test data")

if __name__ == '__main__':
    test_image_data()
