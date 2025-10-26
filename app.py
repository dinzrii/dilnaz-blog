from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # максимум 2 МБ
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Проверяем наличие папки для базы
if not os.path.exists('instance'):
    os.makedirs('instance')

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db) 

# Модель Post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Post {self.id} - {self.title}>'

# Главная страница
@app.route('/')
def index():
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('index.html', posts=posts)

# Добавить пост
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        image = request.files.get('image')
        filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_post = Post(title=title, content=content, image_filename=filename)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_post.html')


# Просмотр поста
@app.route('/post/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    return render_template('post_detail.html', post=post)

# Редактировать пост
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.author = request.form['author']
        db.session.commit()
        return redirect(url_for('post_detail', id=post.id))
    return render_template('edit_post.html', post=post)

# Удалить пост
@app.route('/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

# Страница "Обо мне"
@app.route('/about')
def about():
    return render_template('about.html')

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # максимум 2 МБ
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(debug=False)

@app.cli.command("fix_authors")
def fix_authors():
    posts = Post.query.filter_by(author="Anonymous").all()
    for p in posts:
        p.author = "Dilnaz"
    db.session.commit()
    print("✅ All 'Anonymous' authors replaced with 'Dilnaz'")
