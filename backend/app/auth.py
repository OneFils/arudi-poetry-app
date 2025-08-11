import os, time, jwt
from fastapi import APIRouter, HTTPException, Depends, Form
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .schemas import TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET = os.getenv("JWT_SECRET", "change-me")
ALG = "HS256"

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(409, "Username taken")
    u = User(username=username, password_hash=bcrypt.hash(password))
    db.add(u)
    db.commit()
    return {"ok": True}

@router.post("/login", response_model=TokenOut)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == username).first()
    if not u or not bcrypt.verify(password, u.password_hash):
        raise HTTPException(401, "Bad credentials")
    token = jwt.encode({"sub": u.username, "uid": u.id, "exp": int(time.time()) + 86400}, SECRET, algorithm=ALG)
    return {"access_token": token}

def require_user(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALG])
        return int(payload["uid"])
    except Exception:
        raise HTTPException(401, "Invalid token")
