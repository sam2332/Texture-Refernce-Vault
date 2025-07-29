#!/usr/bin/env python3
"""
Quick test script to verify database models and connections work correctly
before running the full population script.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Collection, CollectionPermission, TextureImage, ImageVersion, CollectionInvitation

def test_database_setup():
    """Test that database setup and models work correctly"""
    app = create_app('development')
    
    with app.app_context():
        print("Testing database setup...")
        
        # Test creating tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Test creating a user
        test_user = User(
            username='test_user',
            email='test@example.com',
            is_admin=False
        )
        test_user.set_password('test123')
        
        db.session.add(test_user)
        db.session.commit()
        print("✓ User creation successful")
        
        # Test creating a collection
        test_collection = Collection(
            name='Test Collection',
            description='A test collection',
            created_by=test_user.id
        )
        
        db.session.add(test_collection)
        db.session.commit()
        print("✓ Collection creation successful")
        
        # Test creating an image with version
        test_image = TextureImage(
            filename='test_texture.png',
            original_filepath='/test/path/test_texture.png',
            width=512,
            height=512,
            file_size=1024000,
            collection_id=test_collection.id,
            uploaded_by=test_user.id
        )
        
        db.session.add(test_image)
        db.session.flush()  # Get the ID
        
        # Create a test version with dummy binary data
        test_version = ImageVersion(
            image_id=test_image.id,
            version_number=1,
            filepath='uploads/test_texture_v1.png',
            uploaded_by=test_user.id,
            is_current=True,
            data=b'dummy_image_data_for_testing'
        )
        
        db.session.add(test_version)
        db.session.commit()
        print("✓ Image and version creation successful")
        
        # Test permissions
        test_permission = CollectionPermission(
            user_id=test_user.id,
            collection_id=test_collection.id,
            permission_level='write'
        )
        
        db.session.add(test_permission)
        db.session.commit()
        print("✓ Permission creation successful")
        
        # Test invitation
        test_invitation = CollectionInvitation(
            collection_id=test_collection.id,
            invited_by=test_user.id,
            email='invited@example.com',
            permission_level='read'
        )
        
        db.session.add(test_invitation)
        db.session.commit()
        print("✓ Invitation creation successful")
        
        # Test relationships
        user_collections = test_user.created_collections
        collection_images = test_collection.images
        image_versions = test_image.versions
        
        print(f"✓ User has {len(user_collections)} collections")
        print(f"✓ Collection has {len(collection_images)} images")  
        print(f"✓ Image has {len(image_versions)} versions")
        
        # Clean up test data
        db.session.delete(test_invitation)
        db.session.delete(test_permission)
        db.session.delete(test_version)
        db.session.delete(test_image)
        db.session.delete(test_collection)
        db.session.delete(test_user)
        db.session.commit()
        print("✓ Test cleanup successful")
        
        print("\n🎉 All database tests passed! Ready to run population script.")
        return True

if __name__ == '__main__':
    try:
        test_database_setup()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
