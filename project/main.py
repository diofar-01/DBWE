import requests
from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import User, Post, Comment

main = Blueprint('main', __name__)

# --------------------------------------------------
# Endpunkt: Buchsuche mit Google Books API
# Diese Route wird per GET aufgerufen und liefert
# bis zu 5 Buchergebnisse als JSON zurück.
# Nur eingeloggte Nutzer können diese Funktion nutzen.
# --------------------------------------------------
@main.route('/search_book', methods=['GET'])
@login_required
def search_book():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Kein Suchbegriff angegeben'}), 400
    
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': 5,
        'printType': 'books'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'items' not in data or len(data['items']) == 0:
        return jsonify({'error': 'Kein Buch gefunden'}), 404

    results = []
    for item in data['items']:
        volume = item.get('volumeInfo', {})
        result = {
            'title': volume.get('title', ''),
            'authors': volume.get('authors', []),
            'isbn': '',
            'image': volume.get('imageLinks', {}).get('thumbnail', ''),
            'publishedDate': volume.get('publishedDate', '')
        }
        if 'industryIdentifiers' in volume:
            for identifier in volume['industryIdentifiers']:
                if identifier.get('type') in ['ISBN_10', 'ISBN_13']:
                    result['isbn'] = identifier.get('identifier')
                    break
        results.append(result)
    return jsonify(results)

# --------------------------------------------------
# Endpunkt: Startseite
# Zeigt alle Beiträge an und verarbeitet POST-Anfragen,
# um Kommentare zu einem Beitrag zu speichern.
# Nur eingeloggte Nutzer haben Zugriff.
# --------------------------------------------------
@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Kommentar abspeichern
        post_id = request.form.get('post_id')
        comment_text = request.form.get('comment_text')
        if post_id and comment_text:
            new_comment = Comment(
                text=comment_text,
                user_id=current_user.id,
                post_id=post_id
            )
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('main.index'))
    
    # Beiträge nach Erstellungsdatum absteigend sortieren
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('index.html', posts=posts)
# --------------------------------------------------
# Endpunkt: Profilseite
# Zeigt nur die Beiträge des aktuell eingeloggten Nutzers an.
# --------------------------------------------------
@main.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', name=current_user.name, posts=posts)

# --------------------------------------------------
# Endpunkt: Beitrag hinzufügen
# Ermöglicht es, einen neuen Beitrag mit manueller Eingabe
# (Buchtitel, Autor, ISBN, Veröffentlichungsdatum, Bild URL und Meinung)
# zu erstellen. Es wird auch eine Debug-Ausgabe des Titels gemacht.
# --------------------------------------------------
@main.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        # Lese den Buchtitel aus dem Formular
        title = request.form.get('title')
        # Debug-Ausgabe in der Konsole
        print("Gespeicherter Titel:", title)
        
        meinung = request.form.get('meinung')
        book_author = request.form.get('author')
        isbn = request.form.get('isbn')
        published_date = request.form.get('publishedDate')
        image = request.form.get('image')  # Bild-URL (manuell oder automatisch gefüllt)
        
        new_post = Post(
            title=title,
            meinung=meinung,
            book_author=book_author,
            isbn=isbn,
            published_date=published_date,
            image=image,
            user_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        
        flash("Beitrag wurde erfolgreich erstellt.", "success")
        return redirect(url_for('main.index'))
    return render_template('add_post.html')

# --------------------------------------------------
# Endpunkt: Beitrag löschen
# Löscht einen Beitrag, wenn der aktuell eingeloggte Nutzer
# der Ersteller (Besitzer) des Beitrags ist.
# --------------------------------------------------
@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)  # Zugriff verweigern, wenn nicht der Besitzer
    db.session.delete(post)
    db.session.commit()
    flash("Beitrag wurde erfolgreich gelöscht.", "success")
    return redirect(url_for('main.profile'))

# --------------------------------------------------
# Endpunkt: Kommentar löschen
# Löscht einen Kommentar, wenn der aktuell eingeloggte Nutzer
# der Ersteller des Kommentars ist.
# --------------------------------------------------
@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash("Kommentar wurde erfolgreich gelöscht.", "success")
    return redirect(request.referrer or url_for('main.index'))

# --------------------------------------------------
# Endpunkt: Beitrag bearbeiten
# Ermöglicht es dem Nutzer, einen seiner Beiträge zu bearbeiten.
# Zunächst wird geprüft, ob der Nutzer der Besitzer ist.
# Bei POST werden die neuen Werte übernommen und gespeichert.
# --------------------------------------------------
@main.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)  # Zugriff verweigern, wenn nicht der Besitzer

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.meinung = request.form.get('meinung')
        post.book_author = request.form.get('author')
        post.isbn = request.form.get('isbn')
        post.published_date = request.form.get('publishedDate')
        post.image = request.form.get('image')
        db.session.commit()
        flash("Beitrag wurde erfolgreich aktualisiert.", "success")
        return redirect(url_for('main.profile'))
        
    return render_template('edit_post.html', post=post)
