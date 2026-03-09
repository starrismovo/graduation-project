from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import base64
import json
from datetime import datetime
import shutil
from pathlib import Path

from models.user import User
from models.assessment import AssessmentRecord
from schemas.user import (
    UserProfileUpdate,
    UserProfileResponse,
    AvatarUploadResponse,
    StandardResponse,
)
from database import get_db

load_dotenv()

router = APIRouter(prefix="/user", tags=["用户信息"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# 上传文件保存目录
UPLOAD_DIR = Path(__file__).parent.parent / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/profile", response_model=StandardResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户个人信息"""
    try:
        profile = UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            nickname=current_user.nickname,
            real_name=current_user.real_name,
            email=current_user.email,
            phone=current_user.phone,
            bio=current_user.bio,
            avatar=current_user.avatar_url,
            delivery_privacy=current_user.delivery_privacy,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
        )
        return StandardResponse(code=200, message="获取成功", data=profile.model_dump())
    except Exception as e:
        return StandardResponse(code=500, message=f"获取失败: {str(e)}")


@router.patch("/profile", response_model=StandardResponse)
def update_user_profile(
    update_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    print(f"收到 avatar 长度: {len(update_data.avatar) if update_data.avatar else 'None'}")
    """更新用户个人信息"""
    try:
        # 更新字段（只更新提供的字段）
        if update_data.nickname is not None:
            current_user.nickname = update_data.nickname
        if update_data.real_name is not None:
            current_user.real_name = update_data.real_name
        if update_data.email is not None:
            # 检查邮箱是否已被其他用户使用
            existing = (
                db.query(User)
                .filter(User.email == update_data.email, User.id != current_user.id)
                .first()
            )
            if existing:
                return StandardResponse(code=400, message="邮箱已被其他用户使用")
            current_user.email = update_data.email
        if update_data.phone is not None:
            current_user.phone = update_data.phone
        if update_data.bio is not None:
            current_user.bio = update_data.bio
        if update_data.avatar is not None:
            current_user.avatar_url = update_data.avatar
            
        if update_data.delivery_privacy is not None:
            current_user.delivery_privacy = update_data.delivery_privacy

        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        profile = UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            nickname=current_user.nickname,
            real_name=current_user.real_name,
            email=current_user.email,
            phone=current_user.phone,
            bio=current_user.bio,
            avatar=current_user.avatar_url,
            delivery_privacy=current_user.delivery_privacy,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
        )
        return StandardResponse(code=200, message="更新成功", data=profile.model_dump())
    except Exception as e:
        db.rollback()
        return StandardResponse(code=500, message=f"更新失败: {str(e)}")


@router.post("/avatar", response_model=StandardResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传用户头像"""
    try:
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if file.content_type not in allowed_types:
            return StandardResponse(code=400, message="只支持 JPG、PNG、WebP 格式的图片")

        # 读取文件内容
        content = await file.read()

        # 验证文件大小 (2MB)
        if len(content) > 2 * 1024 * 1024:
            return StandardResponse(code=400, message="文件大小不能超过 2MB")

        # 保存为 Base64 编码（存储在数据库中）
        avatar_base64 = base64.b64encode(content).decode("utf-8")
        avatar_data_url = f"data:{file.content_type};base64,{avatar_base64}"

        # 更新用户头像
        current_user.avatar_url = avatar_data_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return StandardResponse(
            code=200,
            message="头像上传成功",
            data={"avatar": avatar_data_url, "filename": file.filename},
        )
    except Exception as e:
        db.rollback()
        return StandardResponse(code=500, message=f"头像上传失败: {str(e)}")


@router.delete("/assessments", response_model=StandardResponse)
def delete_all_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除用户所有评估记录"""
    try:
        # 查找并删除该用户的所有评估记录
        deleted_count = (
            db.query(AssessmentRecord)
            .filter(AssessmentRecord.candidate_id == current_user.id)
            .delete()
        )
        db.commit()

        return StandardResponse(
            code=200,
            message=f"已删除 {deleted_count} 条评估记录",
            data={"deleted_count": deleted_count},
        )
    except Exception as e:
        db.rollback()
        return StandardResponse(code=500, message=f"删除失败: {str(e)}")

