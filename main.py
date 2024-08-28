from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User, Video
from schemas import UserCreate
from fastapi.responses import FileResponse
import os


app = FastAPI()

@app.get('/')
async def root(db: Session = Depends(get_db)):
    try:
        videos = db.query(Video).all()
        
        if not videos:
            return {"message": "No videos at all"}
        
        video_names = [video.video_name for video in videos]
        
        return {"videos": video_names}

    except HTTPException as e:
        raise e  
    
    except Exception as e:
        
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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


import os

@app.post('/upload_video')
async def upload_video(user_email: str, video_name: str, video_file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.admin != 1:
        raise HTTPException(status_code=403, detail="Permission denied: Only admins can upload videos")
    
    video_name_check = db.query(Video).filter(Video.video_name == video_name).first()

    if video_name_check:
        raise HTTPException(status_code=403, detail="Permission denied: a video with same name exists")
    else:
        # Save the file to the filesystem
        file_location = f"videos/{video_name}.mp4"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        # Store the file path in the database
        new_video = Video(user_email=user.email, video_name=video_name, video_file=file_location)
        db.add(new_video)
        db.commit()
        db.refresh(new_video)

        return {"filename": video_file.filename, "message": "Video uploaded successfully"}
        
@app.post('/search_videos')
async def search_videos(video_name: str, db: Session = Depends(get_db)):
    try:
        video = db.query(Video).filter(Video.video_name == video_name).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        video_path = video.video_file

        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found on disk")

        return FileResponse(video_path)
    
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions to send them as responses
    
    except Exception as e:
        # Log the exception if you have a logger, or print it out for now
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    