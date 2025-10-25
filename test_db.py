from app import app, db, Post
from sqlalchemy import text

with app.app_context():
    posts = Post.query.all()
    for p in posts:
        print(p.id, p.title, p.author)
