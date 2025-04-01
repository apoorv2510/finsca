from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import datetime

# FastAPI instance
app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./sports_kits.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Secret key for JWT
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class KitOrder(Base):
    __tablename__ = "kit_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    team_name = Column(String, index=True)
    color = Column(String, index=True)
    size = Column(String, index=True)
    status = Column(String, default="Pending")  # Possible statuses: Pending, In Progress, Shipped, Delivered

Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class KitOrderCreate(BaseModel):
    team_name: str
    color: str
    size: str

class KitOrderUpdate(BaseModel):
    status: str

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create User
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

# Login User and Get Token
@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate JWT token
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    token = jwt.encode({"sub": user.username, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

# Get Current User from Token
def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Place an Order for a Sports Kit
@app.post("/orders/")
def create_order(order: KitOrderCreate, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    new_order = KitOrder(user_id=user.id, team_name=order.team_name, color=order.color, size=order.size)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"message": "Order placed successfully", "order_id": new_order.id}

# Get All Orders of the Logged-in User
@app.get("/orders/")
def get_orders(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    orders = db.query(KitOrder).filter(KitOrder.user_id == user.id).all()
    return orders

# Update Order Status (Admin Use Case)
@app.put("/orders/{order_id}")
def update_order_status(order_id: int, order_update: KitOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(KitOrder).filter(KitOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = order_update.status
    db.commit()
    db.refresh(order)
    return {"message": "Order status updated successfully"}

# Run Server: uvicorn main:app --reload
