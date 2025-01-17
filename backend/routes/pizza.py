from fastapi import APIRouter, Depends, HTTPException ,File, UploadFile,Body
from sqlalchemy.orm import Session
from db.config import get_db
from services.pizza import (
    get_all_pizzas,
    get_pizza_by_id,
    create_pizza,
    update_pizza,
    delete_pizza,
)
from schemas.pizza import PizzaCreateUpdate, PizzaResponse
from utils.dependencies import admin_required

router = APIRouter()

@router.get("/pizzas")
async def list_pizzas(db: Session = Depends(get_db)):
    pizzas = await get_all_pizzas(db)
    return {"Message" : "Pizza geted successfully","data":pizzas}

@router.get("/pizzas/{pizza_id}")
async def retrieve_pizza(pizza_id: int, db: Session = Depends(get_db)):
    pizza = await get_pizza_by_id(pizza_id, db)
    return {"Message" : "Pizza geted successfully","data":pizza}

@router.post("/pizzas",dependencies=[Depends(admin_required)])
async def create_new_pizza(
    name: str = Body(...),
    description: str = Body(...),
    price: float = Body(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Create new pizza and get the saved pizza ORM object
    new_pizza = await create_pizza(name, description, price, file, db)
    
    # Return a structured response with a message and data
    return {
        "message": "Pizza created successfully.",
        "data": new_pizza
    }

@router.put("/pizzas/{pizza_id}", dependencies=[Depends(admin_required)])
async def update_existing_pizza(pizza_id: int, pizza: PizzaCreateUpdate, db: Session = Depends(get_db)):
    updated_pizza = await update_pizza(pizza_id, pizza, db)
    return {"Message" : "Pizza Updated successfully","data":updated_pizza}


@router.delete("/pizzas/{pizza_id}", dependencies=[Depends(admin_required)])
async def delete_existing_pizza(pizza_id: int, db: Session = Depends(get_db)):
    deleted_pizza = await delete_pizza(pizza_id, db)
    return {"Message" : "Pizza Deleted successfully","data":deleted_pizza}
