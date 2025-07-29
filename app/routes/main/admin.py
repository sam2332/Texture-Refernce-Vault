from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ...models.user import User
from ...models.collection import Collection


@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    collections = Collection.query.all()
    return render_template('admin.html', users=users, collections=collections)


def register_route(app):
    """Register the admin route with the Flask app"""
    app.add_url_rule('/admin', 'main.admin', admin)
