from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas import UserCreate


app = FastAPI()

@app.get('/')
async def root():
    return "this is the default path"

@app.get('/login')
async def login(email: str, paswd: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and user.paswd==paswd and user.admin==1:
            return f"{user.name} u logged in as an admin"
        elif user and user.paswd == paswd:
            return {"message": "Congrats, logged in!"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.post('/signup')
async def signup(user:UserCreate,  db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        paswd=user.paswd,
        name=user.name,
        admin=user.admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}
   