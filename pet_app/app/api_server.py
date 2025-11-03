import threading
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, func,Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.hash import bcrypt as bcrypt_hash
from pydantic import BaseModel
import jwt
import datetime
import os
import time
import random
import string
import smtplib
from email.mime.text import MIMEText
import logging
import sys
import pymysql
pymysql.install_as_MySQLdb() 
# 在文件顶部添加环境检测
IS_FROZEN = getattr(sys, 'frozen', False)
print(f"运行环境: {'打包后' if IS_FROZEN else '开发环境'}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "rm-bp19kz85ye935j549po.mysql.rds.aliyuncs.com")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "petapp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Lsm050401")
DB_NAME = os.getenv("DB_NAME", "petapp_db")
# 构建数据库连接URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 15})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 邮件配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "2172723436@qq.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "qqoflkzlvkisebhh") 
EMAIL_FROM = os.getenv("EMAIL_FROM", "2172723436@qq.com")

# JWT配置
JWT_SECRET = "petapp_secret_key"
JWT_EXPIRE_MINUTES = 120
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 验证码存储（内存版）
verification_codes = {}
# 用于密码重置的验证码存储
password_reset_codes = {}

# 创建线程锁 - 确保线程安全
verification_codes_lock = threading.Lock()
password_reset_codes_lock = threading.Lock()  # 为密码重置添加专用锁

# 密码加密
def verify_password(plain_password, hashed_password):
    return bcrypt_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return bcrypt_hash.using(rounds=12).hash(password)

def generate_verification_code():
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email: str, code: str, is_reset: bool = False):
    """发送验证邮件"""
    if is_reset:
        subject = '密码重置验证码'
        message = f"您的智慧宠物管家密码重置验证码是：{code}\n该验证码15分钟内有效。"
    else:
        subject = '邮箱验证'
        message = f"您的智慧宠物管家验证码是：{code}\n该验证码5分钟内有效。"
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = email

    try:
        print(f"尝试连接SMTP服务器: {SMTP_SERVER}:{SMTP_PORT}")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        print("连接成功，准备启动TLS...")
        server.starttls()
        print("TLS启动成功，准备登录...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("登录成功，准备发送邮件...")
        server.sendmail(EMAIL_FROM, [email], msg.as_string())
        print("邮件发送成功，准备安全关闭连接...")
        
        # 安全关闭连接
        try:
            server.rset()
            server.quit()
        except:
            server.close()
        
        # 存储验证码
        current_time = time.time()
        if is_reset:
            with password_reset_codes_lock:
                if email not in password_reset_codes:
                    password_reset_codes[email] = {}
                password_reset_codes[email]['code'] = code
                password_reset_codes[email]['timestamp'] = current_time
        else:
            with verification_codes_lock:
                if email not in verification_codes:
                    verification_codes[email] = {}
                verification_codes[email]['code'] = code
                verification_codes[email]['timestamp'] = current_time
            
        return True
    except smtplib.SMTPAuthenticationError as auth_err:
        print(f"SMTP认证失败: {auth_err}")
        print("请检查：1. SMTP_USER是否为完整邮箱 2. SMTP_PASSWORD是否为授权码(不是QQ密码) 3. 是否已开启SMTP服务")
        return False
    except Exception as e:
        import traceback
        print(f"邮件发送失败详情:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"堆栈跟踪:")
        traceback.print_exc()
        return False

# 数据库模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    display_name = Column(String(255))
    role = Column(String(32), nullable=False, default="member")
    created_at = Column(DateTime, server_default=func.now())

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100))
    sex = Column(String(10))
    birth_date = Column(Date)
    neutered = Column(String(10))
    weight_kg = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())

class PetCreate(BaseModel):
    name: str
    species: str
    breed: str = None
    sex: str = None
    birth_date: str = None
    weight_kg: str = None

class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    breakfast = Column(Text)
    lunch = Column(Text)
    dinner = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MealPlanCreate(BaseModel):
    breakfast: str = None
    lunch: str = None
    dinner: str = None

