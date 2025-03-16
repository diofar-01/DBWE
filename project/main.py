from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Post, Comment  # Comment importieren

main = Blueprint('main', __name__)

# Startseite: für alle sichtbar, zeigt alle Beiträge und verarbeitet Kommentar-POSTs
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
    
    # GET-Anfrage: Alle Beiträge laden
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

# Profilseite: zeigt nur die eigenen Beiträge des Nutzers
@main.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', name=current_user.name, posts=posts)

# Route zum Hinzufügen eines neuen Beitrags (ohne Kommentar-Feld)
@main.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form.get('title')
        meinung = request.form.get('meinung')
        
        new_post = Post(
            title=title,
            meinung=meinung,
            user_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        
        return redirect(url_for('main.index'))
    return render_template('add_post.html')

# Neue Route zum Löschen eines Beitrags – nur der Besitzer darf löschen
@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)  # Zugriff verweigern, wenn der Nutzer nicht der Besitzer ist
    db.session.delete(post)
    db.session.commit()
    flash("Beitrag wurde erfolgreich gelöscht.", "success")
    return redirect(url_for('main.profile'))
