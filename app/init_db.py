from app.db import engine, Base
from app.models import User, Post, Report, CrisisTicket, AuditLogEntry

# Create all tables
def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    init_db()