#!/usr/bin/env python3
"""
Collection Import Tool for Texture Reference Vault

This command-line tool imports image files from a folder into a new unowned private collection.
The specified user becomes the owner of the collection.

Only processes image files with supported formats (PNG, JPEG, GIF, BMP, TIFF, WEBP).
Automatically skips folders: .git, node_modules, Game Source, Game XML

Usage: python import_collection.py [options]
"""
import os
import sys
import argparse
import uuid
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Collection, CollectionPermission, TextureImage, ImageVersion

class CollectionImporter:
    """Main class for importing collections from folders
    
    Only imports image files with supported formats.
    Automatically skips: .git, node_modules, Game Source, Game XML folders
    """
    
    def __init__(self, app):
        self.app = app
        self.supported_formats = {
            '.png': 'PNG',
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.gif': 'GIF',
            '.bmp': 'BMP',
            '.tiff': 'TIFF',
            '.tif': 'TIFF',
            '.webp': 'WEBP'
        }
        self.stats = {
            'files_processed': 0,
            'files_imported': 0,
            'files_skipped': 0,
            'total_size': 0,
            'errors': []
        }
    
    def get_image_info(self, filepath):
        """Extract image information using PIL"""
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                format_type = img.format or 'UNKNOWN'
                
                # Get file size
                file_size = os.path.getsize(filepath)
                
                return {
                    'width': width,
                    'height': height,
                    'format': format_type,
                    'file_size': file_size
                }
        except Exception as e:
            return None
    
    def read_image_as_binary(self, filepath):
        """Read image file as binary data"""
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Error reading file {filepath}: {e}")
            return None
    
    def create_collection(self, name, description, owner_username):
        """Create a new collection and assign ownership"""
        try:
            # Find the user
            owner = User.query.filter_by(username=owner_username).first()
            if not owner:
                print(f"❌ User '{owner_username}' not found!")
                return None
            
            # Create collection as unowned initially
            collection = Collection(
                name=name,
                description=description,
                created_by=None,  # Unowned initially
                created_at=datetime.utcnow(),
                is_public=False  # Private collection
            )
            
            db.session.add(collection)
            db.session.flush()  # Get the collection ID
            
            # Add owner permission
            permission = CollectionPermission(
                user_id=owner.id,
                collection_id=collection.id,
                permission_level='admin'
            )
            
            db.session.add(permission)
            db.session.commit()
            
            print(f"✅ Created collection '{name}' with owner '{owner_username}'")
            return collection
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            db.session.rollback()
            return None
    
    def import_image(self, filepath, collection, owner_user):
        """Import a single image file into the collection"""
        self.stats['files_processed'] += 1
        
        try:
            # Check if file extension is supported
            file_ext = Path(filepath).suffix.lower()
            if file_ext not in self.supported_formats:
                print(f"⏭️  Skipping unsupported file: {filepath}")
                self.stats['files_skipped'] += 1
                return False
            
            # Get image information
            image_info = self.get_image_info(filepath)
            if not image_info:
                print(f"⚠️  Cannot read image info for: {filepath}")
                self.stats['files_skipped'] += 1
                self.stats['errors'].append(f"Cannot read image info: {filepath}")
                return False
            
            # Read binary data
            binary_data = self.read_image_as_binary(filepath)
            if not binary_data:
                print(f"⚠️  Cannot read binary data for: {filepath}")
                self.stats['files_skipped'] += 1
                self.stats['errors'].append(f"Cannot read binary data: {filepath}")
                return False
            
            # Get file info
            filename = Path(filepath).name
            modification_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Create TextureImage record
            texture_image = TextureImage(
                filename=filename,
                original_filepath=str(filepath),
                current_filepath=None,  # Will be set when we create the version
                width=image_info['width'],
                height=image_info['height'],
                file_size=image_info['file_size'],
                modification_date=modification_time,
                collection_id=collection.id,
                uploaded_by=owner_user.id,
                created_at=datetime.utcnow(),
                is_published=False
            )
            
            db.session.add(texture_image)
            db.session.flush()  # Get the image ID
            
            # Create version with binary data
            uuid_prefix = str(uuid.uuid4())[:8]
            version_filename = f"{uuid_prefix}_{filename}"
            version_filepath = f"uploads/{version_filename}"
            
            image_version = ImageVersion(
                image_id=texture_image.id,
                version_number=1,
                filepath=version_filepath,
                uploaded_by=owner_user.id,
                uploaded_at=datetime.utcnow(),
                is_current=True,
                data=binary_data
            )
            
            # Update the current filepath in the image
            texture_image.current_filepath = version_filepath
            
            db.session.add(image_version)
            db.session.commit()
            
            self.stats['files_imported'] += 1
            self.stats['total_size'] += len(binary_data)
            
            print(f"✅ Imported: {filename} ({image_info['width']}x{image_info['height']}, {len(binary_data)/1024:.1f}KB)")
            return True
            
        except Exception as e:
            print(f"❌ Error importing {filepath}: {e}")
            self.stats['errors'].append(f"Import error for {filepath}: {e}")
            db.session.rollback()
            return False
    
    def scan_folder(self, folder_path, recursive=True):
        """Scan folder for image files"""
        image_files = []
        folder = Path(folder_path)
        
        # Folders to skip during scanning
        skip_folders = {'.git', 'node_modules', 'Game Source', 'Game XML',".venv", "venv", "__pycache__"}
        
        if not folder.exists():
            print(f"❌ Folder does not exist: {folder_path}")
            return []
        
        if not folder.is_dir():
            print(f"❌ Path is not a directory: {folder_path}")
            return []
        
        print(f"🔍 Scanning folder: {folder_path}")
        print(f"⏭️  Skipping folders: {', '.join(skip_folders)}")
        
        # Collect image files
        if recursive:
            # Use os.walk for better control over directory traversal
            for root, dirs, files in os.walk(folder):
                # Remove skip folders from dirs list to prevent traversing them
                dirs[:] = [d for d in dirs if d not in skip_folders]
                
                for file in files:
                    filepath = Path(root) / file
                    file_ext = filepath.suffix.lower()
                    if file_ext in self.supported_formats:
                        image_files.append(filepath)
        else:
            # Non-recursive: only scan direct files in the folder
            for filepath in folder.iterdir():
                if filepath.is_file():
                    file_ext = filepath.suffix.lower()
                    if file_ext in self.supported_formats:
                        image_files.append(filepath)
        
        print(f"📁 Found {len(image_files)} image files")
        
        # Show file types breakdown
        if image_files:
            file_types = {}
            for filepath in image_files:
                ext = filepath.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            print("📊 File types found:")
            for ext, count in sorted(file_types.items()):
                print(f"   {ext}: {count} files")
        
        return image_files
    
    def import_folder(self, folder_path, collection_name, collection_description, owner_username, recursive=True, auto_yes=False):
        """Import all images from a folder into a new collection"""
        
        print("=" * 60)
        print("TEXTURE REFERENCE VAULT - COLLECTION IMPORT")
        print("=" * 60)
        print(f"📁 Source folder: {folder_path}")
        print(f"📋 Collection name: {collection_name}")
        print(f"👤 Owner: {owner_username}")
        print(f"🔄 Recursive: {recursive}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Verify user exists
            owner = User.query.filter_by(username=owner_username).first()
            if not owner:
                print(f"❌ User '{owner_username}' not found!")
                print("\nAvailable users:")
                users = User.query.all()
                for user in users[:10]:  # Show first 10 users
                    print(f"   - {user.username}")
                if len(users) > 10:
                    print(f"   ... and {len(users) - 10} more")
                return False
            
            # Scan for image files
            image_files = self.scan_folder(folder_path, recursive)
            if not image_files:
                print("❌ No image files found to import!")
                return False
            
            # Confirm import
            print(f"\n📝 Ready to import {len(image_files)} files")
            if not self.confirm_import(auto_yes):
                print("❌ Import cancelled by user")
                return False
            
            # Create collection
            collection = self.create_collection(collection_name, collection_description, owner_username)
            if not collection:
                return False
            
            # Import images
            print(f"\n📤 Starting import of {len(image_files)} files...")
            
            for i, filepath in enumerate(image_files, 1):
                print(f"\n[{i}/{len(image_files)}] Processing: {filepath.name}")
                self.import_image(filepath, collection, owner)
                
                # Show progress every 10 files
                if i % 10 == 0:
                    progress = (i / len(image_files)) * 100
                    print(f"📈 Progress: {progress:.1f}% ({i}/{len(image_files)} files)")
            
            # Final statistics
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "=" * 60)
            print("IMPORT COMPLETE!")
            print("=" * 60)
            print(f"⏱️  Time taken: {duration}")
            print(f"📁 Collection: {collection.name} (ID: {collection.id})")
            print(f"📊 Statistics:")
            print(f"   📥 Files processed: {self.stats['files_processed']}")
            print(f"   ✅ Files imported: {self.stats['files_imported']}")
            print(f"   ⏭️  Files skipped: {self.stats['files_skipped']}")
            print(f"   💾 Total data size: {self.stats['total_size'] / (1024*1024):.1f}MB")
            
            if self.stats['errors']:
                print(f"   ⚠️  Errors: {len(self.stats['errors'])}")
                print("\n❌ Errors encountered:")
                for error in self.stats['errors'][:5]:  # Show first 5 errors
                    print(f"   - {error}")
                if len(self.stats['errors']) > 5:
                    print(f"   ... and {len(self.stats['errors']) - 5} more errors")
            
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Fatal error during import: {e}")
            return False
    
    def confirm_import(self, auto_yes=False):
        """Ask user to confirm the import operation"""
        if auto_yes:
            print("Auto-confirming import (--yes flag used)")
            return True
            
        try:
            response = input("\nProceed with import? (y/N): ").strip().lower()
            return response in ['y', 'yes']
        except KeyboardInterrupt:
            print("\n❌ Import cancelled")
            return False

