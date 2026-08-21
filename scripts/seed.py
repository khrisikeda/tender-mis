"""
Run once against a fresh database:

    python -m scripts.seed

Creates all tables (dev convenience -- use Alembic migrations in production),
seeds the 7 roles from RoleName, and creates one initial admin user so you
can log in and start creating the rest of your team.
"""
import getpass
import sys

from app.database import Base, engine, SessionLocal
from app.core.enums import RoleName
from app.core.security import hash_password
from app.models.user import User, Role
import app.models  # noqa: F401  (ensures all models are registered)


ROLE_DESCRIPTIONS = {
    RoleName.ADMIN: "Full system access, including source and user management.",
    RoleName.MANAGEMENT: "Dashboard, bid decisions, financial reports, all analytics.",
    RoleName.SALES: "Tender discovery, customer info, bid preparation.",
    RoleName.BIOMEDICAL_ENGINEER: "Technical analysis, spec matching, compliance matrix.",
    RoleName.PROCUREMENT: "Supplier quotations, manufacturer authorization, sourcing.",
    RoleName.FINANCE: "Financial requirements, securities, cost analysis.",
    RoleName.VIEWER: "Read-only access.",
}


def main():
    print("Creating tables (if they don't already exist)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding roles...")
        for role_name, description in ROLE_DESCRIPTIONS.items():
            existing = db.query(Role).filter(Role.name == role_name.value).first()
            if not existing:
                db.add(Role(name=role_name.value, description=description))
        db.commit()
        print(f"  {len(ROLE_DESCRIPTIONS)} roles ensured.")

        existing_admin = db.query(User).join(Role).filter(Role.name == RoleName.ADMIN.value).first()
        if existing_admin:
            print(f"An admin user already exists ({existing_admin.email}). Skipping admin creation.")
            return

        print("\nNo admin user found -- let's create the first one.")
        full_name = input("Admin full name: ").strip()
        email = input("Admin email: ").strip()
        password = getpass.getpass("Admin password: ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("Passwords did not match. Aborting.", file=sys.stderr)
            sys.exit(1)

        admin_role = db.query(Role).filter(Role.name == RoleName.ADMIN.value).first()
        admin_user = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role_id=admin_role.id,
        )
        db.add(admin_user)
        db.commit()
        print(f"\nAdmin user '{email}' created. You can now log in via POST /auth/login.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
