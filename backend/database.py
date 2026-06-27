from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    database_url = os.getenv('DATABASE_URL', 'sqlite:///exam_platform.db')
    # Fix for PostgreSQL on Render (replace postgres:// with postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

        from models import User, SiteSettings, Category

        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                username='admin',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        default_categories = [
            ('Permis auto', 'Întrebări pentru obținerea permisului de conducere'),
            ('Examen medical', 'Teste pentru admiterea la facultăți de medicină'),
            ('BAC', 'Întrebări pregătitoare pentru examenul de bacalaureat'),
            ('Drept', 'Teste de drept constituțional, civil, penal')
        ]
        for name, description in default_categories:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, description=description))
        db.session.commit()

        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings(
                site_name='Platformă de Testare',
                logo_url='',
                welcome_message='Bine ai venit pe platforma noastră de testare!'
            )
            db.session.add(settings)
            db.session.commit()
