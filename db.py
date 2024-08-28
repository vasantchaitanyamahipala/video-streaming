from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://vc:Tma%401999@localhost/quiz"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            print("Connection successful!")
            print("Result:", result.fetchone())
    except Exception as e:
        print("Connection failed!")
        print("Exception:", e)

if __name__ == '__main__':
    test_connection()
