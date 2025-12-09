from app.db import engine, Base, SessionLocal
from app.models import User, Post, Report, CrisisTicket, AuditLogEntry, ConditionBoard, UserRole
from app.services.board_service import seed_initial_boards
from app.services.account_service import hash_password


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
                "email": "user1@len.com",
                "display_name": "User 1",
                "role": UserRole.USER,
                "is_anonymous": False
            },
            {
                "email": "user2@len.com",
                "display_name": "User 2",
                "role": UserRole.USER,
                "is_anonymous": False
            },
            {
                "email": "mod@len.com",
                "display_name": "Moderator",
                "role": UserRole.MODERATOR,
                "is_anonymous": False
            }
        ]

        for user_data in initial_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                new_user = User(
                    email=user_data["email"],
                    hashed_password=hash_password("placeholderPassword"),
                    display_name=user_data["display_name"],
                    is_anonymous=user_data["is_anonymous"],
                    role=user_data["role"],
                    is_banned=False,
                )
                db.add(new_user)
                print(f"Created user: {user_data['display_name']}")
            else:
                print(f"User already exists: {user_data['display_name']}")
        
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()