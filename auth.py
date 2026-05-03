from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRole, Role

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()

def create_token(data: dict):
    data['exp'] = datetime.now() + timedelta(hours=2)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

def get_current_user(payload = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_role(user_id, db):
    roles = (
        db.query(Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return [r[0] for r in roles]

def require_roles(required_roles: list):
    def checker(user = Depends(get_current_user), db: Session = Depends(get_db)):
        user_roles = get_user_role(user.id, db)
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Access Denied")
        return user
    return checker
