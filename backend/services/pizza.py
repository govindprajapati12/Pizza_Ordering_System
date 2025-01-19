import os
from sqlalchemy.orm import Session
from models.models import Pizza
from schemas.pizza import PizzaCreateUpdate,PizzaResponse
from fastapi import HTTPException
from fastapi import HTTPException, UploadFile,File
from utils.dependencies import get_upload_path, admin_required

async def get_all_pizzas(db: Session):
    pizzas = db.query(Pizza).all()
    if not pizzas:
        {"Message" : "Pizza Not Found","data":[]}
    else:
        return pizzas 

async def get_pizza_by_id(pizza_id: int, db: Session):
    pizza = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")
    return pizza

async def save_image(file, pizza_name: str):
    try:
        # Get the path where the image will be stored (you can configure this as needed)
        upload_dir = get_upload_path()
        os.makedirs(upload_dir, exist_ok=True)
        
        # Get file extension and generate filename
        file_extension = file.filename.split('.')[-1]
        filename = f"{pizza_name.lower().replace(' ', '_')}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)

        # Save the image to the server
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        # Generate image URL (assuming static URL)
        image_url = f"/static/images/{filename}"
        return image_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

async def create_pizza(name: str, description: str, price: float, file: UploadFile, db: Session):
    # Check if pizza with the same name already exists
    existing_pizza = db.query(Pizza).filter(Pizza.name == name).first()
    if existing_pizza:
        raise HTTPException(status_code=400, detail="Pizza with this name already exists")
    
    # Save image and get the URL
    image_url = await save_image(file, name)

    # Create new pizza object and save it to the database
    new_pizza = Pizza(
        name=name,
        description=description,
        price=price,
        image=image_url,  # Save image URL to the database
    )
    
    db.add(new_pizza)
    db.commit()
    db.refresh(new_pizza)
    
    return new_pizza

async def update_pizza(pizza_id: int, pizza_data: PizzaCreateUpdate, db: Session):
    pizza = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")

    for key, value in pizza_data.dict().items():
        setattr(pizza, key, value)

    db.commit()
    db.refresh(pizza)
    return pizza

async def delete_pizza(pizza_id: int, db: Session):
    pizza = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")

    db.delete(pizza)
    db.commit()
    return {"message": "Pizza deleted successfully"}
