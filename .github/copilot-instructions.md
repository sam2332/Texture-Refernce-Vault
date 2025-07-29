# GitHub Copilot Instructions for Texture Reference Vault

## Project Overview
This is a Flask web application for managing texture reference collections with advanced version control, user authentication, and permissions. The project uses a modular Blueprint architecture with binary data storage for image versions.

## Code Style and Conventions

### Python Code Style
- Follow PEP 8 conventions
- Use type hints where appropriate
- Include docstrings for functions and classes
- Use meaningful variable and function names
- Prefer explicit imports over wildcard imports

### Flask Patterns
- Use Blueprint pattern for route organization
- Implement proper error handling with try-except blocks
- Use Flask-Login's `@login_required` decorator for protected routes
- Validate permissions using `has_collection_permission()` helper
- Use `flash()` for user feedback messages
- Return appropriate HTTP status codes

### Database Patterns
- Use SQLAlchemy ORM relationships properly
- Always commit database changes within try-except blocks
- Use `db.session.rollback()` in exception handlers
- Implement proper foreign key relationships
- Use `query.get_or_404()` for single record retrieval

## Project Structure Guidelines

### File Organization
```
app/
├── models/          # Database models only
├── routes/          # Blueprint routes grouped by functionality  
├── templates/       # Jinja2 HTML templates
└── utils/           # Helper functions and utilities
```

### Blueprint Organization
- `main.py` - Dashboard, index, general pages
- `auth.py` - Authentication (login, register, logout)
- `collections.py` - Collection CRUD operations
- `images.py` - Image upload, version control, serving

## Key Components and Patterns

### Authentication & Permissions
```python
# Always check permissions before operations
if not has_collection_permission(current_user, collection, 'write'):
    flash('You do not have permission to perform this action.')
    return redirect(url_for('main.dashboard'))
```

### File Upload Handling
```python
# Standard file upload pattern
if 'file' not in request.files:
    flash('No file selected')
    return redirect(request.url)

file = request.files['file']
if file.filename == '' or not allowed_file(file.filename):
    flash('Invalid file')
    return redirect(request.url)
```

### Image Version Management
- Always store binary data in `ImageVersion.data` field
- Mark previous versions as `is_current=False` when uploading new versions
- Use UUID prefixes for file naming to prevent conflicts
- Update parent image metadata when new version is uploaded

### Error Handling
```python
try:
    # Database operations
    db.session.commit()
    flash('Operation successful!')
except Exception as e:
    db.session.rollback()
    flash(f'Error: {str(e)}')
    return redirect(request.url)
```

## Frontend Guidelines

### Template Structure
- Extend `base.html` for consistent layout
- Use Bootstrap 5 classes for styling
- Include Font Awesome icons with semantic meaning
- Implement responsive design patterns

### JavaScript Patterns
- Use vanilla JavaScript for simple interactions
- Implement file upload previews for better UX
- Handle modal interactions for version viewing
- Use `fetch()` for AJAX requests when needed

### Form Handling
- Include CSRF protection
- Validate file types and sizes client-side
- Provide real-time feedback for form inputs
- Use progress indicators for file uploads

## Database Schema Considerations

### Core Models
- **User**: Authentication and authorization
- **Collection**: Grouping and organization
- **CollectionPermission**: Granular access control
- **TextureImage**: Image metadata and current state
- **ImageVersion**: Complete version history with binary data

### Relationships
- Use proper SQLAlchemy relationships with backref
- Implement cascade deletes where appropriate
- Consider lazy loading for performance

## Security Best Practices

### Input Validation
- Validate all file uploads (type, size, content)
- Sanitize user inputs
- Use `secure_filename()` for file handling
- Implement path traversal protection

### Access Control
- Always verify user permissions before operations
- Use session-based authentication
- Implement proper logout functionality
- Validate ownership before allowing modifications

## Performance Considerations

### File Handling
- Store binary data efficiently in database
- Use direct Response objects for file serving
- Implement proper MIME type detection
- Consider file size limits and validation

### Database Queries
- Use efficient querying patterns
- Implement proper indexing
- Use joins instead of N+1 queries
- Consider pagination for large datasets

## Common Patterns to Follow

### Route Patterns
```python
@blueprint.route('/<int:id>/action', methods=['GET', 'POST'])
@login_required
def action_name(id):
    # Get resource with 404 handling
    resource = Model.query.get_or_404(id)
    
    # Check permissions
    if not has_permission(current_user, resource):
        flash('Permission denied')
        return redirect(url_for('main.dashboard'))
    
    # Handle POST requests
    if request.method == 'POST':
        try:
            # Process form data
            # Update database
            db.session.commit()
            flash('Success message')
            return redirect(url_for('target.route'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}')
    
    # Render template for GET
    return render_template('template.html', resource=resource)
```

### Model Patterns
```python
class ModelName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Use appropriate data types
    # Include created_at timestamps
    # Implement proper relationships
    # Add useful methods for business logic
```

## Testing Guidelines

### Test Patterns
- Use the existing `test_image_data.py` as reference
- Test database operations with transactions
- Verify file upload functionality
- Test permission systems thoroughly

### Data Validation
- Test edge cases for file uploads
- Verify binary data integrity
- Test permission boundaries
- Validate form input handling

## Debugging and Development

### Logging
- Use Flask's built-in logging
- Log important operations and errors
- Include context in error messages
- Use appropriate log levels

### Development Tools
- Use Flask's debug mode during development
- Implement proper error pages
- Use meaningful variable names for debugging
- Include helpful comments for complex logic

## Special Considerations

### Binary Data Handling
- This project stores image data as binary in the database
- Use `db.LargeBinary` for image version data
- Serve binary data using Flask's Response object
- Handle MIME types correctly for different image formats

### Version Control Logic
- Each image can have multiple versions
- Only one version should be marked as `is_current=True`
- Version numbers should increment sequentially
- Binary data must be stored for each version

### File Publishing
- Images can be "published" back to their original filepath
- Use the current version's binary data for publishing
- Implement proper directory creation for publishing
- Handle file system errors gracefully

Remember: This project emphasizes version control, binary data storage, and granular permissions. Always consider these aspects when implementing new features or modifying existing code.
