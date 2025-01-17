from fastapi import FastAPI
from routes import auth, pizza, toppings, coupons, cart, order,users,email
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (e.g., pizza images or other assets)
static_dir = os.path.join(os.path.dirname(__file__), "static")  # Adjust to your folder structure
if not os.path.exists(static_dir):
    print(f"Warning: The static directory '{static_dir}' does not exist!")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to Pizza Ordering System!"}

# Include the routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(pizza.router, prefix="/api", tags=["Pizzas"])
app.include_router(toppings.router, prefix="/api", tags=["Toppings"])
app.include_router(coupons.router, prefix="/api", tags=["Coupons"])
app.include_router(cart.router, prefix="/api", tags=["Cart"])
app.include_router(order.router, prefix="/api", tags=["Order"])
app.include_router(email.router, prefix="/api", tags=["Email"])