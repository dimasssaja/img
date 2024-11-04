from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()  

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['ALLOWED_EXTENSIONS'] = set(os.getenv("ALLOWED_EXTENSIONS").split(","))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Database model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_picture = db.Column(db.String(120), nullable=True)  # Path to the picture

    def __repr__(self):
        return f'<User {self.name}>'

# Main route
@app.route('/')
def index():
    users = User.query.all()  # Fetch all user data
    return render_template('index.html', users=users)

# Route to add a new user with a picture
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    profile_picture = request.files['profile_picture']

    # Save picture if uploaded
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

# Route to delete a user
@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('index'))

# Route to update user information
@app.route('/update/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get(id)
    if user:
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
    return redirect(url_for('index'))

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
