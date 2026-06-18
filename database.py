import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Configure and initialize the database for the Flask app."""
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Cloud (Render) vs local database selection
    if os.getenv('RENDER'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'grade_manager_cloud.db')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Root123@localhost/grade_manager_db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Bind SQLAlchemy to the app
    db.init_app(app)

    # Create tables automatically
    with app.app_context():
        db.create_all()