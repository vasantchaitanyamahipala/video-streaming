from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from auth import get_current_user, create_access_token, get_password_hash, verify_password, get_current_active_user
from db import get_db
from models import User, Video
from schemas import UserCreate
from moviepy.editor import VideoFileClip
import shutil
import os

app = FastAPI()

@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.paswd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", response_model=dict)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.paswd)
    new_user = User(
        email=user.email,
        paswd=hashed_password,
        name=user.name,
        admin=user.admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.get("/users/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {"email": current_user.email, "name": current_user.name, "admin": current_user.admin}

@app.post("/upload_video", response_model=dict)
async def upload_video(
    video_name: str,
    video_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied: Only admins can upload videos")

    video_name_check = db.query(Video).filter(Video.video_name == video_name).first()
    if video_name_check:
        raise HTTPException(status_code=403, detail="A video with this name already exists")

    file_location = f"videos/{video_name}.mp4"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)

    thumbnail_location = f"thumbnails/{video_name}.png"
    with VideoFileClip(file_location) as clip:
        clip.save_frame(thumbnail_location, t=1.00)  # Save a frame at 1 second

    new_video = Video(user_email=current_user.email, video_name=video_name, video_file=file_location, thumbnail_file=thumbnail_location)
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return {"filename": video_file.filename, "message": "Video uploaded and thumbnail generated successfully"}

@app.get("/stream_video/{video_name}", response_class=StreamingResponse)
async def stream_video(video_name: str, request: Request, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.video_name == video_name).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video_path = video.video_file
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    file_size = os.stat(video_path).st_size
    range_header = request.headers.get('Range', None)
    if range_header:
        range_str = range_header.strip().split("=")[-1]
        range_start, range_end = range_str.split("-")
        range_start = int(range_start)
        range_end = int(range_end) if range_end else file_size - 1
    else:
        range_start = 0
        range_end = file_size - 1

    def iter_file():
        with open(video_path, "rb") as video_file:
            video_file.seek(range_start)
            chunk_size = 1024 * 1024  # 1MB
            bytes_remaining = range_end - range_start + 1
            while bytes_remaining > 0:
                bytes_to_read = min(chunk_size, bytes_remaining)
                chunk = video_file.read(bytes_to_read)
                if not chunk:
                    break
                yield chunk
                bytes_remaining -= len(chunk)

    response = StreamingResponse(iter_file(), media_type="video/mp4")
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Range"] = f"bytes {range_start}-{range_end}/{file_size}"
    return response
