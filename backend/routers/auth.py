from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.user import User
from database import get_db
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv
import os
from fastapi import Form

load_dotenv()

router = APIRouter(prefix="/auth", tags=["认证"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # 这里 expire 是 datetime 对象
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    is_hr: bool = Form(False),
    db: Session = Depends(get_db)
):
    # 验证输入
    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少3个字符")
    if not email or '@' not in email:
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6个字符")
    
    try:
        # 检查用户名是否已存在
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        db_email = db.query(User).filter(User.email == email).first()
        if db_email:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        hashed = get_password_hash(password)
        new_user = User(username=username, email=email, hashed_password=hashed, is_hr=is_hr)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "注册成功", "user_id": new_user.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"注册错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    access_token = create_access_token(data={"sub": user.username, "is_hr": user.is_hr, "user_id": user.id})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "is_hr": user.is_hr,
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }