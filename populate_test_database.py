#!/usr/bin/env python3
"""
Complex Testing Script for Texture Reference Vault Database Population

This script creates:
- 100-500 users with varied profiles
- 50-150 collections per user (distributed)
- 15-25 images per collection
- 2-8 versions per image
- Realistic permission structures
- Sample binary image data for testing

Run with: python populate_test_database.py
"""
import os
import sys
import random
import uuid
import time
import threading
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
from faker import Faker

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Collection, CollectionPermission, TextureImage, ImageVersion, CollectionInvitation

fake = Faker()

class ProgressTracker:
    """Enhanced progress tracking with real-time feedback"""
    
    def __init__(self):
        self.start_time = None
        self.current_operation = ""
        self.current_progress = 0
        self.total_progress = 0
        self.last_update_time = 0
        self.update_interval = 0.5  # Update every 500ms
        
    def start_operation(self, operation_name, total_items):
        """Start tracking a new operation"""
        self.current_operation = operation_name
        self.current_progress = 0
        self.total_progress = total_items
        self.start_time = time.time()
        self.last_update_time = 0
        print(f"\n🚀 Starting: {operation_name}")
        print(f"📊 Target: {total_items} items")
        self._update_progress()
        
    def update_progress(self, increment=1):
        """Update progress counter"""
        self.current_progress += increment
        current_time = time.time()
        
        # Update display every update_interval seconds
        if current_time - self.last_update_time >= self.update_interval:
            self._update_progress()
            self.last_update_time = current_time
            
    def _update_progress(self):
        """Display current progress"""
        if self.total_progress == 0:
            return
            
        percentage = (self.current_progress / self.total_progress) * 100
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        # Calculate ETA
        if self.current_progress > 0 and elapsed_time > 0:
            rate = self.current_progress / elapsed_time
            remaining_items = self.total_progress - self.current_progress
            eta_seconds = remaining_items / rate if rate > 0 else 0
            eta_str = f" | ETA: {self._format_time(eta_seconds)}"
        else:
            eta_str = ""
            
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Format the output
        rate_str = f"{self.current_progress/elapsed_time:.1f}/s" if elapsed_time > 0 else "calculating..."
        
        print(f"\r📈 {self.current_operation}: [{bar}] {percentage:.1f}% " +
              f"({self.current_progress}/{self.total_progress}) | " +
              f"Rate: {rate_str}{eta_str}", end="", flush=True)
              
    def finish_operation(self):
        """Complete the current operation"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        print(f"\n✅ Completed: {self.current_operation}")
        print(f"⏱️  Time taken: {self._format_time(elapsed_time)}")
        print(f"📊 Items created: {self.current_progress}")
        if elapsed_time > 0:
            print(f"⚡ Average rate: {self.current_progress/elapsed_time:.2f} items/second")
        print("-" * 60)
        
    def _format_time(self, seconds):
        """Format time in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds//60:.0f}m {seconds%60:.0f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"

class MemoryMonitor:
    """Monitor memory usage during database population"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start memory monitoring in background thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Background monitoring loop"""
        try:
            import psutil
            process = psutil.Process()
            while self.monitoring:
                memory_mb = process.memory_info().rss / 1024 / 1024
                if memory_mb > 500:  # Alert if over 500MB
                    print(f"\n⚠️  Memory usage: {memory_mb:.1f}MB")
                time.sleep(5)
        except ImportError:
            pass  # psutil not available

