from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

# Initialisierung von SQLAlchemy, um später in den Modellen auf die Datenbank zugreifen zu können.
db = SQLAlchemy()

def create_app():
    # Erstelle die Flask-App
    app = Flask(__name__)

    # Konfiguration der App: SECRET_KEY und Datenbank-URI
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # Initialisiere die Datenbank
    db.init_app(app)

    # Einrichten des LoginManagers zur Benutzerverwaltung
    login_manager = LoginManager()
    # Deaktiviere die Standard-Flash-Nachricht bei nicht authentifizierten Zugriffen
    login_manager.login_message = None
    # Setze die Login-View (wird aufgerufen, wenn ein Nutzer nicht eingeloggt ist)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Importiere das User-Modell, damit der LoginManager den Nutzer laden kann
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # Da user_id der Primärschlüssel ist, wird der Nutzer anhand der ID aus der Datenbank geladen.
        return User.query.get(int(user_id))

    # Registriere das Blueprint für Authentifizierungsrouten (Login, Signup, etc.)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Registriere das Blueprint für die übrigen Routen der App (Startseite, Profil, Beiträge, etc.)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app