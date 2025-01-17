from sqlalchemy.orm import Session
from models.models import Topping
from schemas.toppings import ToppingCreate
from fastapi import HTTPException

async def create_new_topping(topping: ToppingCreate, db: Session):
    existing_topping = db.query(Topping).filter(Topping.name == topping.name).first()
    if existing_topping:
        raise HTTPException(status_code=400, detail="Topping already exists")

    new_topping = Topping(name=topping.name, price=topping.price)
    db.add(new_topping)
    db.commit()
    db.refresh(new_topping)
    return new_topping

async def get_all_toppings(db: Session):
    return db.query(Topping).all()

async def get_topping_by_id(topping_id: int, db: Session):
    topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not topping:
        raise HTTPException(status_code=404, detail="Topping not found")
    return topping

async def update_existing_topping(topping_id: int, topping: ToppingCreate, db: Session):
    existing_topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not existing_topping:
        raise HTTPException(status_code=404, detail="Topping not found")

    existing_topping.name = topping.name
    existing_topping.price = topping.price
    db.commit()
    db.refresh(existing_topping)
    return existing_topping

async def delete_topping(topping_id: int, db: Session):
    topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not topping:
        raise HTTPException(status_code=404, detail="Topping not found")

    db.delete(topping)
    db.commit()
    return {"message": "Topping deleted successfully"}
