from app import app
from models import User, Admin,db

with app.app_context():
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('Password2025')  # Change this to a secure password
        db.session.add(admin)
        db.session.commit()

        # Create the corresponding Admin profile
        admin_profile = Admin(user=admin)
        db.session.add(admin_profile)
        db.session.commit()

        print("Admin user created successfully!")
    else:
        print("An admin user already exists.")