def main():
    """Main function - parse arguments and run import"""
    parser = argparse.ArgumentParser(
        description="Import a folder of images into a new private collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import folder with basic options
  python import_collection.py --folder "C:/textures/wood" --name "Wood Textures" --owner admin_1

  # Import with custom description and non-recursive scan
  python import_collection.py --folder "./images" --name "My Collection" --owner john_doe --description "Custom texture pack" --no-recursive

  # List available users
  python import_collection.py --list-users
        """
    )
    
    parser.add_argument('--folder', '-f', 
                       help='Path to folder containing images to import')
    parser.add_argument('--name', '-n', 
                       help='Name for the new collection')
    parser.add_argument('--owner', '-o', 
                       help='Username of the collection owner')
    parser.add_argument('--description', '-d', 
                       help='Description for the collection (optional)',
                       default='')
    parser.add_argument('--no-recursive', 
                       action='store_true',
                       help='Do not scan subfolders recursively')
    parser.add_argument('--list-users', 
                       action='store_true',
                       help='List available users and exit')
    parser.add_argument('--yes', '-y',
                       action='store_true',
                       help='Skip confirmation prompt and proceed automatically')
    
    args = parser.parse_args()
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        # List users if requested
        if args.list_users:
            print("Available users:")
            users = User.query.all()
            for user in users:
                admin_status = " (Admin)" if user.is_admin else ""
                print(f"  - {user.username}{admin_status}")
            return
        
        # Validate required arguments
        if not all([args.folder, args.name, args.owner]):
            print("❌ Missing required arguments!")
            print("Required: --folder, --name, --owner")
            print("Use --help for more information")
            return
        
        # Validate folder path
        folder_path = Path(args.folder).resolve()
        if not folder_path.exists():
            print(f"❌ Folder does not exist: {folder_path}")
            return
        
        # Create importer and run
        importer = CollectionImporter(app)
        success = importer.import_folder(
            folder_path=folder_path,
            collection_name=args.name,
            collection_description=args.description,
            owner_username=args.owner,
            recursive=not args.no_recursive,
            auto_yes=args.yes
        )
        
        if success:
            print("\n🎉 Import completed successfully!")
        else:
            print("\n💥 Import failed!")
            sys.exit(1)

if __name__ == '__main__':
    main()
