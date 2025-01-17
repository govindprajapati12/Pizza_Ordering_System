from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, List
from sqlalchemy.exc import SQLAlchemyError
from db.config import Base
from .error import CustomError

# Helper function to handle database commits
def commit(db: Session):
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomError(f"Database commit failed: {str(e)}")


# Reusable function to get a record by ID
def get_by_id(model: Any, db: Session, record_id: int) -> Optional[Any]:
    try:
        record = db.query(model).filter(model.id == record_id).first()
        if not record:
            raise CustomError(f"{model.__name__} not found with ID: {record_id}")
        return record
    except SQLAlchemyError as e:
        raise CustomError(f"Error fetching {model.__name__} with ID {record_id}: {str(e)}")


# Reusable function to create a new record
def create(model: Any, db: Session, data: Dict) -> Any:
    try:
        new_record = model(**data)  # Assuming model is a SQLAlchemy declarative class
        db.add(new_record)
        commit(db)
        return new_record
    except SQLAlchemyError as e:
        raise CustomError(f"Error creating {model.__name__}: {str(e)}")


# Reusable function to update a record
def update(model: Any, db: Session, record_id: int, data: Dict) -> Any:
    try:
        # Get the record by its ID
        record = get_by_id(model, db, record_id)
        
        # Only update the fields provided in the data
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        # Commit the changes to the database
        commit(db)
        return record
    except SQLAlchemyError as e:
        raise CustomError(f"Error updating {model.__name__} with ID {record_id}: {str(e)}")


# Reusable function to delete a record
def delete(model: Any, db: Session, record_id: int) -> bool:
    try:
        record = get_by_id(model, db, record_id)
        db.delete(record)
        commit(db)
        return True
    except SQLAlchemyError as e:
        raise CustomError(f"Error deleting {model.__name__} with ID {record_id}: {str(e)}")


# Function for applying filters
def apply_filters(query: Any, filters: Dict) -> List[Any]:
    try:
        for key, value in filters.items():
            if hasattr(query, key):
                query = query.filter(getattr(query, key) == value)
        return query.all()
    except SQLAlchemyError as e:
        raise CustomError(f"Error applying filters: {str(e)}")
