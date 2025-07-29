# Texture Reference Vault

A comprehensive Flask web application for managing texture reference collections with user authentication, permissions, and advanced version control. Built with a modular architecture using Flask blueprints for scalability and maintainability.

## Features

### 🔐 Authentication & User Management
- User registration and login system with Flask-Login
- Admin panel for user management
- Role-based access control (Admin/User)
- Secure password hashing with Werkzeug

### 📁 Collection Management
- Create and organize texture collections
- Per-collection permission system (Read/Write/Admin)
- Collection sharing with other users
- Hierarchical organization system

### 🖼️ Advanced Image Management
- Upload texture images with comprehensive metadata
- Image preview with dimensions and file size info
- Original filepath tracking for publishing workflows
- Automatic image dimension detection using Pillow
- Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP, TIFF, WebP)
- File size optimization and validation

### 🔄 Advanced Version Control
- Upload multiple versions of the same image
- Complete version history tracking with timestamps
- Binary data storage for each version in database
- Current version tracking and management
- Publish current version back to original location
- Version comparison and preview capabilities
- Download specific versions

### 👥 Collaboration & Permissions
- Share collections with specific users
- Granular permission levels (Read/Write/Admin)
- User activity tracking and upload accountability
- Real-time permission validation

### 🎨 Modern UI/UX
- Bootstrap 5 responsive design
- Interactive image preview modals
- Drag-and-drop file upload interface
- Real-time file preview before upload
- Progress indicators and loading states
- Mobile-friendly responsive layout

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or setup the project directory:**
   ```bash
   git clone <repository-url>
   cd "Texture Reference Vault"
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

4. **Environment Configuration (Optional):**
   Create a `.env` file for custom configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Create required directories:**
   ```bash
   mkdir -p uploads
   mkdir -p static
   mkdir -p instance
   ```

6. **Run the application:**
   ```bash
   python run.py
   ```
   Or use the provided scripts:
   ```bash
   # Unix/Linux/macOS
   ./start.sh
   
   # Windows
   start.bat
   ```

7. **Access the application:**
   Open your browser and go to `http://localhost:5000`

### Development Setup
For development with auto-reload:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

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

### Users (`user`)
- User accounts with secure authentication
- Admin flag for elevated privileges
- Password hashing and session management

### Collections (`collection`)
- Organized groups of texture images
- Owner-based access control
- Metadata and description fields

### Collection Permissions (`collection_permission`)
- User-specific access levels per collection
- Granular permission system (Read/Write/Admin)
- Flexible sharing capabilities

### Texture Images (`texture_image`)
- Comprehensive image metadata
- Original filepath for publishing workflows
- Current filepath tracking
- Dimensions (width/height) and file size
- Upload tracking and publication status
- Relationship to collections and users

### Image Versions (`image_version`)
- Complete version history for each image
- Binary data storage (LargeBinary field)
- Version numbering system
- Current version tracking
- Upload accountability with timestamps
- Individual version serving capabilities

## Project Structure

```
Texture Reference Vault/
├── run.py                    # Application entry point
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── start.sh / start.bat     # Platform-specific startup scripts
├── test_image_data.py       # Database testing utilities
├── app/                     # Main application package
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── collection.py    # Collection and permission models
│   │   └── image.py         # Image and version models
│   ├── routes/              # Blueprint routes
│   │   ├── __init__.py      # Blueprint registration
│   │   ├── main.py          # Main routes (dashboard, index)
│   │   ├── auth.py          # Authentication routes
│   │   ├── collections.py   # Collection management
│   │   └── images.py        # Image and version handling
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Base template with Bootstrap 5
│   │   ├── index.html       # Landing page
│   │   ├── login.html       # User authentication
│   │   ├── register.html    # User registration
│   │   ├── dashboard.html   # Main dashboard
│   │   ├── create_collection.html
│   │   ├── view_collection.html
│   │   ├── edit_collection.html
│   │   ├── upload_image.html # Drag-drop image upload
│   │   ├── view_image.html  # Image details & version management
│   │   ├── edit_image.html  # Image metadata editing
│   │   ├── admin.html       # Admin panel
│   │   ├── profile.html     # User profile management
│   │   └── manage_permissions.html
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── helpers.py       # Permission helpers, file validation
├── static/                  # Static assets (CSS, JS, images)
├── uploads/                 # User uploaded files
├── instance/                # Instance-specific files
│   └── texture_vault.db     # SQLite database (auto-created)
└── backup_old_templates/    # Template backups
```

## Dependencies

### Core Framework
- **Flask 2.3.3** - Web framework
- **Flask-SQLAlchemy 3.0.5** - Database ORM
- **Flask-Login 0.6.3** - User session management
- **Werkzeug 2.3.7** - WSGI utilities and security

