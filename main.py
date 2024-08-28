from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User

app = FastAPI()

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