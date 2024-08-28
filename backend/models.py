from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class RoleEnum(enum.Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    paswd = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.viewer)
    videos = relationship("Video", back_populates="uploader")

class Video(Base):
    __tablename__ = "videos"

    video_id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    video_name = Column(String, nullable=False)
    video_file = Column(String, nullable=False)  # Path to the video file
    thumbnail_file = Column(String, nullable=False)  # Path to the thumbnail file

    uploader = relationship("User", back_populates="videos")