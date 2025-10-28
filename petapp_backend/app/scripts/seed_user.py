from app.db import SessionLocal
from app.models import User

def main():
    s = SessionLocal()
    try:
        exists = s.query(User).filter_by(id=1).first()
        if not exists:
            s.add(User(id=1, email='admin@local', password_hash='x', display_name='Admin'))
            s.commit()
            print("Seeded user id=1")
        else:
            print("User id=1 exists")
    finally:
        s.close()

if __name__ == "__main__":
    main()
