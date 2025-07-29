# Modular Flask Application Structure

## Overview
The original monolithic Flask application has been successfully broken down into a modular structure using Flask blueprints and the application factory pattern.

## New Structure

```
/workspaces/Texture Reference Vault/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/
│   │   ├── __init__.py          # Model imports
│   │   ├── user.py              # User model
│   │   ├── collection.py        # Collection and Permission models
│   │   └── image.py             # Image and Version models
│   ├── routes/
│   │   ├── __init__.py          # Blueprint registration
│   │   ├── main.py              # Main routes (dashboard, admin)
│   │   ├── auth.py              # Authentication routes
│   │   ├── collections.py       # Collection management routes
│   │   └── images.py            # Image management routes
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   └── ... (other templates)
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # Utility functions
├── static/                      # CSS, JS, images
├── uploads/                     # User uploaded files
├── config.py                    # Configuration classes
├── run.py                       # Application entry point
└── requirements.txt

```

## Key Components

### 1. Application Factory (`app/__init__.py`)
- Uses the factory pattern for creating Flask app instances
- Configures database, login manager, and blueprints
- Sets up template and static folder locations
- Registers context processors and user loader

### 2. Models (`app/models/`)
- **User**: Authentication and user management
- **Collection**: Image collections with permissions
- **TextureImage**: Image metadata and file management
- **ImageVersion**: Version control for images
- **CollectionPermission**: Access control for collections

### 3. Routes/Blueprints (`app/routes/`)
- **main_bp**: Dashboard, admin, and general pages
- **auth_bp**: Login, logout, registration, profile
- **collections_bp**: Collection CRUD and permissions
- **images_bp**: Image upload, versioning, and publishing

### 4. Configuration (`config.py`)
- Environment-based configuration classes
- Support for development and production settings
- Centralized configuration management

### 5. Utilities (`app/utils/`)
- Helper functions for file handling
- Permission checking utilities
- Image processing functions

## Benefits of the Modular Structure

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to find and modify code
3. **Scalability**: Easy to add new features as separate modules
4. **Testing**: Individual components can be tested in isolation
5. **Reusability**: Modules can be reused in other projects
6. **Team Development**: Multiple developers can work on different modules

## URL Structure

With blueprints, the URLs are now organized as:

- `/` - Main routes (dashboard, admin)
- `/auth/` - Authentication routes (login, register, profile)
- `/collection/` - Collection management routes
- `/image/` - Image management routes

## Running the Application

Use the new entry point:

```bash
python run.py
```

Or use the start script:

```bash
./start.sh
```

## Migration Notes

- Templates have been moved to `app/templates/`
- All URL references updated to use blueprint syntax
- Database models use relative imports
- Configuration separated from application code
- Old `app.py` backed up as `app_old.py`

This modular structure provides a solid foundation for future development and maintenance of the Texture Reference Vault application.
