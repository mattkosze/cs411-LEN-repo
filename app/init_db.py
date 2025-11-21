from app.db import engine, Base, SessionLocal
from app.models import User, Post, Report, CrisisTicket, AuditLogEntry, ConditionBoard, UserRole
from app.services.board_service import seed_initial_boards

# Create all tables
def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    # Seed boards if empty
    db = SessionLocal()
    try:
        # Seed boards
        seed_initial_boards(db)
        # Seed a dummy guest user if none exist
        if db.query(User).count() == 0:
            guest = User(
                email=None,
                hashedpassword=None,
                displayname="Guest",
                isanonymous=True,
                role=UserRole.USER,
                isbanned=False,
            )
            db.add(guest)
            db.commit()
            print("Created guest user")
        else:
            print("Users already present; skipping guest creation")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()