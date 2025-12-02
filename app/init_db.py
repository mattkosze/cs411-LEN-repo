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
        # Seed initial users
        initial_users = [
            {
                "email": "user1@example.com",
                "displayname": "User 1",
                "role": UserRole.USER,
                "isanonymous": False
            },
            {
                "email": "user2@example.com",
                "displayname": "User 2",
                "role": UserRole.USER,
                "isanonymous": False
            },
            {
                "email": "mod@example.com",
                "displayname": "Moderator",
                "role": UserRole.MODERATOR,
                "isanonymous": False
            }
        ]

        for user_data in initial_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                new_user = User(
                    email=user_data["email"],
                    hashedpassword="hashed_password_placeholder", # In a real app, hash this
                    displayname=user_data["displayname"],
                    isanonymous=user_data["isanonymous"],
                    role=user_data["role"],
                    isbanned=False,
                )
                db.add(new_user)
                print(f"Created user: {user_data['displayname']}")
            else:
                print(f"User already exists: {user_data['displayname']}")
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()