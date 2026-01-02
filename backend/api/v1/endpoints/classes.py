from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Any
import pandas as pd
import io

from backend.api import deps
from backend.models.user import User
from backend.models.class_ import Class
from backend.models.student import Student
from backend.db.session import SessionLocal

from pydantic import BaseModel

router = APIRouter()

class ClassCreate(BaseModel):
    name: str
    grade: str = None

class ClassOut(BaseModel):
    id: int
    name: str
    grade: str = None
    school_id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ClassOut])
def get_classes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.school_id:
        return []
    return db.query(Class).filter(Class.school_id == current_user.school_id).all()

@router.post("/", response_model=ClassOut)
def create_class(
    class_in: ClassCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.school_id:
        raise HTTPException(status_code=400, detail="User not associated with a school")

    cls = Class(
        name=class_in.name,
        grade=class_in.grade,
        school_id=current_user.school_id
    )
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return cls

@router.post("/{class_id}/students/import")
async def import_students(
    class_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Verify class belongs to user's school
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    if cls.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        content = await file.read()
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Invalid file format. Use CSV or Excel.")

        # Expected columns: Name, StudentNumber
        # Map columns if needed
        # Simple logic: look for "姓名" or "name", "学号" or "number"

        name_col = next((c for c in df.columns if "姓名" in str(c) or "name" in str(c).lower()), None)
        num_col = next((c for c in df.columns if "学号" in str(c) or "number" in str(c).lower() or "id" in str(c).lower()), None)

        if not name_col or not num_col:
             raise HTTPException(status_code=400, detail="Could not find Name or Student Number columns")

        count = 0
        for _, row in df.iterrows():
            name = str(row[name_col]).strip()
            number = str(row[num_col]).strip()

            # Check existing
            exists = db.query(Student).filter(
                Student.school_id == current_user.school_id,
                Student.student_number == number
            ).first()

            if exists:
                # Update? Or skip? Let's update class_id and name
                exists.name = name
                exists.class_id = class_id
            else:
                new_student = Student(
                    name=name,
                    student_number=number,
                    class_id=class_id,
                    school_id=current_user.school_id
                )
                db.add(new_student)
            count += 1

        db.commit()
        return {"message": f"Imported/Updated {count} students"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
