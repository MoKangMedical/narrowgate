"""
窄门 (NarrowGate) - 用户认证系统

功能：
- 用户注册/登录
- JWT token生成和验证
- 密码加密
- 微信登录支持
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Depends, Header
from pydantic import BaseModel

# JWT配置
SECRET_KEY = "narrowgate_secret_key_2026"  # 生产环境应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: str
    password: str
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str  # 用户名或邮箱
    password: str


class WechatLogin(BaseModel):
    """微信登录请求"""
    code: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    nickname: str
    avatar: Optional[str] = None


class AuthManager:
    """认证管理器"""
    
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """加密密码"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            salt, hash_value = hashed.split(":")
            hash_obj = hashlib.sha256((password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    def create_access_token(self, user_id: str, username: str) -> str:
        """创建JWT token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "username": username,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Dict:
        """验证JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token已过期")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="无效的Token")
    
    def register(self, user_data: UserRegister) -> TokenResponse:
        """用户注册"""
        # 检查用户名是否已存在
        with self.db._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?",
                (user_data.username, user_data.email)
            ).fetchone()
            
            if existing:
                raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
            
            # 创建用户
            user_id = f"user_{secrets.token_hex(8)}"
            hashed_password = self.hash_password(user_data.password)
            nickname = user_data.nickname or user_data.username
            now = datetime.now().isoformat()
            
            conn.execute(
                """INSERT INTO users 
                (id, username, email, password_hash, nickname, created_at, updated_at, level, experience_points)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)""",
                (user_id, user_data.username, user_data.email, hashed_password, nickname, now, now)
            )
            conn.commit()
        
        # 生成token
        access_token = self.create_access_token(user_id, user_data.username)
        
        return TokenResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user_id,
            username=user_data.username,
            nickname=nickname
        )
    
    def login(self, login_data: UserLogin) -> TokenResponse:
        """用户登录"""
        with self.db._connect() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (login_data.username, login_data.username)
            ).fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            
            # 验证密码
            if not self.verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            
            # 更新最后登录时间
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(), user["id"])
            )
            conn.commit()
        
        # 生成token
        access_token = self.create_access_token(user["id"], user["username"])
        
        return TokenResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user["id"],
            username=user["username"],
            nickname=user["nickname"],
            avatar=user["avatar"]
        )
    
    def wechat_login(self, wechat_data: WechatLogin) -> TokenResponse:
        """微信登录"""
        # 这里需要调用微信API获取openid
        # 简化实现：使用code作为临时标识
        wechat_openid = f"wx_{wechat_data.code[:16]}"
        
        with self.db._connect() as conn:
            # 检查是否已存在
            user = conn.execute(
                "SELECT * FROM users WHERE wechat_openid = ?",
                (wechat_openid,)
            ).fetchone()
            
            if user:
                # 已存在，直接登录
                user_id = user["id"]
                username = user["username"]
                nickname = user["nickname"]
                avatar = user["avatar"]
            else:
                # 新用户，创建账号
                user_id = f"user_{secrets.token_hex(8)}"
                username = f"wx_{secrets.token_hex(6)}"
                nickname = wechat_data.nickname or "微信用户"
                avatar = wechat_data.avatar
                now = datetime.now().isoformat()
                
                conn.execute(
                    """INSERT INTO users 
                    (id, username, wechat_openid, nickname, avatar, created_at, updated_at, level, experience_points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)""",
                    (user_id, username, wechat_openid, nickname, avatar, now, now)
                )
                conn.commit()
        
        # 生成token
        access_token = self.create_access_token(user_id, username)
        
        return TokenResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user_id,
            username=username,
            nickname=nickname,
            avatar=avatar
        )
    
    def get_current_user(self, authorization: str = Header(None)) -> Dict:
        """获取当前用户"""
        if not authorization:
            raise HTTPException(status_code=401, detail="未提供认证信息")
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="认证格式错误")
        except ValueError:
            raise HTTPException(status_code=401, detail="认证格式错误")
        
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        with self.db._connect() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="用户不存在")
            
            return dict(user)


def create_auth_routes(app, db):
    """创建认证路由"""
    auth_manager = AuthManager(db)
    
    @app.post("/api/auth/register", response_model=TokenResponse)
    async def register(user_data: UserRegister):
        """用户注册"""
        return auth_manager.register(user_data)
    
    @app.post("/api/auth/login", response_model=TokenResponse)
    async def login(login_data: UserLogin):
        """用户登录"""
        return auth_manager.login(login_data)
    
    @app.post("/api/auth/wechat", response_model=TokenResponse)
    async def wechat_login(wechat_data: WechatLogin):
        """微信登录"""
        return auth_manager.wechat_login(wechat_data)
    
    @app.get("/api/auth/me")
    async def get_current_user(authorization: str = Header(None)):
        """获取当前用户信息"""
        return auth_manager.get_current_user(authorization)
    
    @app.post("/api/auth/logout")
    async def logout(authorization: str = Header(None)):
        """用户登出"""
        # JWT是无状态的，客户端删除token即可
        # 这里可以记录登出日志
        return {"message": "已成功登出"}
    
    return auth_manager