### Image Processing & File Handling
- **Pillow 10.0.1** - Image processing and dimension detection

### Configuration Management
- **python-dotenv 1.0.0** - Environment variable management

### Frontend Technologies
- **Bootstrap 5** - Responsive UI framework
- **Font Awesome** - Icon library
- **JavaScript** - Interactive features and AJAX

## Technical Architecture

### Application Factory Pattern
- Modular Flask application using factory pattern
- Blueprint-based route organization
- Configurable environments (development/production)

### Database Design
- SQLAlchemy ORM with relationship mapping
- Binary large object (BLOB) storage for image versions
- Efficient querying with proper indexing
- Automatic table creation and schema management

### Security Features
- **Password Security:** Werkzeug password hashing
- **Session Management:** Flask-Login secure sessions
- **File Upload Security:** Type validation and secure filename handling
- **Path Traversal Protection:** Secure file path handling
- **Permission-Based Access:** Granular permission system
- **CSRF Protection:** Built-in Flask security features

### Performance Optimizations
- **Binary Data Storage:** Direct database storage for version control
- **Efficient File Serving:** Direct binary response serving
- **Image Optimization:** Automatic dimension detection
- **Lazy Loading:** Optimized database queries

## Testing

The project includes testing utilities:

```bash
# Test image data functionality
python test_image_data.py

# This script verifies:
# - Image creation and storage
# - Version control functionality
# - Binary data integrity
# - Database relationships
```

## Configuration

### Environment Variables
Create a `.env` file to override default settings:

```bash
# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///texture_vault.db

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=536870912  # 512MB in bytes

# Application Environment
FLASK_ENV=development  # or production
FLASK_DEBUG=1          # for development only
```

### File Upload Settings
- **Supported formats:** PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
- **Maximum file size:** 512MB (configurable)
- **Storage:** Files stored with UUID prefixes to prevent conflicts
- **Version control:** Binary data stored in database for complete version history
- **Validation:** File type validation and dimension detection

### Database Configuration
- **Development:** SQLite database (default)
- **Production:** Configurable via DATABASE_URL environment variable
- **Migrations:** Automatic table creation on first run
- **Binary storage:** Large binary fields for image version data

## API Endpoints

### Authentication
- `GET/POST /login` - User login with session management
- `GET/POST /register` - User registration with validation
- `GET /logout` - User logout and session cleanup

### Collections
- `GET /dashboard` - Main dashboard with collections overview
- `GET/POST /collection/create` - Create new collection
- `GET /collection/<id>` - View collection with images
- `GET/POST /collection/<id>/edit` - Edit collection metadata
- `GET /collection/<id>/delete` - Delete collection (with confirmation)

### Images
- `GET/POST /collection/<id>/upload` - Upload image with metadata
- `GET /image/<id>` - View image details and version history
- `GET/POST /image/<id>/edit` - Edit image metadata
- `POST /image/<id>/upload_version` - Upload new version
- `GET /image/<id>/publish` - Publish current version to original path
- `GET /image/<id>/serve` - Serve current image version
- `GET /image/version/<version_id>/serve` - Serve specific version

### Permissions
- `GET /collection/<id>/permissions` - Manage collection permissions
- `POST /collection/<id>/add_permission` - Add user permission
- `GET /collection/<id>/remove_permission/<permission_id>` - Remove permission

### Admin & User Management
- `GET /admin` - Admin panel with user management
- `GET /profile` - User profile and settings
- `POST /change_password` - Change user password

### Version Control
- Version history tracking with complete metadata
- Binary data serving for each version
- Current version management and switching

## Contributing

This is a production-ready Flask application with modern architecture and comprehensive functionality. The codebase follows Flask best practices and is well-structured for maintainability and scalability.

### Development Guidelines
- Follow Python PEP 8 coding standards
- Use Blueprint pattern for route organization
- Implement proper error handling and validation
- Maintain comprehensive comments and documentation
- Test changes with the provided test utilities

### Key Features for Contributors
- **Modular Architecture:** Easy to extend with new features
- **Comprehensive Permission System:** Granular access control
- **Modern UI/UX:** Bootstrap 5 responsive design
- **Advanced Version Control:** Complete image history tracking
- **Binary Data Management:** Efficient file storage and serving

## Deployment

### Production Deployment
1. Set `FLASK_ENV=production` in environment
2. Configure a production database (PostgreSQL recommended)
3. Set a secure `SECRET_KEY`
4. Configure reverse proxy (nginx recommended)
5. Use WSGI server (gunicorn recommended)

### Docker Deployment (Optional)
The project structure supports containerization for easy deployment.

## License

This project is provided as-is for educational and practical use. It represents a complete, feature-rich texture management system suitable for professional workflows.

---

**Last Updated:** July 2025  
**Version:** 2.0 - Advanced Version Control Release
