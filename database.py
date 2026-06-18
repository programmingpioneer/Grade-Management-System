import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Render pe RENDER env variable set karna, yahan backup detection bhi
    if os.getenv('RENDER') or os.getenv('RENDER_EXTERNAL_HOSTNAME') or os.getenv('PORT'):
        # /tmp/ use karo (Render free tier pe safe zone)
        db_path = '/tmp/grade_manager_cloud.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
        print(f"✅ [RENDER MODE] SQLite path: {db_path}")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Root123@localhost/grade_manager_db'
        print("✅ [LOCAL MODE] MySQL")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("✅ Tables created successfully")