from flask import render_template
from flask_login import login_required


@login_required
def profile():
    return render_template('profile.html')


def register_route(app):
    """Register the profile route with the Flask app"""
    app.add_url_rule('/auth/profile', 'auth.profile', profile)