class MealPlanResponse(BaseModel):
    id: int
    pet_id: int
    breakfast: str = None
    lunch: str = None
    dinner: str = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

class FeedingRecord(Base):
    __tablename__ = "feeding_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    date = Column(Date, default=datetime.date.today, nullable=False)
    breakfast_done = Column(Boolean, default=False)
    lunch_done = Column(Boolean, default=False)
    dinner_done = Column(Boolean, default=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# 初始化数据库
def init_db():
    """初始化数据库，创建表结构"""
    # 确保连接到云数据库
    engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
    Base.metadata.create_all(bind=engine)
    
    # 检查并创建管理员账号
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email="admin@petapp.com").first():
            admin = User(
                email="admin@petapp.com",
                password_hash=get_password_hash("admin123"),
                display_name="管理员"
            )
            db.add(admin)
            db.commit()
            print("✅ 管理员账号已创建")
        else:
            print("ℹ️ 管理员账号已存在")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        # 如果是表不存在错误，尝试重新创建
        if "1146" in str(e):  # MySQL错误代码：表不存在
            Base.metadata.create_all(bind=engine)
            init_db()  # 递归重试
    finally:
        db.close()

# 创建FastAPI应用
app = FastAPI(title="智慧宠物APP", version="1.0.0")

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(401, "无效的认证凭证")
        return user
    except jwt.PyJWTError:
        raise HTTPException(401, "无效的令牌")

