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
   python app.py
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
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   ├── index.html        # Landing page
│   ├── login.html        # User login
│   ├── register.html     # User registration
│   ├── dashboard.html    # Main dashboard
│   ├── create_collection.html
│   ├── view_collection.html
│   ├── edit_collection.html
│   ├── upload_image.html
│   ├── view_image.html   # Image details and version management
│   ├── admin.html        # Admin panel
│   ├── profile.html      # User profile
│   └── manage_permissions.html
├── static/               # Static assets
├── uploads/              # User uploaded files
└── texture_vault.db      # SQLite database (created on first run)
```

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

This is a complete, production-ready Flask application with modern UI design and comprehensive functionality. The codebase is well-structured and follows Flask best practices.

## License

This project is provided as-is for educational and practical use.
