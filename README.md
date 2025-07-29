# Texture Reference Vault

A comprehensive Flask web application for managing texture reference collections with user authentication, permissions, and version control.

## Features

### 🔐 Authentication & User Management
- User registration and login system
- Admin panel for user management
- Role-based access control (Admin/User)

### 📁 Collection Management
- Create and organize texture collections
- Per-collection permission system (Read/Write/Admin)
- Collection sharing with other users

### 🖼️ Image Management
- Upload texture images with metadata
- Image preview with dimensions and file info
- Original filepath tracking for publishing

### 🔄 Version Control
- Upload multiple versions of the same image
- Version history tracking
- Publish current version back to original location

### 👥 Collaboration
- Share collections with specific users
- Granular permission levels
- User activity tracking

## Installation

1. **Clone or setup the project directory:**
   ```bash
   cd "/home/srudloff/Research/Texture Refernce Vault"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create uploads directory:**
   ```bash
   mkdir -p uploads
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```

6. **Access the application:**
   Open your browser and go to `http://localhost:5000`

## Usage

### Getting Started

1. **First Run:** The first user to register will automatically become an admin.

2. **Create Collections:** Use the dashboard to create new texture collections.

3. **Upload Images:** Add texture images to collections with original filepath metadata.

4. **Manage Permissions:** Share collections with other users and set appropriate permission levels.

5. **Version Control:** Upload new versions of images and publish them back to their original locations.

### User Roles

- **Admin:** Full access to all collections, user management, and system settings
- **User:** Access to owned collections and shared collections based on permissions

### Permission Levels

- **Read:** View images and collections
- **Write:** Upload images, create versions, publish images
- **Admin:** Full collection management including permission control

## Database Schema

### Users
- User accounts with authentication
- Admin flag for elevated privileges

### Collections
- Organized groups of texture images
- Owner-based access control

### Collection Permissions
- User-specific access levels per collection
- Granular permission system

### Texture Images
- Image metadata and file information
- Original filepath for publishing
- Upload tracking and status

### Image Versions
- Version history for each image
- Current version tracking
- Upload accountability

## File Structure

```
Texture Reference Vault/
├── run.py                 # Main Flask application entry point
├── config.py             # Application configuration
├── requirements.txt      # Python dependencies
├── app/                  # Application package
│   ├── __init__.py       # Flask app factory
│   ├── models/           # Database models
│   │   ├── user.py       # User model
│   │   ├── collection.py # Collection models
│   │   ├── image.py      # Image models
│   │   └── invitation.py # Invitation models
│   ├── routes/           # Route handlers (modular structure)
│   │   ├── __init__.py   # Route registration system
│   │   ├── auth/         # Authentication routes
│   │   │   ├── login.py
│   │   │   ├── register.py
│   │   │   ├── logout.py
│   │   │   ├── profile.py
│   │   │   └── change_password.py
│   │   ├── main/         # Main application routes
│   │   │   ├── index.py
│   │   │   ├── dashboard.py
│   │   │   └── admin.py
│   │   ├── collections/  # Collection management routes
│   │   │   ├── create_collection.py
│   │   │   ├── view_collection.py
│   │   │   ├── edit_collection.py
│   │   │   ├── delete_collection.py
│   │   │   ├── manage_permissions.py
│   │   │   ├── add_permission.py
│   │   │   ├── remove_permission.py
│   │   │   ├── invite_user.py
│   │   │   ├── accept_invitation.py
│   │   │   ├── accept_invitation_register.py
│   │   │   ├── cancel_invitation.py
│   │   │   ├── join_collection.py
│   │   │   ├── leave_collection.py
│   │   │   ├── claim_ownership.py
│   │   │   ├── transfer_ownership.py
│   │   │   └── discover_collections.py
│   │   └── images/        # Image management routes
│   │       ├── upload_image.py
│   │       ├── view_image.py
│   │       ├── edit_image.py
│   │       ├── upload_version.py
│   │       ├── publish_image.py
│   │       ├── restore_version.py
│   │       ├── serve_image.py
│   │       └── serve_version.py
│   ├── templates/        # HTML templates
│   │   ├── base.html     # Base template with styling
│   │   ├── index.html    # Landing page
│   │   ├── login.html    # User login
│   │   ├── register.html # User registration
│   │   ├── dashboard.html # Main dashboard
│   │   ├── create_collection.html
│   │   ├── view_collection.html
│   │   ├── edit_collection.html
│   │   ├── upload_image.html
│   │   ├── view_image.html # Image details and version management
│   │   ├── admin.html    # Admin panel
│   │   ├── profile.html  # User profile
│   │   └── manage_permissions.html
│   └── utils/            # Utility functions
│       └── helpers.py    # Helper functions
├── instance/             # Instance-specific files
│   └── texture_vault.db  # SQLite database (created on first run)
├── uploads/              # User uploaded files
└── static/               # Static assets (if any)
```