# 认证路由
@app.post("/api/auth/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "邮箱或密码错误")
    
    payload = {
        "sub": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

# 宠物管理路由
@app.get("/api/pets")
def get_pets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{
        "id": pet.id,
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "sex": pet.sex,
        "birth_date": pet.birth_date.isoformat() if pet.birth_date else None,
        "neutered": pet.neutered,
        "weight_kg": pet.weight_kg
    } for pet in db.query(Pet).filter(Pet.owner_id == current_user.id).all()]

@app.post("/api/pets")
def create_pet(pet: PetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pet_db = Pet(
        owner_id=current_user.id,
        name=pet.name,
        species=pet.species,
        breed=pet.breed,
        sex=pet.sex,
        birth_date=datetime.datetime.strptime(pet.birth_date, "%Y-%m-%d").date() if pet.birth_date else None,
        weight_kg=pet.weight_kg
    )
    db.add(pet_db)
    db.commit()
    db.refresh(pet_db)
    return {"id": pet_db.id, "name": pet_db.name, "species": pet_db.species}

@app.post("/api/auth/send-verification-code")
def send_verification_code(email: str = Form(...)):
    """发送邮箱验证码（修复频率限制问题）"""
    # 检查邮箱是否已注册
    db = SessionLocal()
    if db.query(User).filter_by(email=email).first():
        db.close()
        raise HTTPException(400, "该邮箱已被注册")
    db.close()

    current_time = time.time()
    
    # 使用锁保护对verification_codes的访问
    with verification_codes_lock:
        # 安全获取上一次请求时间
        email_data = verification_codes.get(email, {})
        last_request = email_data.get('last_request', 0)
        
        # 正确计算时间差
        if last_request > 0:
            time_since_last = current_time - last_request
            time_since_last_str = f"{time_since_last:.1f}秒"
        else:
            time_since_last = float('inf')  # 第一次请求视为"无限久之前"
            time_since_last_str = "从未请求过"
        
        print(f"\n{'='*50}")
        print(f"验证码请求: {email}")
        print(f"当前时间戳: {current_time:.2f}")
        print(f"上次请求时间戳: {last_request:.2f}")
        print(f"时间间隔: {time_since_last_str}")
        
        # 严格检查是否在60秒内
        if time_since_last < 60:
            print(f"❌ 请求过于频繁，拒绝发送验证码 (间隔: {time_since_last:.1f}秒 < 60秒)")
            raise HTTPException(429, "请求过于频繁，请1分钟后重试")
        
        # 通过检查后才更新时间戳
        if email not in verification_codes:
            verification_codes[email] = {}
        verification_codes[email]['last_request'] = current_time
        print(f"✅ 更新请求时间戳: {current_time:.2f}")
    
    # 生成并发送验证码
    code = generate_verification_code()
    
    if send_verification_email(email, code, is_reset=False):
        print(f"✅ 验证码已发送至 {email}: {code}")
        return {"message": "验证码已发送"}
    else:
        # 发送失败时清理（避免因发送失败而永久锁定）
        with verification_codes_lock:
            if email in verification_codes:
                verification_codes[email].pop('last_request', None)
        raise HTTPException(500, "邮件发送失败")

@app.post("/api/auth/register")
def register(
    email: str = Form(...), 
    password: str = Form(...), 
    display_name: str = Form(...),
    verification_code: str = Form(...),
    db: Session = Depends(get_db)
):
    """用户注册端点（修复KeyError问题）"""
    # 添加详细调试日志
    print(f"\n{'='*50}")
    print(f"注册请求: {email}")
    print(f"验证码: '{verification_code}' (长度: {len(verification_code)})")
    
    # 清理验证码（去除前后空格）
    verification_code = verification_code.strip()
    
    # 检查邮箱是否已存在
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(400, "该邮箱已被注册")
    
    # 使用锁保护对verification_codes的访问
    with verification_codes_lock:
        # 安全获取验证码记录
        stored = verification_codes.get(email, {})
        
        if not stored or 'code' not in stored:
            print(f"❌ 未找到 {email} 的验证码记录")
            raise HTTPException(400, "验证码错误或已过期")
        
        # 安全获取存储的验证码
        stored_code = stored.get('code', '').strip()
        timestamp = stored.get('timestamp', 0)
        
        print(f"存储的验证码: '{stored_code}'")
        print(f"存储时间: {timestamp:.0f} ({time.time()-timestamp:.1f}秒前)")
        
        if stored_code != verification_code:
            print(f"❌ 验证码不匹配!")
            raise HTTPException(400, "验证码错误")
        
        # 检查是否过期
        if time.time() - timestamp > 300:
            print(f"❌ 验证码已过期 ({time.time()-timestamp:.1f}秒 > 300秒)")
            verification_codes.pop(email, None)
            raise HTTPException(400, "验证码已过期")
        
        # 安全删除验证码
        print(f"✅ 验证码验证通过，删除记录")
        verification_codes.pop(email, None)

    # 创建新用户
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        display_name=display_name
    )
    db.add(user)
    db.commit()
    
    print(f"✅ 用户 {email} 注册成功")
    return {"message": "注册成功"}

# 新增：忘记密码功能
@app.post("/api/auth/forgot-password")
def forgot_password(email: str = Form(...)):
    """请求密码重置（发送重置验证码）"""
    # 检查邮箱是否已注册
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    
    if not user:
        # 为了安全，即使邮箱不存在也返回成功（防止邮箱枚举攻击）
        print(f"⚠️ 密码重置请求: {email} (邮箱未注册)")
        return {"message": "如果该邮箱已注册，验证码将发送至该邮箱"}
    
    current_time = time.time()
    
    # 使用锁保护对password_reset_codes的访问
    with password_reset_codes_lock:
        # 安全获取上一次请求时间
        email_data = password_reset_codes.get(email, {})
        last_request = email_data.get('last_request', 0)
        
        # 正确计算时间差
        if last_request > 0:
            time_since_last = current_time - last_request
            time_since_last_str = f"{time_since_last:.1f}秒"
        else:
            time_since_last = float('inf')  # 第一次请求视为"无限久之前"
            time_since_last_str = "从未请求过"
        
        print(f"\n{'='*50}")
        print(f"密码重置请求: {email}")
        print(f"当前时间戳: {current_time:.2f}")
        print(f"上次请求时间戳: {last_request:.2f}")
        print(f"时间间隔: {time_since_last_str}")
        
        # 严格检查是否在60秒内
        if time_since_last < 60:
            print(f"❌ 请求过于频繁，拒绝发送验证码 (间隔: {time_since_last:.1f}秒 < 60秒)")
            raise HTTPException(429, "请求过于频繁，请1分钟后重试")
        
        # 通过检查后才更新时间戳
        if email not in password_reset_codes:
            password_reset_codes[email] = {}
        password_reset_codes[email]['last_request'] = current_time
        print(f"✅ 更新密码重置请求时间戳: {current_time:.2f}")
    
    # 生成并发送验证码
    code = generate_verification_code()
    
    if send_verification_email(email, code, is_reset=True):
        print(f"✅ 密码重置验证码已发送至 {email}: {code}")
        return {"message": "验证码已发送，请查收邮箱"}
    else:
        # 发送失败时清理
        with password_reset_codes_lock:
            if email in password_reset_codes:
                password_reset_codes[email].pop('last_request', None)
        raise HTTPException(500, "邮件发送失败")


@app.post("/api/auth/reset-password")
def reset_password(
    email: str = Form(...),
    verification_code: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """重置密码端点"""
    # 添加详细调试日志
    print(f"\n{'='*50}")
    print(f"密码重置请求: {email}")
    print(f"验证码: '{verification_code}'")
    
    # 验证新密码
    if len(new_password) < 6:
        raise HTTPException(400, "密码长度至少为6位")
    
    if new_password != confirm_password:
        raise HTTPException(400, "两次输入的密码不一致")
    
    # 使用锁保护对password_reset_codes的访问
    with password_reset_codes_lock:
        # 安全获取验证码记录
        stored = password_reset_codes.get(email, {})
        
        if not stored or 'code' not in stored:
            print(f"❌ 未找到 {email} 的密码重置验证码记录")
            raise HTTPException(400, "验证码错误或已过期")
        
        # 安全获取存储的验证码
        stored_code = stored.get('code', '').strip()
        timestamp = stored.get('timestamp', 0)
        
        print(f"存储的验证码: '{stored_code}'")
        print(f"存储时间: {timestamp:.0f} ({time.time()-timestamp:.1f}秒前)")
        
        if stored_code != verification_code.strip():
            print(f"❌ 验证码不匹配!")
            raise HTTPException(400, "验证码错误")
        
        # 检查是否过期（15分钟）
        if time.time() - timestamp > 900:  # 15分钟 = 900秒
            print(f"❌ 验证码已过期 ({time.time()-timestamp:.1f}秒 > 900秒)")
            password_reset_codes.pop(email, None)
            raise HTTPException(400, "验证码已过期")
    
    # 更新密码
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(400, "用户不存在")
        
        # 检查新密码是否与旧密码相同
        if verify_password(new_password, user.password_hash):
            raise HTTPException(400, "新密码不能与当前密码相同")
        
        # 更新密码
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        # 清除密码重置记录
        with password_reset_codes_lock:
            if email in password_reset_codes:
                del password_reset_codes[email]
        
        print(f"✅ 用户 {email} 密码已成功重置")
        return {"message": "密码重置成功，请使用新密码登录"}
    except Exception as e:
        print(f"❌ 密码重置失败: {str(e)}")
        raise HTTPException(500, "密码重置失败")


@app.delete("/api/pets/{pet_id}")
def delete_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"尝试删除宠物: pet_id={pet_id}, user_id={current_user.id}")
    
    # 先检查宠物是否属于当前用户
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        print("未找到该用户拥有的宠物")
        raise HTTPException(404, "宠物不存在或无权访问")
    
    # 先删除相关的喂食记录
    db.query(FeedingRecord).filter(FeedingRecord.pet_id == pet_id).delete()
    
    # 先删除相关的食谱计划
    db.query(MealPlan).filter(MealPlan.pet_id == pet_id).delete()
    db.delete(pet)
    db.commit()
    return {"message": "宠物删除成功"}
@app.get("/api/pets/{pet_id}/meal-plan")
def get_meal_plan(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取宠物的食谱计划"""
    # 先检查宠物是否属于当前用户
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(404, "宠物不存在或无权访问")
    
    # 获取食谱计划
    meal_plan = db.query(MealPlan).filter(MealPlan.pet_id == pet_id).first()
    if not meal_plan:
        # 如果没有食谱计划，创建一个空的
        meal_plan = MealPlan(
            pet_id=pet_id,
            breakfast="",
            lunch="",
            dinner=""
        )
        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)
    
    return {
        "id": meal_plan.id,
        "pet_id": meal_plan.pet_id,
        "breakfast": meal_plan.breakfast,
        "lunch": meal_plan.lunch,
        "dinner": meal_plan.dinner,
        "created_at": meal_plan.created_at.isoformat(),
        "updated_at": meal_plan.updated_at.isoformat()
    }

@app.post("/api/pets/{pet_id}/meal-plan")
def update_meal_plan(
    pet_id: int,
    meal_plan: MealPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建或更新宠物的食谱计划"""
    # 先检查宠物是否属于当前用户
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(404, "宠物不存在或无权访问")
    
    # 获取或创建食谱计划
    existing_plan = db.query(MealPlan).filter(MealPlan.pet_id == pet_id).first()
    if existing_plan:
        # 更新现有计划
        if meal_plan.breakfast is not None:
            existing_plan.breakfast = meal_plan.breakfast
        if meal_plan.lunch is not None:
            existing_plan.lunch = meal_plan.lunch
        if meal_plan.dinner is not None:
            existing_plan.dinner = meal_plan.dinner
        db.commit()
        db.refresh(existing_plan)
        return {"message": "食谱计划已更新", "meal_plan": existing_plan}
    else:
        # 创建新计划
        new_plan = MealPlan(
            pet_id=pet_id,
            breakfast=meal_plan.breakfast or "",
            lunch=meal_plan.lunch or "",
            dinner=meal_plan.dinner or ""
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return {"message": "食谱计划已创建", "meal_plan": new_plan}

@app.get("/api/pets/{pet_id}/feeding-record")
def get_feeding_record(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取宠物当天的喂食记录"""
    # 先检查宠物是否属于当前用户
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(404, "宠物不存在或无权访问")
    
    # 获取当天的喂食记录
    today = datetime.date.today()
    record = db.query(FeedingRecord).filter(
        FeedingRecord.pet_id == pet_id,
        FeedingRecord.date == today
    ).first()
    
    if not record:
        # 创建新记录
        record = FeedingRecord(
            pet_id=pet_id,
            date=today,
            breakfast_done=False,
            lunch_done=False,
            dinner_done=False
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    
    return {
        "id": record.id,
        "pet_id": record.pet_id,
        "date": record.date.isoformat(),
        "breakfast_done": record.breakfast_done,
        "lunch_done": record.lunch_done,
        "dinner_done": record.dinner_done,
        "updated_at": record.updated_at.isoformat()
    }

@app.post("/api/pets/{pet_id}/feeding-record")
def update_feeding_record(
    pet_id: int,
    meal_type: str = Form(...),
    done: bool = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新宠物当天的喂食记录"""
    # 先检查宠物是否属于当前用户
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(404, "宠物不存在或无权访问")
    
    # 获取当天的喂食记录
    today = datetime.date.today()
    record = db.query(FeedingRecord).filter(
        FeedingRecord.pet_id == pet_id,
        FeedingRecord.date == today
    ).first()
    
    if not record:
        # 创建新记录
        record = FeedingRecord(
            pet_id=pet_id,
            date=today,
            breakfast_done=False,
            lunch_done=False,
            dinner_done=False
        )
        db.add(record)
    
    # 更新相应餐次的打卡状态
    if meal_type == "breakfast":
        record.breakfast_done = done
    elif meal_type == "lunch":
        record.lunch_done = done
    elif meal_type == "dinner":
        record.dinner_done = done
    else:
        raise HTTPException(400, "无效的餐次类型")
    
    db.commit()
    db.refresh(record)
    
    return {
        "id": record.id,
        "pet_id": record.pet_id,
        "date": record.date.isoformat(),
        "breakfast_done": record.breakfast_done,
        "lunch_done": record.lunch_done,
        "dinner_done": record.dinner_done,
        "updated_at": record.updated_at.isoformat()
    }

@app.get("/api/meal-plan/recommendations/{species}")
def get_recommendations(species: str):
    """获取特定宠物品种的早中晚三餐推荐"""
    print(f"【API】收到食物推荐请求 - 种类: {species}")
    
    # 创建详细的三餐推荐表单
    recommendations = {
        "狗": {
            "breakfast": "推荐早餐：优质狗粮+煮熟的鸡胸肉（100g）+胡萝卜碎（20g）",
            "lunch": "推荐午餐：西兰花（30g）+牛肉（80g）+狗粮（50g）",
            "dinner": "推荐晚餐：三文鱼（60g）+南瓜泥（40g）+狗粮（60g）"
        },
        "猫": {
            "breakfast": "推荐早餐：优质猫粮（40g）+煮熟的鱼肉（30g）",
            "lunch": "推荐午餐：鸡胸肉（50g）+猫草（少量）+罐头（半罐）",
            "dinner": "推荐晚餐：猫粮（40g）+煮虾（2只）+营养膏（1cm）"
        },
        "兔子": {
            "breakfast": "推荐早餐：干草（不限量）+胡萝卜（20g）",
            "lunch": "推荐午餐：新鲜生菜（30g）+兔粮（15g）",
            "dinner": "推荐晚餐：干草（不限量）+苹果片（2片）"
        },
        "仓鼠": {
            "breakfast": "推荐早餐：仓鼠粮（10g）+葵花籽（3粒）",
            "lunch": "推荐午餐：胡萝卜丁（10g）+苹果（5g）",
            "dinner": "推荐晚餐：仓鼠粮（10g）+面包虫（1只）"
        },
        "鸟": {
            "breakfast": "推荐早餐：鸟粮（15g）+苹果块（10g）",
            "lunch": "推荐午餐：青菜（10g）+小米（5g）",
            "dinner": "推荐晚餐：鸟粮（15g）+葡萄干（2粒）"
        },
        "默认": {
            "breakfast": "推荐早餐：优质主粮+适量蛋白质来源",
            "lunch": "推荐午餐：蔬菜+主粮+少量水果",
            "dinner": "推荐晚餐：营养均衡的主食+少量零食"
        }
    }
    
    # 获取推荐，如果找不到特定种类，使用默认推荐
    species_recommendation = recommendations.get(species, recommendations["默认"])
    
    print(f"【API】返回推荐 - 早餐: {species_recommendation['breakfast']}")
    print(f"【API】返回推荐 - 午餐: {species_recommendation['lunch']}")
    print(f"【API】返回推荐 - 晚餐: {species_recommendation['dinner']}")
    
    return {
        "breakfast": species_recommendation["breakfast"],
        "lunch": species_recommendation["lunch"],
        "dinner": species_recommendation["dinner"]
    }
# 健康建议路由
@app.get("/api/health/advice/{species}")
def get_health_advice(species: str):
    advice = {
        "狗": "每日运动1小时，定期驱虫，注意牙齿清洁",
        "猫": "提供猫抓板，定期梳理毛发，注意饮食均衡",
        "兔子": "提供充足干草，注意牙齿生长，避免潮湿环境",
        "仓鼠": "提供跑轮和磨牙石，注意饮食均衡，避免过度肥胖",
        "鸟": "提供足够的活动空间，注意羽毛清洁，定期检查喙部"
    }
    return {"advice": advice.get(species, "暂无该宠物的健康建议")}


# 启动服务器
def run_server():
    init_db()
    
    # 修复日志配置问题 - 针对打包环境特殊处理
    if IS_FROZEN:
        # 创建自定义日志配置（避免使用需要isatty的formatter）
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(message)s",
                    "use_colors": False  # 关键：强制禁用颜色输出
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                    "use_colors": False  # 同样禁用颜色
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
            },
        }
        # 使用自定义日志配置启动
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            log_level="warning", 
            workers=1,
            log_config=log_config  # 关键：传入自定义配置
        )
    else:
        # 开发环境使用默认配置
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning", workers=1)

if __name__ == "__main__":
    run_server()