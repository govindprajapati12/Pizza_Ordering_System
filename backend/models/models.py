from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric, Enum, Text,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Date
from db.config import Base

# User Model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    role = Column(Enum('admin', 'user', name='user_roles'))
    created_at = Column(DateTime, server_default=func.now())

    orders = relationship("Order", back_populates="user")
    cart = relationship("Cart", uselist=False, back_populates="user")
    coupon_usages = relationship("CouponUsage", back_populates="user")

class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())
    total_price = Column(Float, default=0.0)  # Stores the total price of the cart
    discounted_price = Column(Float, default=0.0)  # Stores the price after applying the coupon

    user = relationship("User", back_populates="cart")
    cart_items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

# CartItem Model
class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    pizza_id = Column(Integer, ForeignKey('pizzas.id'))
    quantity = Column(Integer)

    cart = relationship("Cart", back_populates="cart_items")
    pizza = relationship("Pizza", back_populates="cart_items")
    cart_toppings = relationship("CartTopping", back_populates="cart_item", cascade="all, delete-orphan")

# CartTopping Model
class CartTopping(Base):
    __tablename__ = 'cart_toppings'

    id = Column(Integer, primary_key=True)
    cart_item_id = Column(Integer, ForeignKey('cart_items.id'))
    topping_id = Column(Integer, ForeignKey('toppings.id'))
    quantity = Column(Integer)

    cart_item = relationship("CartItem", back_populates="cart_toppings")
    topping = relationship("Topping", back_populates="cart_toppings")

# Pizza Model
class Pizza(Base):
    __tablename__ = 'pizzas'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    image = Column(String(255))
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())

    cart_items = relationship("CartItem", back_populates="pizza")
    order_items = relationship("OrderItem", back_populates="pizza")

# Topping Model
class Topping(Base):
    __tablename__ = 'toppings'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())

    cart_toppings = relationship("CartTopping", back_populates="topping")
    order_toppings = relationship("OrderTopping", back_populates="topping")

# Order Model
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('Received', 'Preparing', 'Baking', 'Ready for Pickup', 'Completed', name='order_status'))
    total_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    order_coupons = relationship("OrderCoupon", back_populates="order", cascade="all, delete-orphan")

# OrderItem Model
class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    pizza_id = Column(Integer, ForeignKey('pizzas.id'))
    quantity = Column(Integer)

    order = relationship("Order", back_populates="order_items")
    pizza = relationship("Pizza", back_populates="order_items")
    order_toppings = relationship("OrderTopping", back_populates="order_item", cascade="all, delete-orphan")

# OrderCoupon Model
class OrderCoupon(Base):
    __tablename__ = 'order_coupons'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    coupon_id = Column(Integer, ForeignKey('coupons.id'))

    order = relationship("Order", back_populates="order_coupons")
    coupon = relationship("Coupon", back_populates="order_coupons")

# OrderTopping Model
class OrderTopping(Base):
    __tablename__ = 'order_toppings'

    id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey('order_items.id'))
    topping_id = Column(Integer, ForeignKey('toppings.id'))
    quantity = Column(Integer)

    order_item = relationship("OrderItem", back_populates="order_toppings")
    topping = relationship("Topping", back_populates="order_toppings")

# Coupon Model
class Coupon(Base):
    __tablename__ = 'coupons'

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    discount = Column(Numeric(5, 2))
    expiration_date = Column(Date)
    usage_limit = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    coupon_usages = relationship("CouponUsage", back_populates="coupon")
    order_coupons = relationship("OrderCoupon", back_populates="coupon")

# CouponUsage Model
class CouponUsage(Base):
    __tablename__ = "user_coupon_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    used_at = Column(DateTime, nullable=True)  # Timestamp of usage
    usage_limit = Column(Integer, default=1)   # Indicates if the coupon can be reused (1 = not used, 0 = used)

    # Relationships
    user = relationship("User", back_populates="coupon_usages")
    coupon = relationship("Coupon", back_populates="coupon_usages")


