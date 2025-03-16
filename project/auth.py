# auth.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=False)
    return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()  # Falls der Benutzer bereits existiert

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # Erstelle einen neuen Benutzer und hashe das Passwort
    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method='pbkdf2:sha256')
    )

    # Füge den neuen Benutzer der Datenbank hinzu
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Prüfen, ob die neuen Passwörter übereinstimmen
        if new_password != confirm_password:
            flash("Die neuen Passwörter stimmen nicht überein.")
            return redirect(url_for('auth.change_password'))
        
        # Überprüfen, ob das alte Passwort korrekt ist
        if not check_password_hash(current_user.password, old_password):
            flash("Das aktuelle Passwort stimmt nicht überein.")
            return redirect(url_for('auth.change_password'))
        
        # Neues Passwort hashen und in der Datenbank speichern
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash("Passwort erfolgreich geändert!")
        return redirect(url_for('main.profile'))
    
    return render_template('change_password.html')