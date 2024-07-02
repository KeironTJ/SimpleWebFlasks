from app import app as application  # Rename to avoid potential conflicts
from app.models import db, Role, User, UserRoles
from sqlalchemy.exc import IntegrityError

# Push an application context
with application.app_context():
    # Function to add roles
    def add_role(role_name):
        role = Role(name=role_name)
        db.session.add(role)
        try:
            db.session.commit()
            print(f"Added role: {role_name}")
        except IntegrityError:
            db.session.rollback()
            print(f"Role {role_name} already exists.")

    # Function to assign a role to a user
    def assign_role_to_user(username, role_name):
        user = User.query.filter_by(username=username).first()
        role = Role.query.filter_by(name=role_name).first()
        if user and role:
            user_role = UserRoles(user_id=user.id, role_id=role.id)
            db.session.add(user_role)
            try:
                db.session.commit()
                print(f"Assigned role '{role_name}' to user '{username}'.")
            except IntegrityError:
                db.session.rollback()
                print(f"User '{username}' already has role '{role_name}'.")
        else:
            print(f"User or Role not found. User: {username}, Role: {role_name}")

    # Example usage
    if __name__ == "__main__":
        # Add roles
        add_role("admin")
        add_role("user")  # Add more roles as needed

        # Assign roles to users
        assign_role_to_user("KeironTJ", "admin")  # Replace "adminuser" with your admin username
        # Repeat for other users and roles as needed