## Architecture

### Modular Route Structure

This application uses a modular route architecture where each route is defined in its own file. This provides several benefits:

- **Maintainability:** Each route is isolated in its own file, making it easier to find and modify specific functionality
- **Scalability:** New routes can be added without modifying existing files
- **Testing:** Individual routes can be tested in isolation
- **Code Organization:** Related functionality is grouped together logically

#### Route Registration System

Each route file contains:
1. The route handler function
2. A `register_route(app)` function that registers the route with the Flask application

Example route file structure:
```python
# app/routes/auth/login.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from ...models.user import User

def login():
    # Route handler logic here
    pass

def register_route(app):
    """Register the login route with the Flask app"""
    app.add_url_rule('/auth/login', 'auth.login', login, methods=['GET', 'POST'])
```

#### URL Structure

The URL structure remains exactly the same as before:
- Authentication routes: `/auth/*`
- Collection routes: `/collection/*`
- Image routes: `/image/*`
- Main routes: `/`, `/dashboard`, `/admin`

All `url_for()` calls continue to work with the same endpoint names (e.g., `url_for('auth.login')`, `url_for('collections.view_collection', id=1)`).

## Security Features

- Password hashing using Werkzeug
- Session management with Flask-Login
- Secure file uploads with validation
- Path traversal protection
- Permission-based access control

## Configuration

### Environment Variables
You can create a `.env` file to override default settings:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///texture_vault.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

### File Upload Settings
- Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
- Maximum file size: 16MB
- Files are stored with UUID prefixes to prevent conflicts

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Collections
- `GET /dashboard` - Main dashboard
- `GET/POST /collection/create` - Create new collection
- `GET /collection/<id>` - View collection
- `GET/POST /collection/<id>/edit` - Edit collection
- `GET /collection/<id>/delete` - Delete collection

### Images
- `GET/POST /collection/<id>/upload` - Upload image
- `GET /image/<id>` - View image details
- `POST /image/<id>/upload_version` - Upload new version
- `GET /image/<id>/publish` - Publish to original path

### Permissions
- `GET /collection/<id>/permissions` - Manage permissions
- `POST /collection/<id>/add_permission` - Add user permission
- `GET /collection/<id>/remove_permission/<permission_id>` - Remove permission

### Admin
- `GET /admin` - Admin panel
- `GET /profile` - User profile
- `POST /change_password` - Change password

## Contributing

### Adding New Routes

To add a new route to the application:

1. **Create a new route file** in the appropriate subdirectory (e.g., `app/routes/auth/new_feature.py`)

2. **Implement the route handler** and registration function:
   ```python
   from flask import render_template
   from flask_login import login_required

   @login_required
   def new_feature():
       return render_template('new_feature.html')

   def register_route(app):
       """Register the new_feature route with the Flask app"""
       app.add_url_rule('/auth/new_feature', 'auth.new_feature', new_feature)
   ```

3. **Import and register** the new route in `app/routes/__init__.py`:
   ```python
   from .auth import new_feature as auth_new_feature

   def register_all_routes(app):
       # ... existing routes ...
       auth_new_feature.register_route(app)
   ```

4. **Create the template** (if needed) in `app/templates/`

5. **Test the route** by accessing it through the application

### Development Guidelines

This is a complete, production-ready Flask application with modern UI design and comprehensive functionality. The codebase is well-structured and follows Flask best practices:

- Use type hints where appropriate
- Include docstrings for complex functions
- Follow the existing permission checking patterns
- Use the database transaction patterns shown in existing routes
- Maintain consistent error handling and user feedback

## License

This project is provided as-is for educational and practical use.
