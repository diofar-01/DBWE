from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

# --------------------------------------------------
# Route: /login (GET)
# Zeigt die Login-Seite an.
# --------------------------------------------------
@auth.route('/login')
def login():
    return render_template('login.html')

# --------------------------------------------------
# Route: /login (POST)
# Verarbeitet das Login-Formular:
# - Liest die eingegebene E-Mail und das Passwort
# - Überprüft, ob der Nutzer existiert und ob das Passwort korrekt ist
# - Falls die Authentifizierung fehlschlägt, wird eine Flash-Nachricht ausgegeben
# - Bei erfolgreichem Login wird der Nutzer angemeldet und zur Startseite weitergeleitet
# --------------------------------------------------
@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    # Der "remember" Parameter wird hier übergangen (immer False, auch wenn Checkbox gesetzt)
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # Überprüfe, ob der Nutzer existiert und das Passwort korrekt ist
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    # Anmelden des Nutzers und Weiterleitung zur Startseite
    login_user(user, remember=False)
    return redirect(url_for('main.index'))

# --------------------------------------------------
# Route: /signup (GET)
# Zeigt das Registrierungsformular an.
# --------------------------------------------------
@auth.route('/signup')
def signup():
    return render_template('signup.html')

# --------------------------------------------------
# Route: /signup (POST)
# Verarbeitet das Registrierungsformular:
# - Liest E-Mail, Name und Passwort aus dem Formular
# - Überprüft, ob ein Nutzer mit dieser E-Mail bereits existiert
# - Wenn nicht, wird ein neuer Nutzer erstellt und das Passwort wird gehasht
# - Der neue Nutzer wird in der Datenbank gespeichert
# - Anschliessend erfolgt eine Weiterleitung zur Login-Seite
# --------------------------------------------------
@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # Überprüfe, ob ein Nutzer mit dieser E-Mail bereits existiert
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # Erstelle einen neuen Nutzer und hashe das Passwort
    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method='pbkdf2:sha256')
    )

    # Speichere den neuen Nutzer in der Datenbank
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

# --------------------------------------------------
# Route: /logout
# Meldet den aktuell angemeldeten Nutzer ab und leitet ihn zur Login-Seite weiter.
# --------------------------------------------------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# --------------------------------------------------
# Route: /change_password (GET, POST)
# Ermöglicht es dem Nutzer, sein Passwort zu ändern.
# - GET: Zeigt das Formular zum Passwortwechsel an.
# - POST: Verarbeitet das Formular:
#   - Prüft, ob die neuen Passwörter übereinstimmen
#   - Prüft, ob das eingegebene alte Passwort korrekt ist
#   - Aktualisiert das Passwort, falls alle Prüfungen erfolgreich sind
#   - Gibt eine Flash-Nachricht aus und rendert die Seite erneut,
#     damit die Erfolgsmeldung angezeigt wird.
# --------------------------------------------------
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Die neuen Passwörter stimmen nicht überein.")
            return redirect(url_for('auth.change_password'))
        
        if not check_password_hash(current_user.password, old_password):
            flash("Das aktuelle Passwort stimmt nicht überein.")
            return redirect(url_for('auth.change_password'))
        
        # Aktualisiere das Passwort des aktuellen Nutzers
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash("Passwort erfolgreich geändert!")
        # Rendere die Seite erneut, um die Flash-Meldung anzuzeigen
        return render_template('change_password.html')
    
    return render_template('change_password.html')
