
from fastapi import APIRouter, HTTPException
from ..schemas import RegisterIn, TokenOut
import jwt, datetime, os

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn):
    # 演示用：直接签发 token（正式版需写入数据库、校验重复邮箱、密码加密等）
    payload = {"sub": data.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return TokenOut(access_token=token)

@router.post("/login", response_model=TokenOut)
def login(data: RegisterIn):
    # 演示用：直接签发 token（正式版需校验密码）
    payload = {"sub": data.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return TokenOut(access_token=token)
