from flask import redirect, url_for
from flask_login import logout_user, login_required


@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def register_route(app):
    """Register the logout route with the Flask app"""
    app.add_url_rule('/auth/logout', 'auth.logout', logout)
