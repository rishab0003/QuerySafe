from pathlib import Path
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()


class Employee(BaseModel):
    id: str
    email: str
    full_name: str
    department: str
    role: str
    approval_status: str
    is_active: int


def _db_path() -> Path:
    return Path(__file__).resolve().parent / 'demo.sqlite'


@router.get('/employees', response_model=List[Employee])
def list_employees():
    db = _db_path()
    if not db.exists():
        raise HTTPException(status_code=404, detail='Demo DB not initialized')
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute('SELECT id,email,full_name,department,role,approval_status,is_active FROM employees')
    rows = cur.fetchall()
    conn.close()
    return [Employee(**{k: v for k, v in zip(Employee.__fields__.keys(), row)}) for row in rows]


@router.get('/signups')
def signups():
    db = _db_path()
    if not db.exists():
        raise HTTPException(status_code=404, detail='Demo DB not initialized')
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute('SELECT day,count FROM signups')
    rows = cur.fetchall()
    conn.close()
    return [{'day': r[0], 'count': r[1]} for r in rows]
