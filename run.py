#!/usr/bin/env python3
import os
from app import create_app

# Get configuration from environment or default to development
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