class DatabasePopulator:
    def __init__(self, app):
        self.app = app
        self.users = []
        self.collections = []
        self.images = []
        self.progress = ProgressTracker()
        self.memory_monitor = MemoryMonitor()
        self.stats = {
            'users_created': 0,
            'collections_created': 0,
            'images_created': 0,
            'versions_created': 0,
            'permissions_created': 0,
            'invitations_created': 0,
            'total_data_size': 0
        }
        
        self.image_formats = ['PNG', 'JPEG', 'WEBP', 'BMP']
        self.texture_types = [
            'wood', 'metal', 'fabric', 'stone', 'concrete', 'leather', 'plastic',
            'glass', 'paper', 'marble', 'brick', 'tile', 'grass', 'sand', 'water',
            'rust', 'scratched', 'weathered', 'polished', 'rough', 'smooth'
        ]
        
    def print_stats_update(self, operation=""):
        """Print current statistics"""
        print(f"\n📈 CURRENT STATISTICS {operation}")
        print("=" * 50)
        print(f"👥 Users: {self.stats['users_created']}")
        print(f"📁 Collections: {self.stats['collections_created']}")
        print(f"🖼️  Images: {self.stats['images_created']}")
        print(f"🔄 Versions: {self.stats['versions_created']}")
        print(f"🔐 Permissions: {self.stats['permissions_created']}")
        print(f"📧 Invitations: {self.stats['invitations_created']}")
        print(f"💾 Data Size: {self.stats['total_data_size'] / (1024*1024):.1f}MB")
        print("=" * 50)
        
    def create_sample_image(self, width=512, height=512, format='PNG', texture_type='wood', version=1):
        """Create a sample image with text and patterns for testing"""
        # Create image with random colors
        bg_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add some pattern/texture simulation
        for _ in range(random.randint(100, 500)):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = (
                random.randint(max(0, bg_color[0] - 50), min(255, bg_color[0] + 50)),
                random.randint(max(0, bg_color[1] - 50), min(255, bg_color[1] + 50)),
                random.randint(max(0, bg_color[2] - 50), min(255, bg_color[2] + 50))
            )
            draw.line([x1, y1, x2, y2], fill=color, width=random.randint(1, 3))
        
        # Add text overlay
        try:
            # Try to use default font, fall back to basic if not available
            font_size = random.randint(20, 40)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", font_size)
            except:
                font = ImageFont.load_default()
        except:
            font = None
            
        text = f"{texture_type.upper()}\nv{version}\n{width}x{height}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        # Add text with outline
        outline_color = (255, 255, 255) if sum(bg_color) < 400 else (0, 0, 0)
        text_color = (0, 0, 0) if sum(bg_color) < 400 else (255, 255, 255)
        
        # Draw outline
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((text_x + dx, text_y + dy), text, fill=outline_color, font=font)
        
        # Draw main text
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    def create_users(self, count=300):
        """Create realistic users with varied profiles - use existing users if they exist"""
        print(f"\n🔧 PHASE 1: USER CREATION")
        print(f"🎯 Target: {count} users")
        
        # First, load existing users from database
        existing_users = User.query.all()
        print(f"📋 Found {len(existing_users)} existing users in database")
        
        # Add existing users to our list
        for user in existing_users:
            self.users.append(user)
        
        self.progress.start_operation("Creating Users", count)
        self.memory_monitor.start_monitoring()
        
        batch_size = 50
        current_batch = []
        
        # Calculate how many more users we need
        users_needed = max(0, count - len(existing_users))
        print(f"📝 Need to create {users_needed} additional users")
        
        if users_needed == 0:
            print(f"✅ Already have enough users ({len(existing_users)} >= {count})")
            self.progress.finish_operation()
            self.memory_monitor.stop_monitoring()
            self.stats['users_created'] = len(existing_users)
            self.print_stats_update("using existing users")
            return
        
        # Create admin users if needed
        existing_admin_count = len([u for u in existing_users if u.is_admin])
        target_admin_count = max(1, count // 50)  # 2% admin users
        admin_needed = max(0, target_admin_count - existing_admin_count)
        
        print(f"👑 Creating {admin_needed} additional admin users...")
        
        for i in range(admin_needed):
            # Find next available admin username
            admin_num = existing_admin_count + i + 1
            username = f"admin_{admin_num}"
            email = f"{username}@textureref.com"
            
            # Check if username/email already exists
            while (any(u.username == username for u in self.users) or 
                   any(u.email == email for u in self.users)):
                admin_num += 1
                username = f"admin_{admin_num}"
                email = f"{username}@textureref.com"
            
            user = User(
                username=username,
                email=email,
                is_admin=True,
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            user.set_password('admin123')
            current_batch.append(user)
            self.users.append(user)
            self.progress.update_progress()
            
            # Commit in batches for memory efficiency
            if len(current_batch) >= batch_size:
                try:
                    db.session.add_all(current_batch)
                    db.session.commit()
                    self.stats['users_created'] += len(current_batch)
                    current_batch = []
                except Exception as e:
                    print(f"⚠️  Error creating admin users: {e}")
                    db.session.rollback()
                    current_batch = []
                
        print(f"\n👥 Creating {users_needed - admin_needed} additional regular users...")
            
        # Create regular users
        regular_needed = users_needed - admin_needed
        for i in range(regular_needed):
            # Generate realistic usernames
            username_styles = [
                lambda: fake.user_name(),
                lambda: f"{fake.first_name().lower()}{fake.last_name().lower()}",
                lambda: f"{fake.first_name().lower()}_{fake.random_int(100, 9999)}",
                lambda: f"{fake.word()}_{fake.word()}_{fake.random_int(10, 999)}",
                lambda: f"texture_artist_{fake.random_int(1000, 9999)}"
            ]
            
            username = random.choice(username_styles)()
            email = fake.email()
            
            # Ensure username and email are unique
            attempt_count = 0
            while ((any(u.username == username for u in self.users) or 
                    any(u.email == email for u in self.users)) and attempt_count < 20):
                username = random.choice(username_styles)()
                email = fake.email()
                attempt_count += 1
                
            if attempt_count >= 20:
                username = f"user_{fake.random_int(10000, 99999)}"
                email = f"{username}@example.com"
                
            user = User(
                username=username,
                email=email,
                is_admin=False,
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            user.set_password('password123')
            current_batch.append(user)
            self.users.append(user)
            self.progress.update_progress()
            
            # Commit in batches
            if len(current_batch) >= batch_size:
                try:
                    db.session.add_all(current_batch)
                    db.session.commit()
                    self.stats['users_created'] += len(current_batch)
                    current_batch = []
                    
                    # Print intermediate stats every 100 users
                    if self.stats['users_created'] % 100 == 0:
                        print(f"\n✨ Milestone: {self.stats['users_created']} users processed!")
                        
                except Exception as e:
                    print(f"⚠️  Error creating regular users: {e}")
                    db.session.rollback()
                    current_batch = []
                    
        # Commit remaining users
        if current_batch:
            try:
                db.session.add_all(current_batch)
                db.session.commit()
                self.stats['users_created'] += len(current_batch)
            except Exception as e:
                print(f"⚠️  Error committing final users: {e}")
                db.session.rollback()
            
        self.progress.finish_operation()
        self.memory_monitor.stop_monitoring()
        
        total_admin_count = len([u for u in self.users if u.is_admin])
        total_regular_count = len([u for u in self.users if not u.is_admin])
        
        print(f"✅ User setup complete!")
        print(f"📊 Total: {len(self.users)} users ({total_admin_count} admins, {total_regular_count} regular)")
        print(f"📋 Used {len(existing_users)} existing users, created {users_needed} new users")
        self.print_stats_update("after user creation")

    def create_collections(self, min_per_user=1, max_per_user=5, total_collections=800):
        """Create collections with realistic distribution - use existing collections if they exist"""
        print(f"\n🔧 PHASE 2: COLLECTION CREATION")
        print(f"🎯 Target: {total_collections} collections")
        
        # First, load existing collections from database
        existing_collections = Collection.query.all()
        print(f"📋 Found {len(existing_collections)} existing collections in database")
        
        # Add existing collections to our list
        for collection in existing_collections:
            self.collections.append(collection)
        
        self.progress.start_operation("Creating Collections", total_collections)
        self.memory_monitor.start_monitoring()
        
        # Calculate how many more collections we need
        collections_needed = max(0, total_collections - len(existing_collections))
        print(f"📝 Need to create {collections_needed} additional collections")
        
        if collections_needed == 0:
            print(f"✅ Already have enough collections ({len(existing_collections)} >= {total_collections})")
            self.progress.finish_operation()
            self.memory_monitor.stop_monitoring()
            self.stats['collections_created'] = len(existing_collections)
            self.print_stats_update("using existing collections")
            return
        
        collection_themes = [
            ("Wood Textures", "High-quality wood grain textures for 3D modeling"),
            ("Metal Surfaces", "Various metal textures including rust, polish, and weathered"),
            ("Fabric Materials", "Textile patterns and fabric textures"),
            ("Stone & Rock", "Natural stone textures and rock formations"),
            ("Urban Materials", "Concrete, asphalt, and urban surface textures"),
            ("Organic Textures", "Natural organic materials and surfaces"),
            ("Fantasy Materials", "Stylized and fantasy texture collections"),
            ("Sci-Fi Surfaces", "Futuristic and technological surface textures"),
            ("Architectural", "Building materials and architectural textures"),
            ("Game Assets", "Optimized textures for game development"),
            ("Film & VFX", "High-resolution textures for film production"),
            ("Seamless Patterns", "Tileable texture patterns"),
            ("Weathered Materials", "Aged and weathered surface textures"),
            ("Abstract Textures", "Artistic and abstract surface patterns"),
            ("Nature Pack", "Natural environment textures")
        ]
        
        collections_created = 0
        target_per_user = collections_needed // len(self.users)
        batch_size = 25
        current_batch = []
        
        print(f"📊 Distribution: ~{target_per_user} new collections per user")
        
        for user_idx, user in enumerate(self.users):
            # Print progress every 50 users
            if user_idx % 50 == 0 and user_idx > 0:
                print(f"\n🔄 Processing user {user_idx}/{len(self.users)}")
                print(f"📈 Collections created so far: {collections_created}")
                
            # Calculate remaining collections and users to ensure fair distribution
            remaining_collections = collections_needed - collections_created
            remaining_users = len(self.users) - user_idx
            
            if remaining_users <= 0:
                break
                
            # Ensure each remaining user gets at least min_per_user collections
            max_for_this_user = min(
                remaining_collections - (remaining_users - 1) * min_per_user,
                max_per_user * (2 if user.is_admin else 1)
            )
            min_for_this_user = min(min_per_user, remaining_collections)
            
            # Vary collections per user with better distribution
            if max_for_this_user > min_for_this_user:
                num_collections = random.randint(min_for_this_user, max_for_this_user)
            else:
                num_collections = min_for_this_user
            
            print(f"👤 User {user.username}: planning {num_collections} collections (remaining: {remaining_collections})")
            
            user_collections_created = 0
            for _ in range(num_collections):
                if collections_created >= collections_needed:
                    break
                    
                theme_name, theme_desc = random.choice(collection_themes)
                
                # Add variation to collection names
                variations = [
                    f"{theme_name}",
                    f"{theme_name} - {fake.word().title()} Edition",
                    f"Professional {theme_name}",
                    f"{theme_name} Pack v{random.randint(1, 3)}",
                    f"{fake.company()} {theme_name}",
                    f"{theme_name} - {fake.color_name().title()} Series"
                ]
                
                collection_name = random.choice(variations)
                
                # Ensure unique name with fallback
                attempt_count = 0
                while any(c.name == collection_name for c in self.collections) and attempt_count < 10:
                    collection_name = f"{random.choice(variations)} ({fake.random_int(1, 999)})"
                    attempt_count += 1
                
                if attempt_count >= 10:
                    collection_name = f"{theme_name} {uuid.uuid4().hex[:8]}"
                
                collection = Collection(
                    name=collection_name,
                    description=f"{theme_desc}. {fake.text(max_nb_chars=200)}",
                    created_by=user.id,
                    created_at=fake.date_time_between(
                        start_date=user.created_at, 
                        end_date='now'
                    )
                )
                
                current_batch.append(collection)
                self.collections.append(collection)
                collections_created += 1
                user_collections_created += 1
                self.progress.update_progress()
                
                # Commit in batches
                if len(current_batch) >= batch_size:
                    try:
                        db.session.add_all(current_batch)
                        db.session.commit()
                        
                        # Refresh objects to get IDs
                        for coll in current_batch:
                            db.session.refresh(coll)
                        
                        self.stats['collections_created'] += len(current_batch)
                        current_batch = []
                        
                        # Print milestone updates
                        if self.stats['collections_created'] % 100 == 0:
                            print(f"\n✨ Milestone: {self.stats['collections_created']} collections created!")
                            
                    except Exception as e:
                        print(f"⚠️  Error creating collections: {e}")
                        db.session.rollback()
                        current_batch = []
                
            if collections_created >= collections_needed:
                print(f"\n🎯 Reached target of {collections_needed} new collections!")
                break
        
        # Commit remaining collections
        if current_batch:
            try:
                db.session.add_all(current_batch)
                db.session.commit()
                
                # Refresh objects to get IDs
                for coll in current_batch:
                    db.session.refresh(coll)
                
                self.stats['collections_created'] += len(current_batch)
            except Exception as e:
                print(f"⚠️  Error committing final collections: {e}")
                db.session.rollback()
        
        self.progress.finish_operation()
        self.memory_monitor.stop_monitoring()
        
        print(f"✅ Collection setup complete!")
        print(f"📊 Total: {len(self.collections)} collections")
        print(f"📋 Used {len(existing_collections)} existing collections, created {collections_created} new collections")
        self.print_stats_update("after collection creation")

    def create_collection_permissions(self):
        """Create realistic permission structures between users and collections"""
        print(f"\n🔧 PHASE 3: PERMISSION CREATION")
        
        total_possible_permissions = len(self.collections) * len(self.users) // 4  # Estimate
        self.progress.start_operation("Creating Permissions", total_possible_permissions)
        
        permissions_created = 0
        batch_size = 100
        current_batch = []
        
        print(f"🔐 Analyzing {len(self.collections)} collections for permission assignment...")
        
        for collection_idx, collection in enumerate(self.collections):
            if collection_idx % 100 == 0 and collection_idx > 0:
                print(f"\n🔄 Processing collection {collection_idx}/{len(self.collections)}")
                print(f"🔐 Permissions created so far: {permissions_created}")
                
            # Skip creator's own collections (they have implicit admin access)
            available_users = [u for u in self.users if u.id != collection.created_by]
            
            # Decide how many users to give permissions to
            permission_probability = random.random()
            
            if permission_probability < 0.3:  # 30% private collections
                num_permissions = 0
                permission_type = "Private"
            elif permission_probability < 0.6:  # 30% small team collections
                num_permissions = random.randint(1, 3)
                permission_type = "Small Team"
            elif permission_probability < 0.85:  # 25% medium team collections
                num_permissions = random.randint(3, 8)
                permission_type = "Medium Team"
            else:  # 15% large shared collections
                num_permissions = random.randint(8, 20)
                permission_type = "Large Shared"
            
            if collection_idx % 200 == 0:
                print(f"📊 Collection '{collection.name[:30]}...' → {permission_type} ({num_permissions} permissions)")
            
            if num_permissions > 0:
                selected_users = random.sample(
                    available_users, 
                    min(num_permissions, len(available_users))
                )
                
                for user in selected_users:
                    # Determine permission level
                    level_rand = random.random()
                    if level_rand < 0.1:  # 10% admin
                        level = 'admin'
                    elif level_rand < 0.4:  # 30% write
                        level = 'write'
                    else:  # 60% read
                        level = 'read'
                    
                    permission = CollectionPermission(
                        user_id=user.id,
                        collection_id=collection.id,
                        permission_level=level
                    )
                    
                    current_batch.append(permission)
                    permissions_created += 1
                    self.progress.update_progress()
                    
                    # Commit in batches
                    if len(current_batch) >= batch_size:
                        db.session.add_all(current_batch)
                        db.session.commit()
                        self.stats['permissions_created'] += len(current_batch)
                        current_batch = []
                        
                        # Print milestone updates
                        if self.stats['permissions_created'] % 500 == 0:
                            print(f"\n✨ Milestone: {self.stats['permissions_created']} permissions created!")
        
        # Commit remaining permissions
        if current_batch:
            db.session.add_all(current_batch)
            db.session.commit()
            self.stats['permissions_created'] += len(current_batch)
            
        self.progress.finish_operation()
        
        print(f"✅ Permission creation complete!")
        print(f"📊 Total: {permissions_created} permissions created")
        
        # Permission distribution analysis
        admin_perms = db.session.query(CollectionPermission).filter_by(permission_level='admin').count()
        write_perms = db.session.query(CollectionPermission).filter_by(permission_level='write').count()
        read_perms = db.session.query(CollectionPermission).filter_by(permission_level='read').count()
        
        print(f"📈 Permission breakdown:")
        print(f"   👑 Admin: {admin_perms}")
        print(f"   ✏️  Write: {write_perms}")
        print(f"   👁️  Read: {read_perms}")
        
        self.print_stats_update("after permission creation")

    def create_images_and_versions(self, min_images=15, max_images=25, min_versions=2, max_versions=8):
        """Create images with multiple versions for each collection"""
        print(f"\n🔧 PHASE 4: IMAGE & VERSION CREATION")
        
        # Calculate totals for progress tracking
        total_images_estimate = len(self.collections) * ((min_images + max_images) // 2)
        total_versions_estimate = total_images_estimate * ((min_versions + max_versions) // 2)
        
        print(f"🎯 Estimated targets:")
        print(f"   🖼️  Images: ~{total_images_estimate}")
        print(f"   🔄 Versions: ~{total_versions_estimate}")
        
        self.progress.start_operation("Creating Images & Versions", total_versions_estimate)
        self.memory_monitor.start_monitoring()
        
        total_images = 0
        total_versions = 0
        batch_size = 10  # Smaller batches due to binary data
        current_batch = []
        
        for collection_idx, collection in enumerate(self.collections):
            if collection_idx % 25 == 0 and collection_idx > 0:
                print(f"\n🔄 Processing collection {collection_idx}/{len(self.collections)}")
                print(f"📊 Progress so far:")
                print(f"   🖼️  Images: {total_images}")
                print(f"   🔄 Versions: {total_versions}")
                print(f"   💾 Data: {self.stats['total_data_size'] / (1024*1024):.1f}MB")
            
            # Determine number of images for this collection
            num_images = random.randint(min_images, max_images)
            
            if collection_idx % 100 == 0:
                print(f"📁 Collection '{collection.name[:40]}...' → {num_images} images")
            
            for image_idx in range(num_images):
                # Generate realistic image metadata
                texture_type = random.choice(self.texture_types)
                base_filename = f"{texture_type}_{fake.word()}_{random.randint(1000, 9999)}"
                
                # Random resolution (power of 2 for textures)
                resolutions = [256, 512, 1024, 2048, 4096]
                weights = [5, 25, 40, 25, 5]  # Favor 1024x1024
                width = height = random.choices(resolutions, weights=weights)[0]
                
                # Sometimes use non-square textures
                if random.random() < 0.2:
                    height = random.choice(resolutions)
                
                # Generate original filepath
                original_filepath = fake.file_path(depth=random.randint(2, 5), extension='png')
                
                # Create the base image
                image = TextureImage(
                    filename=f"{base_filename}.png",
                    original_filepath=original_filepath,
                    current_filepath=None,  # Will be set when published
                    width=width,
                    height=height,
                    file_size=random.randint(100000, 10000000),  # 100KB to 10MB
                    modification_date=fake.date_time_between(
                        start_date=collection.created_at,
                        end_date='now'
                    ),
                    collection_id=collection.id,
                    uploaded_by=collection.created_by,
                    created_at=fake.date_time_between(
                        start_date=collection.created_at,
                        end_date='now'
                    ),
                    is_published=random.choice([True, False])
                )
                
                db.session.add(image)
                db.session.flush()  # Get the image ID
                total_images += 1
                
                # Create multiple versions for this image
                num_versions = random.randint(min_versions, max_versions)
                
                for version_num in range(1, num_versions + 1):
                    # Sometimes different users upload versions
                    if random.random() < 0.3 and collection.permissions:
                        # Find a user with write access
                        write_permissions = [p for p in collection.permissions 
                                           if p.permission_level in ['write', 'admin']]
                        if write_permissions:
                            uploader_id = random.choice(write_permissions).user_id
                        else:
                            uploader_id = collection.created_by
                    else:
                        uploader_id = collection.created_by
                    
                    # Generate version-specific data
                    format_type = random.choice(self.image_formats)
                    
                    # Create binary image data
                    try:
                        image_data = self.create_sample_image(
                            width=width,
                            height=height,
                            format=format_type,
                            texture_type=texture_type,
                            version=version_num
                        )
                        data_size = len(image_data)
                        self.stats['total_data_size'] += data_size
                        
                    except Exception as e:
                        print(f"⚠️  Error creating image data: {e}")
                        # Create minimal fallback data
                        image_data = b"DUMMY_IMAGE_DATA"
                        data_size = len(image_data)
                    
                    # Generate filepath for this version
                    uuid_prefix = str(uuid.uuid4())[:8]
                    version_filename = f"{uuid_prefix}_{base_filename}_v{version_num}.{format_type.lower()}"
                    
                    version = ImageVersion(
                        image_id=image.id,
                        version_number=version_num,
                        filepath=f"uploads/{version_filename}",
                        uploaded_by=uploader_id,
                        uploaded_at=fake.date_time_between(
                            start_date=image.created_at,
                            end_date='now'
                        ),
                        is_current=(version_num == num_versions),  # Latest version is current
                        data=image_data
                    )
                    
                    # Update image's current_filepath if this is the current version
                    if version_num == num_versions:
                        image.current_filepath = f"uploads/{version_filename}"
                    
                    current_batch.append(version)
                    total_versions += 1
                    self.progress.update_progress()
                    
                    # Commit in smaller batches due to binary data
                    if len(current_batch) >= batch_size:
                        db.session.add_all(current_batch)
                        try:
                            db.session.commit()
                            self.stats['versions_created'] += len(current_batch)
                            self.stats['images_created'] = total_images
                            current_batch = []
                            
                            # Print milestone updates
                            if self.stats['versions_created'] % 100 == 0:
                                print(f"\n✨ Milestone: {self.stats['versions_created']} versions created!")
                                print(f"   💾 Data size: {self.stats['total_data_size'] / (1024*1024):.1f}MB")
                                
                        except Exception as e:
                            print(f"⚠️  Database commit error: {e}")
                            db.session.rollback()
                            current_batch = []
                            
                    # Memory management - force garbage collection periodically
                    if total_versions % 200 == 0:
                        import gc
                        gc.collect()
        
        # Commit remaining versions
        if current_batch:
            db.session.add_all(current_batch)
            try:
                db.session.commit()
                self.stats['versions_created'] += len(current_batch)
                self.stats['images_created'] = total_images
            except Exception as e:
                print(f"⚠️  Final commit error: {e}")
                db.session.rollback()
        
        self.progress.finish_operation()
        self.memory_monitor.stop_monitoring()
        
        print(f"✅ Image and version creation complete!")
        print(f"📊 Final totals:")
        print(f"   🖼️  Images: {total_images}")
        print(f"   🔄 Versions: {total_versions}")
        print(f"   💾 Data size: {self.stats['total_data_size'] / (1024*1024):.1f}MB")
        print(f"   📈 Avg versions per image: {total_versions / total_images:.1f}")
        
        self.print_stats_update("after image/version creation")

    def create_invitations(self, num_invitations=50):
        """Create some pending and accepted invitations"""
        print(f"\n🔧 PHASE 5: INVITATION CREATION")
        print(f"🎯 Target: {num_invitations} invitations")
        
        self.progress.start_operation("Creating Invitations", num_invitations)
        
        batch_size = 20
        current_batch = []
        
        for i in range(num_invitations):
            collection = random.choice(self.collections)
            inviter = next(u for u in self.users if u.id == collection.created_by)
            
            # Generate email (sometimes existing user, sometimes external)
            if random.random() < 0.6:  # 60% existing users
                invited_user = random.choice([u for u in self.users if u.id != inviter.id])
                email = invited_user.email
                invitation_type = "Internal"
            else:  # 40% external emails
                email = fake.email()
                invitation_type = "External"
            
            permission_level = random.choice(['read', 'write', 'admin'])
            
            invitation = CollectionInvitation(
                collection_id=collection.id,
                invited_by=inviter.id,
                email=email,
                permission_level=permission_level,
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            
            # Some invitations are accepted
            acceptance_status = "Pending"
            if random.random() < 0.4:  # 40% accepted
                if email in [u.email for u in self.users]:
                    accepter = next(u for u in self.users if u.email == email)
                    invitation.accepted_by = accepter.id
                    invitation.accepted_at = fake.date_time_between(
                        start_date=invitation.created_at,
                        end_date='now'
                    )
                    acceptance_status = "Accepted"
            
            if i % 10 == 0:
                print(f"📧 Invitation {i+1}: {invitation_type} → {permission_level} → {acceptance_status}")
            
            current_batch.append(invitation)
            self.progress.update_progress()
            
            # Commit in batches
            if len(current_batch) >= batch_size:
                db.session.add_all(current_batch)
                db.session.commit()
                self.stats['invitations_created'] += len(current_batch)
                current_batch = []
        
        # Commit remaining invitations
        if current_batch:
            db.session.add_all(current_batch)
            db.session.commit()
            self.stats['invitations_created'] += len(current_batch)
        
        self.progress.finish_operation()
        
        # Analyze invitation statistics
        total_invites = db.session.query(CollectionInvitation).count()
        accepted_invites = db.session.query(CollectionInvitation).filter(
            CollectionInvitation.accepted_at.isnot(None)
        ).count()
        pending_invites = total_invites - accepted_invites
        
        print(f"✅ Invitation creation complete!")
        print(f"📊 Invitation breakdown:")
        print(f"   📧 Total: {total_invites}")
        print(f"   ✅ Accepted: {accepted_invites}")
        print(f"   ⏳ Pending: {pending_invites}")
        
        self.print_stats_update("after invitation creation")

    def populate_database(self, 
                         num_users=300,
                         total_collections=800,
                         min_images_per_collection=15,
                         max_images_per_collection=25,
                         min_versions_per_image=2,
                         max_versions_per_image=8,
                         num_invitations=50):
        """Main method to populate the entire database"""
        
        print("=" * 60)
        print("TEXTURE REFERENCE VAULT - DATABASE POPULATION")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Clear existing data (optional - comment out to preserve data)
            if input("Clear existing data? (y/N): ").lower() == 'y':
                print("Clearing existing data...")
                db.session.query(ImageVersion).delete()
                db.session.query(TextureImage).delete()
                db.session.query(CollectionInvitation).delete()
                db.session.query(CollectionPermission).delete()
                db.session.query(Collection).delete()
                db.session.query(User).delete()
                db.session.commit()
            
            # Create all data
            self.create_users(num_users)
            self.create_collections(total_collections=total_collections)
            self.create_collection_permissions()
            self.create_images_and_versions(
                min_images=min_images_per_collection,
                max_images=max_images_per_collection,
                min_versions=min_versions_per_image,
                max_versions=max_versions_per_image
            )
            self.create_invitations(num_invitations)
            
            # Print summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "=" * 60)
            print("DATABASE POPULATION COMPLETE!")
            print("=" * 60)
            print(f"Time taken: {duration}")
            print(f"Users created: {len(self.users)}")
            print(f"Collections created: {len(self.collections)}")
            print(f"Total images: {db.session.query(TextureImage).count()}")
            print(f"Total image versions: {db.session.query(ImageVersion).count()}")
            print(f"Total permissions: {db.session.query(CollectionPermission).count()}")
            print(f"Total invitations: {db.session.query(CollectionInvitation).count()}")
            
            # Sample data for testing
            print("\n" + "-" * 40)
            print("SAMPLE LOGIN CREDENTIALS:")
            print("-" * 40)
            print("Admin users:")
            admin_users = [u for u in self.users if u.is_admin][:3]
            for user in admin_users:
                print(f"  Username: {user.username}")
                print(f"  Password: admin123")
                print()
            
            print("Regular users:")
            regular_users = [u for u in self.users if not u.is_admin][:5]
            for user in regular_users:
                print(f"  Username: {user.username}")
                print(f"  Password: password123")
                print()
            
        except Exception as e:
            print(f"Error during population: {e}")
            db.session.rollback()
            raise

def main():
    """Main execution function"""
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        populator = DatabasePopulator(app)
        
        # Configuration - adjust these numbers as needed
        config = {
            'num_users': 5,              # Total users to create
            'total_collections': 15,     # Total collections across all users  
            'min_images_per_collection': 3,    # Minimum images per collection
            'max_images_per_collection': 8,    # Maximum images per collection
            'min_versions_per_image': 1,       # Minimum versions per image
            'max_versions_per_image': 3,       # Maximum versions per image
            'num_invitations': 4              # Number of invitations to create
        }
        
        print("Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        print()
        
        if input("Proceed with population? (y/N): ").lower() == 'y':
            populator.populate_database(**config)
        else:
            print("Population cancelled.")

if __name__ == '__main__':
    main()
