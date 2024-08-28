Video Streaming and User Authentication API
Overview

This project is a FastAPI-based application that allows users to sign up, log in, upload videos, and stream videos. The application uses JWT (JSON Web Token) for secure user authentication and implements role-based access control (RBAC) to manage user permissions. Additionally, the application generates video thumbnails upon upload and supports video streaming with range requests.
Features

    User Authentication: Secure login and signup using JWT.
    Role-Based Access Control (RBAC): Different user roles such as admin and viewer to control access to resources.
    Video Upload: Admin users can upload videos.
    Thumbnail Generation: Automatically generate and store a thumbnail for each uploaded video.
    Video Streaming: Stream videos directly from the server with support for range requests.

Project Structure

    auth.py: Contains functions for password hashing, JWT creation, and user authentication.
    db.py: Manages the database connection and provides utility functions for database sessions.
    main.py: The main FastAPI application that defines the API endpoints.
    models.py: Defines the database models for User and Video.
    schemas.py: Defines Pydantic schemas for data validation.
    requirements.txt: Lists all the dependencies required to run the project.

Installation
Prerequisites

    Python 3.8 or higher
    MySQL database

Setup

    Clone the repository:

    bash

git clone https://github.com/your-username/video-streaming-api.git
cd video-streaming-api

Create and activate a virtual environment:

bash

python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`

Install dependencies:

bash

pip install -r requirements.txt

Set up the database:

    Update the SQLALCHEMY_DATABASE_URL in db.py with your MySQL credentials.
    Run the database migrations (if any) to set up your tables.

Run the FastAPI server:

bash

    uvicorn main:app --reload

API Endpoints
User Authentication

    POST /signup: Register a new user.
        Request Body:

        json

{
"email": "user@example.com",
"paswd": "password",
"name": "User Name",
"admin": 1
}

Response:

json

    {
        "message": "User created successfully"
    }

POST /token: Login and receive a JWT token.

    Request Body (form data):
        username: User's email
        password: User's password
    Response:

    json

    {
        "access_token": "<JWT>",
        "token_type": "bearer"
    }

GET /users/me: Get details about the currently logged-in user.

    Headers:
        Authorization: Bearer <JWT>
    Response:

    json

        {
            "email": "user@example.com",
            "name": "User Name",
            "admin": 1
        }

Video Management

    POST /upload_video: Upload a new video (Admin only).
        Headers:
            Authorization: Bearer <JWT>
        Request Body (form data):
            video_name: Name of the video
            video_file: The video file to upload
        Response:

        json

        {
            "filename": "uploaded_filename.mp4",
            "message": "Video uploaded and thumbnail generated successfully"
        }

    GET /stream_video/{video_name}: Stream a video by name.
        Response:
            The video content is streamed with appropriate Range headers.

Running the Application

    Start the server:

    bash

    uvicorn main:app --reload

    Access the API:
        Use tools like Postman or Curl to interact with the API endpoints.
        You can also create a simple HTML page to display videos using the /stream_video/{video_name} endpoint.

Example HTML for Video Playback

html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Watch Video</title>
</head>
<body>
    <h1>Watch Video</h1>
    <video width="640" height="360" controls>
        <source src="http://localhost:8000/stream_video/example" type="video/mp4">
        Your browser does not support the video tag.
    </video>
</body>
</html>

Dependencies

Here is a list of all dependencies used in this project, as specified in the requirements.txt file:

plaintext

fastapi[all]
uvicorn[standard]
sqlalchemy
databases[sqlite]
alembic
pymysql
cryptography
python-multipart
python-jose[cryptography]
passlib[bcrypt]
moviepy
