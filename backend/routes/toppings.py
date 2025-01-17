from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.toppings import ToppingCreate, ToppingResponse
from services.toppings import (
    create_new_topping,
    get_all_toppings,
    get_topping_by_id,
    update_existing_topping,
    delete_topping,
)
from db.config import get_db
from utils.dependencies import admin_required

router = APIRouter(prefix="/toppings")

@router.post("/",dependencies=[Depends(admin_required)])
async def create_topping(topping: ToppingCreate, db: Session = Depends(get_db)):
    new_topping = await create_new_topping(topping, db)
    return {"Message":"Topping Created Successfull","data":new_topping}

@router.get("/")
async def list_toppings(db: Session = Depends(get_db)):
    toppings = await get_all_toppings(db)
    return {"Message":"Toppings geted Successfull","data":toppings}

@router.get("/{topping_id}")
async def get_topping(topping_id: int, db: Session = Depends(get_db)):
    topping = await get_topping_by_id(topping_id, db)
    return {"Message":" Topping geted Successfull","data":topping}


@router.put("/{topping_id}",dependencies=[Depends(admin_required)])
async def update_topping(topping_id: int, topping: ToppingCreate, db: Session = Depends(get_db)):
    updated_topping = await update_existing_topping(topping_id, topping, db)
    return {"Message":"Topping Updated Successfull","data":updated_topping}

@router.delete("/{topping_id}", response_model=dict,dependencies=[Depends(admin_required)])
async def remove_topping(topping_id: int, db: Session = Depends(get_db)):
    deleted_topping = await delete_topping(topping_id, db)
    return {"Message":"Topping Successfull","data":deleted_topping}
