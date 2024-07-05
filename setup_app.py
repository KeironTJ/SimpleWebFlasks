

# Assuming your Flask app and models are defined in app.py and app/models.py respectively
from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User

app = create_app()
app_context = app.app_context()
app_context.push()

def check_and_initialize_database():
    """Check if the database exists and is initialized, if not, initialize and migrate."""
    try:
        # Correct way to execute a simple query using the engine with text()
        with db.engine.connect() as connection:
            connection.execute(text('SELECT user'))
        print("Database exists and is accessible.")
    except OperationalError:
        print("Database does not exist or is not accessible. Initializing...")
        if not os.path.exists('migrations'):
            subprocess.run(["flask", "db", "init"])
        subprocess.run(["flask", "db", "migrate"])
        subprocess.run(["flask", "db", "upgrade"])
        print("Database initialized.")

def add_role(role_name):
    """Add a role to the database."""
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)
        try:
            db.session.commit()
            print(f"Added role: {role_name}")
        except IntegrityError:
            db.session.rollback()
            print(f"Failed to add role: {role_name}")

def add_user(username, email, password, role_name):
    """Add a user to the database."""
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, email=email)
        user.set_password(password)
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.role.append(role)
        db.session.add(user)
        db.session.commit()
        try:
            db.session.commit()
            print(f"Added user: {username}")
        except IntegrityError:
            db.session.rollback()
            print(f"Failed to add user: {username}")

def populate_database():
    """Populate the database with predefined data."""
    # Your existing functions to add roles and users
    add_role("admin")
    add_role("user")
    add_user(username="KeironTJ", email="abc123@abc.com", password="abc123", role_name="admin")
    # Add more data population functions here as needed

if __name__ == "__main__":
    check_and_initialize_database()
    populate_database()


