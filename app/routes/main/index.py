from flask import render_template, redirect, url_for
from flask_login import current_user


def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


def register_route(app):
    """Register the index route with the Flask app"""
    app.add_url_rule('/', 'main.index', index)
