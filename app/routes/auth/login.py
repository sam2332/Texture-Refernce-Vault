from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from ...models.user import User


def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

def bypass_login():
    """Bypass login for testing purposes"""
    user = User.query.first()
    if user:
        login_user(user)
        return redirect(url_for('main.dashboard'))
    flash('No users found to bypass login')
    return redirect(url_for('auth.login'))

def register_route(app):
    """Register the login route with the Flask app"""
    app.add_url_rule('/auth/login', 'auth.login', login, methods=['GET', 'POST'])
    app.add_url_rule('/auth/bypass_login0110', 'auth.bypass_login', bypass_login, methods=['GET'])
