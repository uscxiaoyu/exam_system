from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from backend.database import get_engine, is_db_available
from backend.utils import generate_excel_bytes
import json
import pandas as pd
import io

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("/")
async def get_history_summary():
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT exam_name, created_at FROM exam_records ORDER BY created_at DESC"))
            exams = [{"exam_name": row[0], "created_at": str(row[1]) if row[1] else None} for row in result]
            return exams
    except Exception as e:
        # Table might not exist yet
        return []

@router.get("/{exam_name}")
async def get_exam_history(exam_name: str):
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    engine = get_engine()
    try:
        query = text("SELECT student_id, student_name, machine_id, total_score, details_json, created_at FROM exam_records WHERE exam_name=:name")
        df = pd.read_sql(query, engine, params={"name": exam_name})

        # Process JSON details
        records = df.to_dict(orient="records")
        final_records = []
        for rec in records:
            # Map back to UI keys
            ui_rec = {
                "学号": rec["student_id"],
                "姓名": rec["student_name"],
                "机号": rec["machine_id"],
                "总分": rec["total_score"],
                "created_at": str(rec["created_at"])
            }
            if rec.get("details_json"):
                try:
                    details = json.loads(rec["details_json"])
                    ui_rec.update(details)
                except:
                    pass
            final_records.append(ui_rec)
        return final_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{exam_name}/export")
async def export_exam_history(exam_name: str):
    # Reuse get_exam_history logic
    records = await get_exam_history(exam_name)
    try:
        excel_io = generate_excel_bytes(records)
        return Response(
            content=excel_io.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={exam_name}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def save_history(
    exam_name: str,
    records: List[Dict[str, Any]]
):
    if not is_db_available():
        raise HTTPException(status_code=503, detail="Database not available")

    if not records:
        return {"message": "No records to save"}

    engine = get_engine()
    try:
        df = pd.DataFrame(records)

        # Prepare data for DB
        # Columns expected: student_id, student_name, machine_id, total_score, details_json, exam_name

        # Extract details (Q columns and score columns)
        detail_cols = [c for c in df.columns if c.startswith('Q') or '得分' in c]

        df['details_json'] = df[detail_cols].apply(
            lambda x: json.dumps(x.to_dict(), ensure_ascii=False), axis=1
        )

        cols_map = {'学号': 'student_id', '姓名': 'student_name', '机号': 'machine_id', '总分': 'total_score'}

        # Rename if exists, otherwise create/fill
        rename_dict = {}
        for k, v in cols_map.items():
            if k in df.columns:
                rename_dict[k] = v
            elif v not in df.columns:
                # If required col missing, fill with default?
                pass

        final_df = df.rename(columns=rename_dict)

        # Ensure required columns exist
        required_cols = ['student_id', 'student_name', 'machine_id', 'total_score', 'details_json']
        for col in required_cols:
            if col not in final_df.columns:
                final_df[col] = None # Or valid default

        final_df = final_df[required_cols]
        final_df['exam_name'] = exam_name

        with engine.connect() as conn:
            # Delete old records for this exam
            conn.execute(text("DELETE FROM exam_records WHERE exam_name = :name"), {"name": exam_name})
            conn.commit()

        final_df.to_sql('exam_records', con=engine, if_exists='append', index=False)

        return {"message": f"Saved {len(final_df)} records"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
