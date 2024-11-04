from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

# Konfigurasi Flask
app = Flask(__name__)

# Konfigurasi Database MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/plnfotodb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Direktori Penyimpanan Foto
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Inisialisasi Database
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Model Tabel Database
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_picture = db.Column(db.String(120), nullable=True)  # Path foto
    # phone_number = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return f'<User {self.name}>'

# Route Utama
@app.route('/')
def index():
    users = User.query.all()  # Mengambil semua data pengguna
    return render_template('index.html', users=users)

# Route untuk Menambahkan Pengguna Baru dengan Foto
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    profile_picture = request.files['profile_picture']

    # Simpan foto jika ada unggahan
    if profile_picture and allowed_file(profile_picture.filename):
        picture_filename = secure_filename(profile_picture.filename)
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_filename)
        profile_picture.save(picture_path)
        new_user = User(name=name, email=email, profile_picture=picture_filename)
    else:
        new_user = User(name=name, email=email)

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

# Route untuk Menghapus Pengguna
@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('index'))

# Route untuk Memperbarui Pengguna
@app.route('/update/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get(id)
    if user:
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Membuat tabel jika belum ada
    app.run(debug=True)
