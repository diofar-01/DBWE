Eine einfache Flask-basierte Webanwendung zum Erstellen und Verwalten von buchbezogenen Beiträgen, einschliesslich Kommentaren und grundlegender Benutzer-Authentifizierung.

Die Book Forum-Anwendung ermöglicht den Nutzern:
* Sich mit einer E-Mail-Adresse, einem Passwort und einem Anzeigenamen zu registrieren.
* Sich sicher an- und abzumelden.
* Ihr Passwort jederzeit zu ändern.
* Beiträge über Bücher zu erstellen, mit Feldern wie Titel, Autor, ISBN, Veröffentlichungsdatum und persönlicher Meinung.
* (Optional) Buchdetails über die Google Books API zu suchen und automatisch Felder wie Autor, ISBN und Cover-Bild zu befüllen.
* Kommentare zu eigenen oder fremden Beiträgen zu verfassen.
* Eigene Beiträge zu bearbeiten und zu löschen sowie eigene Kommentare zu löschen.
* Eine Liste ihrer eigenen Beiträge auf einer Profilseite und alle Beiträge auf der Startseite anzusehen.

Features
Benutzer-Authentifizierung
* Sicheres An- und Abmelden mit Passwort-Hashing (Werkzeug.security, PBKDF2).
* Verwaltung der Benutzersitzungen über Flask-Login.
* Passwortwechsel-Funktion.

Datenbank-Integration
* SQLite-Datenbank mit SQLAlchemy ORM.
* Automatische Tabellenerstellung für die Modelle User, Post und Comment.

Beitrags- und Kommentarverwaltung
* Beiträge erstellen, bearbeiten und löschen.
* Kommentare erstellen und löschen.
* Automatisches Löschen zugehöriger Kommentare beim Löschen eines Beitrags (Cascade Delete).

Google Books API
* Optionaler Endpunkt (/search_book), um Bücher zu suchen und Felder wie Autor, ISBN und Cover-Bild automatisch auszufüllen.

Frontend-Styling mit Bulma
* Einfache, responsive Gestaltung durch das Bulma-CSS-Framework.

Abhängigkeiten
Alle benötigten Pakete sind in der Datei requirements.txt aufgelistet.





