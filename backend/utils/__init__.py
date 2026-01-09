import pandas as pd
import io
from typing import List, Dict

def generate_excel_bytes(data: List[Dict]) -> io.BytesIO:
    """
    Generates an Excel file in memory from a list of dictionaries.
    """
    if not data:
        return io.BytesIO()

    df = pd.DataFrame(data)

    # Reorder columns to make it look nicer if possible
    # We want base info first, then total score, then section scores, then details
    base_cols = ['学号', '姓名', '机号', '总分']

    # Identify dynamic columns
    all_cols = df.columns.tolist()

    # Section columns (usually simple names like "单选得分")
    # Detail columns (start with Q)
    # Comment columns (end with _comment)

    section_cols = []
    q_cols = []
    comment_cols = []
    other_cols = []

    for c in all_cols:
        if c in base_cols:
            continue
        elif c.startswith('Q'):
            if c.endswith('_comment'):
                comment_cols.append(c)
            else:
                q_cols.append(c)
        elif '得分' in c:
            section_cols.append(c)
        else:
            other_cols.append(c)

    # Sort Q cols naturally if possible (Q1-1, Q1-2...)
    # But string sort is okay for now
    q_cols.sort()
    comment_cols.sort()

    final_cols = [c for c in base_cols if c in df.columns] + \
                 section_cols + \
                 other_cols + \
                 q_cols + \
                 comment_cols

    # Filter only existing columns
    final_cols = [c for c in final_cols if c in df.columns]

    df = df[final_cols]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    output.seek(0)
    return output
