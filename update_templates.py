#!/usr/bin/env python3
"""
Script to update template URL references to use blueprints
"""

import os
import re

# Mapping of old routes to new blueprint routes
ROUTE_MAPPINGS = {
    # Auth routes
    "url_for('login')": "url_for('auth.login')",
    "url_for('logout')": "url_for('auth.logout')",
    "url_for('register')": "url_for('auth.register')",
    "url_for('profile')": "url_for('auth.profile')",
    "url_for('change_password')": "url_for('auth.change_password')",
    
    # Main routes  
    "url_for('index')": "url_for('main.index')",
    "url_for('dashboard')": "url_for('main.dashboard')",
    "url_for('collections')": "url_for('main.collections')",
    "url_for('admin')": "url_for('main.admin')",
    
    # Collection routes
    "url_for('create_collection')": "url_for('collections.create_collection')",
    "url_for('view_collection',": "url_for('collections.view_collection',",
    "url_for('edit_collection',": "url_for('collections.edit_collection',",
    "url_for('delete_collection',": "url_for('collections.delete_collection',",
    "url_for('manage_permissions',": "url_for('collections.manage_permissions',",
    "url_for('add_permission',": "url_for('collections.add_permission',",
    "url_for('remove_permission',": "url_for('collections.remove_permission',",
    
    # Image routes
    "url_for('upload_image',": "url_for('images.upload_image',",
    "url_for('view_image',": "url_for('images.view_image',",
    "url_for('upload_version',": "url_for('images.upload_version',",
    "url_for('publish_image',": "url_for('images.publish_image',",
    "url_for('uploaded_file',": "url_for('images.uploaded_file',",
}

def update_template_file(filepath):
    """Update a single template file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Apply all mappings
    for old_route, new_route in ROUTE_MAPPINGS.items():
        content = content.replace(old_route, new_route)
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated: {filepath}")
        return True
    return False

def main():
    """Main function to update all template files"""
    templates_dir = "templates"
    updated_count = 0
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            if update_template_file(filepath):
                updated_count += 1
    
    print(f"Updated {updated_count} template files")

if __name__ == "__main__":
    main()
