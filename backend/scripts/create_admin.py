"""
Create the first admin user safely.

Usage examples:
  python backend/scripts/create_admin.py --username admin1 --email admin@example.com --full-name "System Admin"
  python backend/scripts/create_admin.py --username admin1 --email admin@example.com --full-name "System Admin" --password "StrongPass#123"
"""
import argparse
import getpass
import os
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import SessionLocal
from models import User
from auth import get_password_hash
from enums import UserRole, DoctorApprovalStatus
from schemas.user import validate_password_strength


def prompt_password() -> str:
    while True:
        password = getpass.getpass("Enter admin password: ")
        confirm = getpass.getpass("Confirm admin password: ")
        if password != confirm:
            print("Passwords do not match. Please try again.")
            continue
        try:
            validate_password_strength(password)
            return password
        except ValueError as exc:
            print(f"Invalid password: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Create admin user safely")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--full-name", required=True, help="Admin full name")
    parser.add_argument("--password", required=False, help="Admin password (optional; prompt if omitted)")
    args = parser.parse_args()

    password = args.password or prompt_password()
    if args.password:
        try:
            validate_password_strength(password)
        except ValueError as exc:
            raise SystemExit(f"Invalid password: {exc}")

    db = SessionLocal()
    try:
        existing_username = db.query(User).filter(User.username == args.username).first()
        if existing_username:
            raise SystemExit(f"Username already exists: {args.username}")

        existing_email = db.query(User).filter(User.email == args.email).first()
        if existing_email:
            raise SystemExit(f"Email already exists: {args.email}")

        admin_user = User(
            username=args.username,
            email=args.email,
            full_name=args.full_name,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN.value,
            approval_status=DoctorApprovalStatus.APPROVED.value,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("Admin user created successfully.")
        print(f"user_id: {admin_user.user_id}")
        print(f"username: {admin_user.username}")
        print(f"email: {admin_user.email}")
        print(f"role: {admin_user.role}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
