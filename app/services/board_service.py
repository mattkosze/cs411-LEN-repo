from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

INITIAL_BOARDS = [
    {"name": "Diabetes", "description": "Support and discussion for diabetes management"},
    {"name": "Mental Health", "description": "A safe space for mental health support"},
    {"name": "Autoimmune", "description": "Connecting those with autoimmune conditions"},
    {"name": "Chronic Pain", "description": "Sharing experiences and coping strategies"},
    {"name": "Heart Disease", "description": "Cardiovascular health and support"},
    {"name": "Cancer Support", "description": "Supporting each other through treatment"},
    {"name": "Arthritis", "description": "Living with arthritis"},
    {"name": "Asthma & COPD", "description": "Respiratory health community"},
]

def list_boards(db: Session):
    return db.query(models.ConditionBoard).order_by(models.ConditionBoard.id.asc()).all()

def create_board(db: Session, data: schemas.ConditionBoardCreate):
    existing = db.query(models.ConditionBoard).filter(models.ConditionBoard.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board name already exists")
    board = models.ConditionBoard(name=data.name, description=data.description)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board

def seed_initial_boards(db: Session):
    count = db.query(models.ConditionBoard).count()
    if count == 0:
        for b in INITIAL_BOARDS:
            board = models.ConditionBoard(name=b["name"], description=b["description"])
            db.add(board)
        db.commit()
        print("Seeded initial condition boards")
    else:
        print("Condition boards already present; skipping seed")