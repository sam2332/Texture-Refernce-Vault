from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db


@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Password updated successfully!')
    return redirect(url_for('auth.profile'))


def register_route(app):
    """Register the change_password route with the Flask app"""
    app.add_url_rule('/auth/change_password', 'auth.change_password', change_password, methods=['POST'])
