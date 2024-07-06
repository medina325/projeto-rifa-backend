import os
from sqlalchemy.orm import Session

def clean_failed_rifa_creation(db: Session, file_path):
    db.rollback()
    if file_path.is_file():
        os.remove(file_path)
