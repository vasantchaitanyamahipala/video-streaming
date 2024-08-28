from sqlalchemy import Column, Integer, String, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    admin = Column(Integer, default=False)
    paswd = Column(String, nullable=False)
    videos = relationship("Video", back_populates="uploader")

class Video(Base):
    __tablename__ = "videos"

    video_id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    video_name = Column(String, nullable=False)
    video_file = Column(BLOB)

    # Relationship to access the user who uploaded the video
    uploader = relationship("User", back_populates="videos")
