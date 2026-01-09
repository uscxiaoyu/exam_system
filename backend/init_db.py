from backend.db.session import engine, SessionLocal
from backend.db.base import Base

# Import all models to ensure they are registered with Base.metadata
from backend.models.user import User
from backend.models.school import School
from backend.models.exam import Exam
from backend.models.exam_record import ExamRecord
from backend.models.class_ import Class
from backend.models.student import Student
from backend.models.section import ExamSection

from backend.core.security import get_password_hash

def init_db():
    print("Creating tables...")
    
    # Retry loop to wait for DB to be ready
    import time
    from sqlalchemy.exc import OperationalError
    
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            # Try to create tables (this involves connecting)
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
            break
        except OperationalError as e:
            if i < max_retries - 1:
                print(f"Database not ready yet, retrying in {retry_interval}s... ({i+1}/{max_retries})")
                time.sleep(retry_interval)
            else:
                print(f"Failed to connect to database after {max_retries} retries.")
                raise e

    db = SessionLocal()

    # Init School
    school = db.query(School).filter(School.name == "Default School").first()
    if not school:
        print("Creating Default School...")
        school = School(name="Default School", description="System Default School")
        db.add(school)
        db.commit()
        db.refresh(school)

    # Check if admin exists
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        print("Creating admin user...")
        user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role="admin",
            school_id=school.id,
            is_active=True
        )
        db.add(user)
        db.commit()
        print("Admin user created (admin/admin123)")
    else:
        print("Admin user already exists.")
        if not user.school_id:
            user.school_id = school.id
            db.commit()
            print("Updated admin user with default school.")

    db.close()

if __name__ == "__main__":
    init_db()
