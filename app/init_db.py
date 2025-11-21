from app.db import engine, Base, SessionLocal
from app.models import User, Post, Report, CrisisTicket, AuditLogEntry, ConditionBoard
from app.services.board_service import seed_initial_boards

# Create all tables
def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    # Seed boards if empty
    db = SessionLocal()
    try:
        seed_initial_boards(db)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()