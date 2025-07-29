# Texture Reference Vault - Advanced Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Database Schema](#database-schema)
4. [Security Implementation](#security-implementation)
5. [API Documentation](#api-documentation)
6. [File Management System](#file-management-system)
7. [Permission System](#permission-system)
8. [Frontend Architecture](#frontend-architecture)
9. [Performance Considerations](#performance-considerations)
10. [Deployment Guide](#deployment-guide)
11. [Testing Strategy](#testing-strategy)
12. [Troubleshooting](#troubleshooting)
13. [Extension Points](#extension-points)

---

## Project Overview

### Technology Stack
- **Backend Framework**: Flask 2.3.3
- **Database ORM**: SQLAlchemy 3.0.5
- **Authentication**: Flask-Login 0.6.3
- **Password Hashing**: Werkzeug 2.3.7
- **Image Processing**: Pillow 10.0.1
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.0.0, Vanilla JavaScript
- **File Storage**: Local filesystem (configurable to cloud storage)

### Core Functionality Matrix

| Feature | Implementation | Status | Security Level |
|---------|---------------|--------|----------------|
| User Authentication | Flask-Login + Werkzeug | ✅ Complete | High |
| Role-Based Access | Custom permission system | ✅ Complete | High |
| File Upload | Secure multipart handling | ✅ Complete | Medium |
| Version Control | Database-backed versioning | ✅ Complete | Medium |
| Image Processing | Pillow-based metadata extraction | ✅ Complete | Low |
| Collection Sharing | Permission-based sharing | ✅ Complete | High |

---

## Architecture & Design Patterns

### MVC Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Models      │    │   Controllers   │    │     Views       │
│   (SQLAlchemy)  │◄──►│  (Flask Routes) │◄──►│  (Jinja2 HTML)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Database     │    │   Business      │    │   Static        │
│   (SQLite)      │    │   Logic         │    │   Assets        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Design Patterns Used

1. **Repository Pattern**: Data access abstraction through SQLAlchemy models
2. **Factory Pattern**: Flask application factory (extendable)
3. **Decorator Pattern**: Route protection with `@login_required`
4. **Strategy Pattern**: Permission validation system
5. **Observer Pattern**: Flask signals for audit logging (future)

### Application Structure
```
app.py                 # Application factory and main routes
├── Models/            # Data models (currently in app.py)
│   ├── User           # User authentication model
│   ├── Collection     # Collection organization model
│   ├── TextureImage   # Image metadata model
│   ├── ImageVersion   # Version control model
│   └── CollectionPermission # Access control model
├── Controllers/       # Route handlers (currently in app.py)
│   ├── auth           # Authentication routes
│   ├── collections    # Collection management
│   ├── images         # Image operations
│   ├── admin          # Administrative functions
│   └── api            # Future API endpoints
├── Views/             # Template rendering
│   └── templates/     # Jinja2 templates
└── Utils/             # Helper functions
    ├── permissions    # Permission checking
    ├── file_handling  # File operations
    └── image_processing # Image metadata
```

---

## Database Schema

### Entity Relationship Diagram
```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────┐
│    User     │────►│ CollectionPermission│◄────│ Collection  │
│             │     │                     │     │             │
│ id (PK)     │     │ id (PK)             │     │ id (PK)     │
│ username    │     │ user_id (FK)        │     │ name        │
│ email       │     │ collection_id (FK)  │     │ description │
│ password_hash│     │ permission_level    │     │ created_by  │
│ is_admin    │     └─────────────────────┘     │ created_at  │
│ created_at  │                                 └─────────────┘
└─────────────┘                                        │
       │                                               │
       │    ┌─────────────┐     ┌──────────────────────┘
       └───►│TextureImage │◄────┘
            │             │
            │ id (PK)     │     ┌─────────────┐
            │ filename    │────►│ImageVersion │
            │ filepath_orig│     │             │
            │ filepath_curr│     │ id (PK)     │
            │ width       │     │ image_id(FK)│
            │ height      │     │ version_num │
            │ file_size   │     │ filepath    │
            │ collection_id│     │ uploaded_by │
            │ uploaded_by │     │ uploaded_at │
            │ created_at  │     │ is_current  │
            │ is_published│     └─────────────┘
            └─────────────┘
```

### Table Specifications

#### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);
```

#### Collections Table
```sql
CREATE TABLE collection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

-- Indexes
CREATE INDEX idx_collection_creator ON collection(created_by);
CREATE INDEX idx_collection_name ON collection(name);
```

#### Collection Permissions Table
```sql
CREATE TABLE collection_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    permission_level VARCHAR(20) NOT NULL CHECK (permission_level IN ('read', 'write', 'admin')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collection(id) ON DELETE CASCADE,
    UNIQUE(user_id, collection_id)
);

-- Indexes
CREATE INDEX idx_permission_user ON collection_permission(user_id);
CREATE INDEX idx_permission_collection ON collection_permission(collection_id);
```

#### Texture Images Table
```sql
CREATE TABLE texture_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    original_filepath VARCHAR(500) NOT NULL,
    current_filepath VARCHAR(500),
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    modification_date DATETIME,
    collection_id INTEGER NOT NULL,
    uploaded_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (collection_id) REFERENCES collection(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES user(id)
);

-- Indexes
CREATE INDEX idx_image_collection ON texture_image(collection_id);
CREATE INDEX idx_image_filename ON texture_image(filename);
CREATE INDEX idx_image_published ON texture_image(is_published);
```

#### Image Versions Table
```sql
CREATE TABLE image_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    uploaded_by INTEGER NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (image_id) REFERENCES texture_image(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES user(id),
    UNIQUE(image_id, version_number)
);

-- Indexes
CREATE INDEX idx_version_image ON image_version(image_id);
CREATE INDEX idx_version_current ON image_version(is_current);
```

---

## Security Implementation

### Authentication Security

#### Password Security
- **Hashing Algorithm**: PBKDF2-SHA256 (Werkzeug default)
- **Salt**: Automatically generated unique salt per password
- **Iteration Count**: 260,000 iterations (Werkzeug 2.3.7 default)
- **Implementation**:
  ```python
  from werkzeug.security import generate_password_hash, check_password_hash
  
  # Password hashing
  password_hash = generate_password_hash(password, method='pbkdf2:sha256')
  
  # Password verification
  is_valid = check_password_hash(password_hash, password)
  ```

#### Session Security
- **Session Storage**: Server-side sessions via Flask-Login
- **Session Timeout**: Browser session (configurable)
- **CSRF Protection**: Built-in Flask CSRF protection (can be enhanced)
- **Secure Cookies**: HTTPOnly, Secure flags in production

### File Upload Security

#### File Validation
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

#### Path Security
- **Secure Filename**: `werkzeug.utils.secure_filename()`
- **UUID Prefixing**: Prevents filename collisions and enumeration
- **Path Traversal Protection**: No user-controlled paths in file operations
- **Upload Directory Isolation**: Files stored outside web root

#### Content Validation
- **MIME Type Checking**: PIL image validation
- **File Header Validation**: Magic number verification
- **Size Limits**: Configurable maximum file size

### Permission Security

#### Access Control Matrix
```python
PERMISSION_LEVELS = {
    'read': 1,
    'write': 2,
    'admin': 3
}

def has_collection_permission(user, collection, required_level='read'):
    # Admin users have full access
    if user.is_admin:
        return True
    
    # Collection owners have full access
    if collection.created_by == user.id:
        return True
    
    # Check explicit permissions
    permission = CollectionPermission.query.filter_by(
        user_id=user.id, 
        collection_id=collection.id
    ).first()
    
    if not permission:
        return False
    
    user_level = PERMISSION_LEVELS.get(permission.permission_level, 0)
    required_level_num = PERMISSION_LEVELS.get(required_level, 0)
    
    return user_level >= required_level_num
```

### SQL Injection Prevention
- **SQLAlchemy ORM**: Parameterized queries by default
- **Input Validation**: Form data validation
- **No Raw SQL**: All database operations through ORM

---

## API Documentation

### Authentication Endpoints

#### POST /register
**Description**: Create new user account
**Request Body**:
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```
**Response**:
```json
{
    "success": true,
    "message": "Registration successful",
    "redirect": "/login"
}
```

#### POST /login
**Description**: Authenticate user
**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```
**Response**:
```json
{
    "success": true,
    "redirect": "/dashboard"
}
```

### Collection Management Endpoints

#### GET /dashboard
**Description**: Get user's accessible collections
**Authentication**: Required
**Response**: HTML dashboard with collections

#### POST /collection/create
**Description**: Create new collection
**Authentication**: Required
**Request Body**:
```json
{
    "name": "string",
    "description": "string"
}
```

#### GET /collection/{id}
**Description**: View collection details
**Authentication**: Required
**Permissions**: Read access to collection

#### POST /collection/{id}/upload
**Description**: Upload image to collection
**Authentication**: Required
**Permissions**: Write access to collection
**Content-Type**: multipart/form-data
**Request Body**:
```
file: [binary image data]
original_path: string
```

### Image Management Endpoints

#### GET /image/{id}
**Description**: View image details and versions
**Authentication**: Required
**Permissions**: Read access to collection

#### POST /image/{id}/upload_version
**Description**: Upload new version of image
**Authentication**: Required
**Permissions**: Write access to collection
**Content-Type**: multipart/form-data

#### GET /image/{id}/publish
**Description**: Publish current version to original filepath
**Authentication**: Required
**Permissions**: Write access to collection

### File Serving Endpoints

#### GET /uploads/{filename}
**Description**: Serve uploaded image files
**Authentication**: Required
**Security**: Filename validation, permission checking

---

## File Management System

### Storage Architecture
```
uploads/
├── [uuid]_original_filename.ext
├── [uuid]_original_filename.ext
└── [uuid]_original_filename.ext
```

### File Processing Pipeline
1. **Upload Validation**: File type, size, security checks
2. **Filename Processing**: Secure filename + UUID prefix
3. **Metadata Extraction**: Dimensions, file size, MIME type
4. **Database Storage**: File metadata and relationships
5. **Version Management**: Link to previous versions

### Image Metadata Extraction
```python
def get_image_dimensions(filepath):
    try:
        with Image.open(filepath) as img:
            return img.size  # (width, height)
    except Exception as e:
        logger.error(f"Error processing image {filepath}: {e}")
        return None, None
```

### File Cleanup Strategy
- **Orphaned Files**: Periodic cleanup of unreferenced files
- **Version Pruning**: Configurable version history limits
- **Storage Monitoring**: Disk usage alerts

### Future Storage Options
- **AWS S3**: Cloud storage integration
- **CDN Integration**: Fast global content delivery
- **Image Optimization**: Automatic compression and format conversion

---

## Permission System

### Permission Hierarchy
```
Owner (Collection Creator)
├── Full access to collection
├── Can manage permissions
├── Can delete collection
└── Cannot be removed from collection

Admin Permission
├── All Owner permissions
├── Can add/remove users
├── Can change permission levels
└── Can manage collection settings

Write Permission
├── All Read permissions
├── Can upload images
├── Can create versions
├── Can publish images
└── Can edit image metadata

Read Permission
├── Can view collection
├── Can view images
├── Can download images
└── Can view version history
```

### Permission Checking Implementation
```python
class PermissionChecker:
    @staticmethod
    def can_read(user, collection):
        return has_collection_permission(user, collection, 'read')
    
    @staticmethod
    def can_write(user, collection):
        return has_collection_permission(user, collection, 'write')
    
    @staticmethod
    def can_admin(user, collection):
        return has_collection_permission(user, collection, 'admin')
    
    @staticmethod
    def is_owner(user, collection):
        return collection.created_by == user.id or user.is_admin
```

### Audit Trail (Future Enhancement)
```sql
CREATE TABLE permission_audit (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    collection_id INTEGER,
    action VARCHAR(50),
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Frontend Architecture

### Component Structure
```
templates/
├── base.html              # Base template with navigation
├── components/            # Reusable components (future)
│   ├── image_card.html
│   ├── upload_zone.html
│   └── permission_table.html
├── auth/                  # Authentication templates
│   ├── login.html
│   └── register.html
├── collections/           # Collection management
│   ├── dashboard.html
│   ├── create_collection.html
│   ├── view_collection.html
│   └── edit_collection.html
├── images/                # Image management
│   ├── upload_image.html
│   └── view_image.html
└── admin/                 # Administrative interface
    ├── admin.html
    ├── manage_permissions.html
    └── profile.html
```

### CSS Architecture
```css
/* CSS Custom Properties */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --dark-color: #34495e;
    --light-color: #ecf0f1;
}

/* Component Classes */
.main-content { /* Main container styling */ }
.stats-card { /* Statistics display cards */ }
.collection-grid { /* Grid layout for collections */ }
.upload-zone { /* Drag-and-drop upload areas */ }
.image-preview { /* Image display styling */ }
```

### JavaScript Functionality
- **Drag & Drop**: File upload interfaces
- **Image Previews**: Client-side image preview
- **Form Validation**: Client-side validation
- **AJAX Operations**: Future API integrations
- **Progressive Enhancement**: Works without JavaScript

### Responsive Design
- **Mobile First**: Bootstrap 5 responsive grid
- **Breakpoints**: 
  - xs: <576px (mobile)
  - sm: ≥576px (mobile landscape)
  - md: ≥768px (tablets)
  - lg: ≥992px (desktops)
  - xl: ≥1200px (large desktops)

---

## Performance Considerations

### Database Optimization
- **Indexes**: Strategic indexing on frequently queried columns
- **Query Optimization**: Eager loading for relationships
- **Connection Pooling**: SQLAlchemy connection management
- **Database Migrations**: Alembic for schema changes (future)

### File Serving Optimization
- **Static File Serving**: Nginx/Apache for production
- **Image Compression**: Pillow optimization
- **Caching Headers**: Browser and CDN caching
- **Thumbnail Generation**: On-demand thumbnail creation

### Application Performance
- **Template Caching**: Jinja2 template compilation caching
- **Session Storage**: Redis for production sessions
- **Background Tasks**: Celery for async operations (future)
- **Monitoring**: Application performance monitoring

### Scalability Considerations
- **Horizontal Scaling**: Stateless application design
- **Database Scaling**: PostgreSQL with read replicas
- **File Storage**: Distributed storage systems
- **Load Balancing**: Multiple application instances

---

## Deployment Guide

### Development Environment
```bash
# Local development setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
python app.py
```

### Production Deployment

#### Option 1: Traditional Server (Ubuntu/CentOS)
```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip nginx supervisor

# Application setup
git clone <repository>
cd texture-reference-vault
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create production config
cp .env.example .env
# Edit .env with production values

# Gunicorn service
sudo nano /etc/supervisor/conf.d/texture-vault.conf
```

**Supervisor Configuration**:
```ini
[program:texture-vault]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
directory=/path/to/texture-reference-vault
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/texture-vault.log
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /uploads/ {
        alias /path/to/texture-reference-vault/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /static/ {
        alias /path/to/texture-reference-vault/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Option 2: Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Docker Compose**:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/texture_vault
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=texture_vault
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Option 3: Cloud Deployment (AWS/GCP/Azure)
- **App Service**: Deploy to cloud application platforms
- **Container Service**: Use container orchestration
- **Database**: Managed database services
- **Storage**: Cloud storage for file uploads
- **CDN**: Content delivery network integration

### Environment Configuration

#### Production Environment Variables
```bash
# Security
SECRET_KEY=random-256-bit-key-here
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# File Storage
UPLOAD_FOLDER=/var/uploads
MAX_CONTENT_LENGTH=16777216

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/texture-vault/app.log

# Email (future)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

---

## Testing Strategy

### Unit Testing Framework
```python
import unittest
from app import app, db
from models import User, Collection, TextureImage

class TestUserModel(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_password_hashing(self):
        user = User(username='test', email='test@example.com')
        user.set_password('password')
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertTrue(user.check_password('password'))
```

### Integration Testing
```python
class TestCollectionAPI(unittest.TestCase):
    def test_create_collection(self):
        # Test collection creation workflow
        pass
    
    def test_permission_system(self):
        # Test permission enforcement
        pass
    
    def test_file_upload(self):
        # Test file upload functionality
        pass
```

### Test Coverage Goals
- **Unit Tests**: 80%+ code coverage
- **Integration Tests**: All major workflows
- **Security Tests**: Authentication and authorization
- **Performance Tests**: Load testing with realistic data

### Testing Commands
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/

# Run specific test file
python -m pytest tests/test_models.py

# Run performance tests
python -m pytest tests/test_performance.py -v
```

---

## Troubleshooting

### Common Issues

#### Database Issues
**Problem**: Database locked error
**Solution**: 
```python
# Add to app configuration
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 20,
    'pool_recycle': -1,
    'pool_pre_ping': True
}
```

**Problem**: Migration conflicts
**Solution**:
```bash
# Reset database (development only)
rm instance/texture_vault.db
python -c "from app import db; db.create_all()"
```

#### File Upload Issues
**Problem**: File upload fails silently
**Diagnostics**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check file permissions
import os
print(os.access('uploads', os.W_OK))

# Check disk space
import shutil
print(shutil.disk_usage('uploads'))
```

#### Permission Issues
**Problem**: User cannot access collection
**Diagnostics**:
```python
from app import has_collection_permission
result = has_collection_permission(user, collection, 'read')
print(f"Permission check result: {result}")

# Check explicit permissions
permissions = CollectionPermission.query.filter_by(
    user_id=user.id, 
    collection_id=collection.id
).all()
print(f"User permissions: {permissions}")
```

### Debug Mode Configuration
```python
# Enable detailed error pages
app.config['DEBUG'] = True

# Enable SQL query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Enable template debugging
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
```

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/texture_vault.log', 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Texture Vault startup')
```

---

## Extension Points

### Plugin Architecture (Future)
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin
    
    def get_plugin(self, name):
        return self.plugins.get(name)

# Plugin interface
class StoragePlugin:
    def upload_file(self, file, metadata):
        raise NotImplementedError
    
    def delete_file(self, file_id):
        raise NotImplementedError
    
    def get_file_url(self, file_id):
        raise NotImplementedError
```

### API Extensions
```python
# RESTful API blueprint
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/collections', methods=['GET'])
@login_required
def api_collections():
    # JSON API implementation
    pass

app.register_blueprint(api_bp)
```

### Webhook System (Future)
```python
class WebhookManager:
    def __init__(self):
        self.hooks = {}
    
    def register_hook(self, event, callback):
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(callback)
    
    def trigger(self, event, data):
        for callback in self.hooks.get(event, []):
            callback(data)

# Usage
webhook_manager = WebhookManager()
webhook_manager.register_hook('image_uploaded', send_notification)
webhook_manager.register_hook('collection_shared', log_activity)
```

### Machine Learning Integration (Future)
```python
class ImageAnalyzer:
    def __init__(self):
        # Initialize ML models
        pass
    
    def analyze_texture(self, image_path):
        # Texture analysis using ML
        return {
            'material_type': 'fabric',
            'color_palette': ['#ff0000', '#00ff00'],
            'texture_quality': 0.85,
            'tags': ['smooth', 'pattern', 'textile']
        }
    
    def suggest_similar(self, image_id):
        # Find similar textures
        pass
```

### Advanced Search (Future)
```python
from elasticsearch import Elasticsearch

class SearchEngine:
    def __init__(self):
        self.es = Elasticsearch()
    
    def index_image(self, image):
        doc = {
            'filename': image.filename,
            'tags': image.tags,
            'dimensions': f"{image.width}x{image.height}",
            'collection': image.collection.name
        }
        self.es.index(index='textures', doc_type='image', body=doc)
    
    def search(self, query):
        # Advanced search implementation
        pass
```

### Collaboration Features (Future)
- **Comments**: Image annotation system
- **Reviews**: Quality rating system
- **Notifications**: Real-time updates
- **Activity Feed**: Collection activity tracking
- **Export/Import**: Collection backup and sharing

---

## Performance Benchmarks

### Expected Performance Metrics
- **Database Queries**: <100ms for complex joins
- **File Uploads**: 1MB/second minimum throughput
- **Image Processing**: <2 seconds for metadata extraction
- **Page Load Times**: <3 seconds for complex pages
- **Concurrent Users**: 100+ simultaneous users

### Monitoring Implementation
```python
from flask import g
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    total_time = time.time() - g.start_time
    app.logger.info(f'Request took {total_time:.3f}s')
    return response
```

---

This comprehensive documentation provides detailed technical information for developers, administrators, and advanced users of the Texture Reference Vault application. It covers all aspects from basic setup to advanced customization and troubleshooting.
