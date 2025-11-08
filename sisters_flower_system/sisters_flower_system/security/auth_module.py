"""
安全认证模块

基于ISO/IEC 15408和NIST SP 800-63B标准实现的完整安全认证系统

作者: Security Team
版本: 1.0.0
"""

import sqlite3
import hashlib
import secrets
import time
import logging
import json
import datetime
import re
import base64
import hmac
import base64 as base32
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os
import uuid


# ============= 异常类定义 =============

class SecurityException(Exception):
    """安全模块基础异常类"""
    pass


class AuthenticationException(SecurityException):
    """认证异常"""
    pass


class AuthorizationException(SecurityException):
    """授权异常"""
    pass


class PasswordException(SecurityException):
    """密码相关异常"""
    pass


class SessionException(SecurityException):
    """会话管理异常"""
    pass


class AccountLockoutException(SecurityException):
    """账户锁定异常"""
    pass


class MultiFactorException(SecurityException):
    """多因素认证异常"""
    pass


# ============= 数据结构定义 =============

class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class Permission(Enum):
    """权限枚举"""
    # 系统管理权限
    SYSTEM_ADMIN = "system:admin"
    
    # 用户管理权限
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 销售管理权限
    SALES_CREATE = "sales:create"
    SALES_READ = "sales:read"
    SALES_UPDATE = "sales:update"
    SALES_DELETE = "sales:delete"
    
    # 库存管理权限
    INVENTORY_CREATE = "inventory:create"
    INVENTORY_READ = "inventory:read"
    INVENTORY_UPDATE = "inventory:update"
    INVENTORY_DELETE = "inventory:delete"
    
    # 会员管理权限
    MEMBER_CREATE = "member:create"
    MEMBER_READ = "member:read"
    MEMBER_UPDATE = "member:update"
    MEMBER_DELETE = "member:delete"


@dataclass
class User:
    """用户数据模型"""
    id: int
    username: str
    email: str
    full_name: str
    password_hash: str
    password_salt: str
    role: UserRole
    permissions: List[str]
    is_active: bool
    is_locked: bool
    failed_login_attempts: int
    last_login: Optional[datetime.datetime]
    password_last_changed: datetime.datetime
    mfa_enabled: bool
    mfa_secret: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class Session:
    """会话数据模型"""
    session_id: str
    user_id: int
    username: str
    ip_address: str
    user_agent: str
    created_at: datetime.datetime
    last_accessed: datetime.datetime
    expires_at: datetime.datetime
    is_active: bool


@dataclass
class AuditLog:
    """审计日志数据模型"""
    id: int
    user_id: Optional[int]
    username: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    status: str
    details: Dict[str, Any]
    timestamp: datetime.datetime


@dataclass
class PasswordPolicy:
    """密码策略配置"""
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    require_unique_chars: int = 8
    password_history_count: int = 5
    password_expiry_days: int = 90
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30


# ============= 工具类 =============

class CryptographyUtil:
    """加密工具类"""
    
    @staticmethod
    def generate_salt(size: int = 32) -> bytes:
        """生成随机盐值"""
        return secrets.token_bytes(size)
    
    @staticmethod
    def hash_password(password: str, salt: bytes) -> str:
        """使用PBKDF2哈希密码"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        hashed = kdf.derive(password.encode('utf-8'))
        return base64.b64encode(hashed).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, salt: bytes, hashed: str) -> bool:
        """验证密码"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            kdf.verify(password.encode('utf-8'), base64.b64decode(hashed))
            return True
        except Exception:
            return False
    
    @staticmethod
    def generate_secret_key() -> str:
        """生成密钥用于加密敏感数据"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    
    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """加密数据"""
        f = Fernet(key.encode('utf-8'))
        encrypted = f.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """解密数据"""
        f = Fernet(key.encode('utf-8'))
        decrypted = f.decrypt(base64.b64decode(encrypted_data.encode('utf-8')))
        return decrypted.decode('utf-8')


class OTPGenerator:
    """一次性密码生成器"""
    
    @staticmethod
    def generate_totp_secret() -> str:
        """生成TOTP密钥"""
        return base64.b64encode(secrets.token_bytes(20)).decode('utf-8').rstrip('=')
    
    @staticmethod
    def generate_otp_code(secret: str, timestamp: int = None) -> str:
        """生成TOTP代码"""
        import time
        import hmac
        import struct
        
        if timestamp is None:
            timestamp = int(time.time() // 30)
        
        # 简单的TOTP实现，实际项目中应该使用更可靠的库如pyotp
        secret_bytes = secret.encode('utf-8')
        
        msg = struct.pack(">Q", timestamp)
        hmac_digest = hmac.new(secret_bytes, msg, hashlib.sha1).digest()
        
        offset = hmac_digest[-1] & 0xf
        code = (
            ((hmac_digest[offset] & 0x7f) << 24) |
            ((hmac_digest[offset + 1] & 0xff) << 16) |
            ((hmac_digest[offset + 2] & 0xff) << 8) |
            (hmac_digest[offset + 3] & 0xff)
        ) % (10 ** 6)
        
        return str(code).zfill(6)


# ============= 配置模块 =============

class SecurityConfig:
    """安全配置类"""
    
    # 数据库配置
    DATABASE_PATH = "/workspace/code/sisters_flower_system/security/security.db"
    
    # 会话配置
    SESSION_TIMEOUT_MINUTES = 30
    SESSION_EXTEND_ON_ACTIVITY = True
    
    # 密码策略
    DEFAULT_PASSWORD_POLICY = PasswordPolicy(
        min_length=12,
        require_uppercase=True,
        require_lowercase=True,
        require_numbers=True,
        require_special_chars=True,
        password_expiry_days=90,
        max_failed_attempts=5,
        lockout_duration_minutes=30
    )
    
    # 审计日志配置
    AUDIT_LOG_RETENTION_DAYS = 365
    LOG_FAILED_AUTHENTICATION = True
    LOG_SUCCESSFUL_AUTHENTICATION = True
    LOG_PRIVILEGED_ACTIONS = True
    
    # 加密配置
    ENCRYPTION_KEY = CryptographyUtil.generate_secret_key()
    
    # MFA配置
    MFA_ISSUER_NAME = "Sisters Flower System"
    MFA_WINDOW_TOLERANCE = 1  # 允许的时间窗口误差（30秒间隔）
    
    # 邮件配置（用于MFA和密码重置）
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_USERNAME = "your-email@gmail.com"
    EMAIL_PASSWORD = "your-app-password"
    EMAIL_FROM = "your-email@gmail.com"


# ============= 核心模块 =============

class AuditLogger:
    """审计日志管理器"""
    
    def __init__(self, db_path: str = SecurityConfig.DATABASE_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    status TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.commit()
    
    def log(self, user_id: Optional[int], username: str, action: str, 
            resource: str, status: str, details: Dict[str, Any],
            ip_address: str, user_agent: str):
        """记录审计日志"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_logs 
                (user_id, username, action, resource, ip_address, user_agent, status, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, action, resource, ip_address, user_agent, 
                  status, json.dumps(details)))
            conn.commit()
    
    def get_logs(self, user_id: Optional[int] = None, 
                 start_date: Optional[datetime.datetime] = None,
                 end_date: Optional[datetime.datetime] = None,
                 limit: int = 100) -> List[AuditLog]:
        """获取审计日志"""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_audit_log(row) for row in cursor.fetchall()]
    
    def _row_to_audit_log(self, row) -> AuditLog:
        """将数据库行转换为AuditLog对象"""
        return AuditLog(
            id=row['id'],
            user_id=row['user_id'],
            username=row['username'],
            action=row['action'],
            resource=row['resource'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            status=row['status'],
            details=json.loads(row['details']) if row['details'] else {},
            timestamp=datetime.datetime.fromisoformat(row['timestamp'])
        )


class AccountLockout:
    """账户锁定管理"""
    
    def __init__(self, db_path: str = SecurityConfig.DATABASE_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS account_lockouts (
                    user_id INTEGER PRIMARY KEY,
                    locked_until DATETIME,
                    lockout_reason TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.commit()
    
    def is_locked(self, user_id: int) -> bool:
        """检查账户是否被锁定"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT locked_until FROM account_lockouts WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return False
            
            locked_until = datetime.datetime.fromisoformat(row[0])
            return datetime.datetime.now() < locked_until
    
    def lock_account(self, user_id: int, duration_minutes: int, reason: str):
        """锁定账户"""
        locked_until = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO account_lockouts 
                (user_id, locked_until, lockout_reason)
                VALUES (?, ?, ?)
            """, (user_id, locked_until.isoformat(), reason))
            conn.commit()
    
    def unlock_account(self, user_id: int):
        """解锁账户"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM account_lockouts WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def get_lockout_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取账户锁定信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT locked_until, lockout_reason 
                FROM account_lockouts WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'locked_until': datetime.datetime.fromisoformat(row[0]),
                'reason': row[1]
            }


class MultiFactorAuth:
    """多因素认证管理器"""
    
    def __init__(self, config: SecurityConfig = SecurityConfig):
        self.config = config
        self.secret_key = config.ENCRYPTION_KEY
    
    def generate_secret(self) -> str:
        """生成MFA密钥"""
        return OTPGenerator.generate_totp_secret()
    
    def enable_mfa(self, user_id: int, secret: str) -> bool:
        """为用户启用MFA"""
        try:
            # 验证提供的密钥
            if not self.verify_token(secret, OTPGenerator.generate_otp_code(secret)):
                return False
            
            # 加密存储密钥
            encrypted_secret = CryptographyUtil.encrypt_data(secret, self.secret_key)
            
            with sqlite3.connect(SecurityConfig.DATABASE_PATH) as conn:
                conn.execute("""
                    UPDATE users 
                    SET mfa_enabled = 1, mfa_secret = ?
                    WHERE id = ?
                """, (encrypted_secret, user_id))
                conn.commit()
            
            return True
        except Exception:
            return False
    
    def disable_mfa(self, user_id: int):
        """禁用用户MFA"""
        with sqlite3.connect(SecurityConfig.DATABASE_PATH) as conn:
            conn.execute("""
                UPDATE users 
                SET mfa_enabled = 0, mfa_secret = NULL
                WHERE id = ?
            """, (user_id,))
            conn.commit()
    
    def verify_token(self, secret: str, token: str) -> bool:
        """验证MFA令牌"""
        import base64
        import time
        
        # 允许时间窗口误差
        current_time = int(time.time() // 30)
        
        for i in range(-self.config.MFA_WINDOW_TOLERANCE, 
                      self.config.MFA_WINDOW_TOLERANCE + 1):
            expected_token = OTPGenerator.generate_otp_code(secret, current_time + i)
            if hmac.compare_digest(token, expected_token):
                return True
        
        return False
    
    def generate_qr_code_url(self, username: str, secret: str) -> str:
        """生成MFA设置二维码URL"""
        import urllib.parse
        encoded_issuer = urllib.parse.quote(self.config.MFA_ISSUER_NAME)
        encoded_account = urllib.parse.quote(username)
        
        return (f"otpauth://totp/{encoded_issuer}:{encoded_account}?"
                f"secret={secret}&issuer={encoded_issuer}")


class SessionManager:
    """会话管理器"""
    
    def __init__(self, db_path: str = SecurityConfig.DATABASE_PATH):
        self.db_path = db_path
        self.session_timeout = SecurityConfig.SESSION_TIMEOUT_MINUTES * 60  # 转换为秒
        self._init_database()
    
    def _init_database(self):
        """初始化会话表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.commit()
    
    def create_session(self, user_id: int, username: str, 
                      ip_address: str, user_agent: str) -> str:
        """创建新会话"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(
            minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions 
                (session_id, user_id, username, ip_address, user_agent, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, username, ip_address, user_agent, expires_at))
            conn.commit()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Session]:
        """验证会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sessions 
                WHERE session_id = ? AND is_active = 1
            """, (session_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # 检查会话是否过期
            if datetime.datetime.fromisoformat(row['expires_at']) < datetime.datetime.now():
                self.terminate_session(session_id)
                return None
            
            # 更新最后访问时间
            self._update_last_accessed(session_id)
            
            return self._row_to_session(row)
    
    def extend_session(self, session_id: str) -> bool:
        """延长会话时间"""
        if not SecurityConfig.SESSION_EXTEND_ON_ACTIVITY:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            new_expires = datetime.datetime.now() + datetime.timedelta(
                minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES
            )
            
            conn.execute("""
                UPDATE sessions 
                SET expires_at = ?, last_accessed = ?
                WHERE session_id = ?
            """, (new_expires.isoformat(), datetime.datetime.now().isoformat(), session_id))
            conn.commit()
            
            return conn.total_changes > 0
    
    def terminate_session(self, session_id: str):
        """终止会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET is_active = 0
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
    
    def terminate_all_sessions(self, user_id: int):
        """终止用户的所有会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET is_active = 0
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET is_active = 0
                WHERE expires_at < ?
            """, (datetime.datetime.now().isoformat(),))
            conn.commit()
    
    def get_user_sessions(self, user_id: int) -> List[Session]:
        """获取用户的所有活动会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sessions 
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            return [self._row_to_session(row) for row in cursor.fetchall()]
    
    def _update_last_accessed(self, session_id: str):
        """更新最后访问时间"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET last_accessed = ?
                WHERE session_id = ?
            """, (datetime.datetime.now().isoformat(), session_id))
            conn.commit()
    
    def _row_to_session(self, row) -> Session:
        """将数据库行转换为Session对象"""
        return Session(
            session_id=row['session_id'],
            user_id=row['user_id'],
            username=row['username'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            created_at=datetime.datetime.fromisoformat(row['created_at']),
            last_accessed=datetime.datetime.fromisoformat(row['last_accessed']),
            expires_at=datetime.datetime.fromisoformat(row['expires_at']),
            is_active=bool(row['is_active'])
        )


class PasswordPolicyValidator:
    """密码策略验证器"""
    
    def __init__(self, policy: PasswordPolicy = SecurityConfig.DEFAULT_PASSWORD_POLICY):
        self.policy = policy
    
    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """验证密码是否符合策略"""
        errors = []
        
        # 长度检查
        if len(password) < self.policy.min_length:
            errors.append(f"密码长度至少需要{self.policy.min_length}个字符")
        
        if len(password) > self.policy.max_length:
            errors.append(f"密码长度不能超过{self.policy.max_length}个字符")
        
        # 复杂度检查
        if self.policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("密码需要包含大写字母")
        
        if self.policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("密码需要包含小写字母")
        
        if self.policy.require_numbers and not re.search(r'\d', password):
            errors.append("密码需要包含数字")
        
        if self.policy.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密码需要包含特殊字符")
        
        # 唯一字符检查
        if len(set(password)) < self.policy.require_unique_chars:
            errors.append(f"密码需要包含至少{self.policy.require_unique_chars}个不同的字符")
        
        return len(errors) == 0, errors


class UserManager:
    """用户管理器"""
    
    def __init__(self, db_path: str = SecurityConfig.DATABASE_PATH):
        self.db_path = db_path
        self.audit_logger = AuditLogger(db_path)
        self.password_validator = PasswordPolicyValidator()
        self.mfa_manager = MultiFactorAuth()
        self.account_lockout = AccountLockout(db_path)
        self._init_database()
    
    def _init_database(self):
        """初始化用户表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    role TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_locked BOOLEAN DEFAULT 0,
                    failed_login_attempts INTEGER DEFAULT 0,
                    last_login DATETIME,
                    password_last_changed DATETIME NOT NULL,
                    mfa_enabled BOOLEAN DEFAULT 0,
                    mfa_secret TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def create_user(self, username: str, email: str, full_name: str, 
                   password: str, role: UserRole = UserRole.USER) -> int:
        """创建新用户"""
        # 验证密码策略
        is_valid, errors = self.password_validator.validate(password)
        if not is_valid:
            raise PasswordException(f"密码不符合安全策略: {', '.join(errors)}")
        
        # 检查用户名和邮箱是否已存在
        if self.get_user_by_username(username):
            raise SecurityException("用户名已存在")
        
        if self.get_user_by_email(email):
            raise SecurityException("邮箱已存在")
        
        # 生成密码哈希
        salt = CryptographyUtil.generate_salt()
        password_hash = CryptographyUtil.hash_password(password, salt)
        
        # 生成用户权限
        permissions = self._generate_default_permissions(role)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO users 
                (username, email, full_name, password_hash, password_salt, role, 
                 permissions, password_last_changed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, email, full_name, password_hash, base64.b64encode(salt).decode('utf-8'), role.value,
                  json.dumps(permissions), datetime.datetime.now()))
            user_id = cursor.lastrowid
            conn.commit()
        
        return user_id
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str, user_agent: str) -> Optional[Session]:
        """用户认证"""
        user = self.get_user_by_username(username)
        
        if not user:
            self.audit_logger.log(
                None, username, "authentication_failed", "login",
                "failed", {"reason": "user_not_found"}, ip_address, user_agent
            )
            raise AuthenticationException("用户不存在")
        
        if not user.is_active:
            self.audit_logger.log(
                user.id, username, "authentication_failed", "login",
                "failed", {"reason": "account_inactive"}, ip_address, user_agent
            )
            raise AuthenticationException("账户已被禁用")
        
        if self.account_lockout.is_locked(user.id):
            lockout_info = self.account_lockout.get_lockout_info(user.id)
            self.audit_logger.log(
                user.id, username, "authentication_failed", "login",
                "failed", {"reason": "account_locked", "locked_until": lockout_info['locked_until']},
                ip_address, user_agent
            )
            raise AccountLockoutException(f"账户已被锁定，解除时间: {lockout_info['locked_until']}")
        
        # 验证密码
        if not CryptographyUtil.verify_password(password, 
                                              base64.b64decode(user.password_salt),
                                              user.password_hash):
            self._handle_failed_login(user.id, username, ip_address, user_agent)
            raise AuthenticationException("密码错误")
        
        # 检查密码是否过期
        if self._is_password_expired(user):
            self.audit_logger.log(
                user.id, username, "authentication_failed", "login",
                "failed", {"reason": "password_expired"}, ip_address, user_agent
            )
            raise PasswordException("密码已过期，请重置密码")
        
        # 如果启用了MFA，需要验证MFA令牌
        if user.mfa_enabled:
            # 这里可以返回需要MFA验证的标识，具体的MFA验证在单独的步骤中处理
            return None  # 表示需要MFA验证
        
        # 重置失败尝试次数
        self._reset_failed_login_attempts(user.id)
        
        # 更新最后登录时间
        self._update_last_login(user.id)
        
        # 创建会话
        session_manager = SessionManager(self.db_path)
        session = session_manager.create_session(user.id, username, ip_address, user_agent)
        
        # 记录成功认证
        self.audit_logger.log(
            user.id, username, "authentication_success", "login",
            "success", {"session_id": session}, ip_address, user_agent
        )
        
        return session
    
    def change_password(self, user_id: int, old_password: str, new_password: str):
        """修改密码"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise SecurityException("用户不存在")
        
        # 验证旧密码
        if not CryptographyUtil.verify_password(old_password,
                                              base64.b64decode(user.password_salt),
                                              user.password_hash):
            raise PasswordException("旧密码错误")
        
        # 验证新密码策略
        is_valid, errors = self.password_validator.validate(new_password)
        if not is_valid:
            raise PasswordException(f"新密码不符合安全策略: {', '.join(errors)}")
        
        # 检查密码历史（简单实现）
        if new_password == old_password:
            raise PasswordException("新密码不能与旧密码相同")
        
        # 生成新密码哈希
        new_salt = CryptographyUtil.generate_salt()
        new_hash = CryptographyUtil.hash_password(new_password, new_salt)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET password_hash = ?, password_salt = ?, password_last_changed = ?
                WHERE id = ?
            """, (new_hash, base64.b64encode(new_salt).decode('utf-8'),
                  datetime.datetime.now(), user_id))
            conn.commit()
    
    def reset_password(self, user_id: int, new_password: str):
        """重置密码（管理员功能）"""
        is_valid, errors = self.password_validator.validate(new_password)
        if not is_valid:
            raise PasswordException(f"新密码不符合安全策略: {', '.join(errors)}")
        
        new_salt = CryptographyUtil.generate_salt()
        new_hash = CryptographyUtil.hash_password(new_password, new_salt)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET password_hash = ?, password_salt = ?, password_last_changed = ?
                WHERE id = ?
            """, (new_hash, base64.b64encode(new_salt).decode('utf-8'),
                  datetime.datetime.now(), user_id))
            conn.commit()
        
        # 终止所有现有会话
        session_manager = SessionManager(self.db_path)
        session_manager.terminate_all_sessions(user_id)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        allowed_fields = ['email', 'full_name', 'role', 'is_active', 'permissions']
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                if field == 'permissions':
                    values.append(json.dumps(value))
                else:
                    values.append(value)
        
        if not update_fields:
            return False
        
        values.append(datetime.datetime.now().isoformat())
        values.append(user_id)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"""
                UPDATE users 
                SET {', '.join(update_fields)}, updated_at = ?
                WHERE id = ?
            """, values)
            conn.commit()
            return conn.total_changes > 0
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        with sqlite3.connect(self.db_path) as conn:
            # 删除相关记录
            conn.execute("DELETE FROM account_lockouts WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return conn.total_changes > 0
    
    def _handle_failed_login(self, user_id: int, username: str,
                           ip_address: str, user_agent: str):
        """处理登录失败"""
        # 增加失败尝试次数
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT failed_login_attempts FROM users WHERE id = ?", (user_id,)
            )
            current_attempts = cursor.fetchone()[0] + 1
            
            conn.execute("""
                UPDATE users 
                SET failed_login_attempts = ?
                WHERE id = ?
            """, (current_attempts, user_id))
            conn.commit()
        
        # 检查是否需要锁定账户
        if current_attempts >= SecurityConfig.DEFAULT_PASSWORD_POLICY.max_failed_attempts:
            self.account_lockout.lock_account(
                user_id, 
                SecurityConfig.DEFAULT_PASSWORD_POLICY.lockout_duration_minutes,
                f"密码错误尝试次数过多 ({current_attempts}次)"
            )
            
            # 记录账户锁定
            self.audit_logger.log(
                user_id, username, "account_locked", "login",
                "failed", {"attempts": current_attempts}, ip_address, user_agent
            )
        else:
            # 记录登录失败
            self.audit_logger.log(
                user_id, username, "authentication_failed", "login",
                "failed", {"reason": "invalid_password", "attempts": current_attempts},
                ip_address, user_agent
            )
    
    def _reset_failed_login_attempts(self, user_id: int):
        """重置失败登录尝试次数"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET failed_login_attempts = 0
                WHERE id = ?
            """, (user_id,))
            conn.commit()
    
    def _update_last_login(self, user_id: int):
        """更新最后登录时间"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET last_login = ?
                WHERE id = ?
            """, (datetime.datetime.now().isoformat(), user_id))
            conn.commit()
    
    def _is_password_expired(self, user: User) -> bool:
        """检查密码是否过期"""
        expiry_date = user.password_last_changed + datetime.timedelta(
            days=SecurityConfig.DEFAULT_PASSWORD_POLICY.password_expiry_days
        )
        return datetime.datetime.now() > expiry_date
    
    def _generate_default_permissions(self, role: UserRole) -> List[str]:
        """根据角色生成默认权限"""
        permissions_map = {
            UserRole.ADMIN: [perm.value for perm in Permission],
            UserRole.MANAGER: [
                Permission.USER_READ.value,
                Permission.SALES_CREATE.value, Permission.SALES_READ.value,
                Permission.SALES_UPDATE.value, Permission.SALES_DELETE.value,
                Permission.INVENTORY_READ.value, Permission.INVENTORY_UPDATE.value,
                Permission.MEMBER_CREATE.value, Permission.MEMBER_READ.value,
                Permission.MEMBER_UPDATE.value
            ],
            UserRole.USER: [
                Permission.SALES_CREATE.value, Permission.SALES_READ.value,
                Permission.INVENTORY_READ.value,
                Permission.MEMBER_READ.value
            ],
            UserRole.GUEST: [Permission.INVENTORY_READ.value]
        }
        return permissions_map.get(role, [])
    
    def _row_to_user(self, row) -> User:
        """将数据库行转换为User对象"""
        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            full_name=row['full_name'],
            password_hash=row['password_hash'],
            password_salt=row['password_salt'],
            role=UserRole(row['role']),
            permissions=json.loads(row['permissions']) if row['permissions'] else [],
            is_active=bool(row['is_active']),
            is_locked=bool(row['is_locked']),
            failed_login_attempts=row['failed_login_attempts'],
            last_login=datetime.datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
            password_last_changed=datetime.datetime.fromisoformat(row['password_last_changed']),
            mfa_enabled=bool(row['mfa_enabled']),
            mfa_secret=row['mfa_secret'],
            created_at=datetime.datetime.fromisoformat(row['created_at']),
            updated_at=datetime.datetime.fromisoformat(row['updated_at'])
        )


class PermissionManager:
    """权限管理器"""
    
    def __init__(self, db_path: str = SecurityConfig.DATABASE_PATH):
        self.db_path = db_path
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否有特定权限"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT permissions FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            permissions = json.loads(row['permissions'])
            return permission in permissions
    
    def add_permission(self, user_id: int, permission: str) -> bool:
        """为用户添加权限"""
        user = self._get_user_permissions(user_id)
        if permission not in user:
            user.append(permission)
            return self._update_user_permissions(user_id, user)
        return True
    
    def remove_permission(self, user_id: int, permission: str) -> bool:
        """移除用户权限"""
        user = self._get_user_permissions(user_id)
        if permission in user:
            user.remove(permission)
            return self._update_user_permissions(user_id, user)
        return True
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户所有权限"""
        return self._get_user_permissions(user_id)
    
    def _get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户权限列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT permissions FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            return json.loads(row['permissions']) if row and row['permissions'] else []
    
    def _update_user_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """更新用户权限"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET permissions = ?, updated_at = ?
                WHERE id = ?
            """, (json.dumps(permissions), datetime.datetime.now().isoformat(), user_id))
            conn.commit()
            return conn.total_changes > 0


# ============= 主认证模块 =============

class SecurityAuthModule:
    """安全认证模块主类"""
    
    def __init__(self, config: SecurityConfig = SecurityConfig):
        self.config = config
        self.user_manager = UserManager(config.DATABASE_PATH)
        self.session_manager = SessionManager(config.DATABASE_PATH)
        self.permission_manager = PermissionManager(config.DATABASE_PATH)
        self.audit_logger = AuditLogger(config.DATABASE_PATH)
        self.mfa_manager = MultiFactorAuth(config)
        self.account_lockout = AccountLockout(config.DATABASE_PATH)
        self.password_validator = PasswordPolicyValidator(config.DEFAULT_PASSWORD_POLICY)
    
    def initialize_system(self):
        """初始化安全系统"""
        # 创建默认管理员账户
        if not self.user_manager.get_user_by_username("admin"):
            admin_id = self.user_manager.create_user(
                username="admin",
                email="admin@sistersflower.com",
                full_name="系统管理员",
                password="Admin@123456",  # 首次登录后需要修改
                role=UserRole.ADMIN
            )
            
            # 记录系统初始化
            self.audit_logger.log(
                admin_id, "admin", "system_initialized", "system",
                "success", {"action": "admin_account_created"}, "127.0.0.1", "System"
            )
            
            return admin_id
        return None
    
    def login(self, username: str, password: str, mfa_token: Optional[str] = None,
             ip_address: str = "127.0.0.1", user_agent: str = "Unknown") -> Dict[str, Any]:
        """用户登录"""
        user = None
        try:
            session = self.user_manager.authenticate_user(
                username, password, ip_address, user_agent
            )
            
            if session is None:
                # 需要MFA验证
                user = self.user_manager.get_user_by_username(username)
                if user and user.mfa_enabled and mfa_token:
                    # 验证MFA令牌
                    secret = CryptographyUtil.decrypt_data(user.mfa_secret, self.config.ENCRYPTION_KEY)
                    if self.mfa_manager.verify_token(secret, mfa_token):
                        # MFA验证成功，创建会话
                        session = self.session_manager.create_session(
                            user.id, username, ip_address, user_agent
                        )
                        self.user_manager._reset_failed_login_attempts(user.id)
                        self.user_manager._update_last_login(user.id)
                        
                        self.audit_logger.log(
                            user.id, username, "mfa_authentication_success", "login",
                            "success", {"session_id": session}, ip_address, user_agent
                        )
                        
                        return {
                            "success": True,
                            "session_id": session,
                            "requires_mfa": False,
                            "user": self._user_to_dict(user)
                        }
                    else:
                        self.audit_logger.log(
                            user.id, username, "mfa_authentication_failed", "login",
                            "failed", {"reason": "invalid_mfa_token"}, ip_address, user_agent
                        )
                        raise MultiFactorException("MFA令牌无效")
                elif user and user.mfa_enabled:
                    # 需要MFA验证
                    return {
                        "success": True,
                        "session_id": None,
                        "requires_mfa": True,
                        "user": self._user_to_dict(user)
                    }
            
            if session:
                # 获取用户信息
                if user is None:
                    user = self.user_manager.get_user_by_username(username)
                return {
                    "success": True,
                    "session_id": session,
                    "requires_mfa": False,
                    "user": self._user_to_dict(user)
                }
                
        except (AuthenticationException, AccountLockoutException, PasswordException, MultiFactorException) as e:
            self.audit_logger.log(
                None, username, "login_failed", "login",
                "failed", {"reason": str(e)}, ip_address, user_agent
            )
            raise
        except Exception as e:
            self.audit_logger.log(
                None, username, "login_error", "login",
                "error", {"error": str(e)}, ip_address, user_agent
            )
            raise AuthenticationException(f"登录过程中发生错误: {str(e)}")
    
    def logout(self, session_id: str, ip_address: str = "127.0.0.1", 
              user_agent: str = "Unknown") -> bool:
        """用户登出"""
        session = self.session_manager.validate_session(session_id)
        if session:
            self.session_manager.terminate_session(session_id)
            
            self.audit_logger.log(
                session.user_id, session.username, "logout", "session",
                "success", {"session_id": session_id}, ip_address, user_agent
            )
            return True
        return False
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """验证会话"""
        session = self.session_manager.validate_session(session_id)
        if session:
            user = self.user_manager.get_user_by_id(session.user_id)
            if user and user.is_active:
                return {
                    "session": session,
                    "user": self._user_to_dict(user),
                    "permissions": self.permission_manager.get_user_permissions(user.id)
                }
        return None
    
    def register_user(self, username: str, email: str, full_name: str, 
                     password: str, role: UserRole = UserRole.USER) -> int:
        """注册新用户"""
        user_id = self.user_manager.create_user(username, email, full_name, password, role)
        
        self.audit_logger.log(
            user_id, username, "user_registered", "user",
            "success", {"role": role.value}, "127.0.0.1", "Registration"
        )
        
        return user_id
    
    def change_password(self, user_id: int, old_password: str, new_password: str):
        """修改密码"""
        self.user_manager.change_password(user_id, old_password, new_password)
        
        self.audit_logger.log(
            user_id, f"user_{user_id}", "password_changed", "user",
            "success", {}, "127.0.0.1", "Password Change"
        )
    
    def reset_password(self, user_id: int, new_password: str):
        """重置密码"""
        self.user_manager.reset_password(user_id, new_password)
        
        self.audit_logger.log(
            user_id, f"user_{user_id}", "password_reset", "user",
            "success", {}, "127.0.0.1", "Password Reset"
        )
    
    def setup_mfa(self, user_id: int) -> Dict[str, Any]:
        """设置MFA"""
        secret = self.mfa_manager.generate_secret()
        user = self.user_manager.get_user_by_id(user_id)
        
        if not user:
            raise SecurityException("用户不存在")
        
        # 生成二维码URL
        qr_url = self.mfa_manager.generate_qr_code_url(user.username, secret)
        
        return {
            "secret": secret,
            "qr_url": qr_url,
            "instructions": "请使用Google Authenticator等应用扫描二维码或手动输入密钥"
        }
    
    def confirm_mfa_setup(self, user_id: int, secret: str, token: str) -> bool:
        """确认MFA设置"""
        if self.mfa_manager.verify_token(secret, token):
            return self.mfa_manager.enable_mfa(user_id, secret)
        return False
    
    def disable_mfa(self, user_id: int):
        """禁用MFA"""
        self.mfa_manager.disable_mfa(user_id)
        
        self.audit_logger.log(
            user_id, f"user_{user_id}", "mfa_disabled", "user",
            "success", {}, "127.0.0.1", "MFA Disable"
        )
    
    def check_permission(self, user_id: int, permission: str) -> bool:
        """检查用户权限"""
        return self.permission_manager.has_permission(user_id, permission)
    
    def get_audit_logs(self, user_id: Optional[int] = None, 
                      start_date: Optional[datetime.datetime] = None,
                      end_date: Optional[datetime.datetime] = None,
                      limit: int = 100) -> List[AuditLog]:
        """获取审计日志"""
        return self.audit_logger.get_logs(user_id, start_date, end_date, limit)
    
    def get_user_sessions(self, user_id: int) -> List[Session]:
        """获取用户会话"""
        return self.session_manager.get_user_sessions(user_id)
    
    def terminate_user_session(self, session_id: str):
        """终止指定会话"""
        self.session_manager.terminate_session(session_id)
    
    def get_password_policy(self) -> PasswordPolicy:
        """获取当前密码策略"""
        return self.config.DEFAULT_PASSWORD_POLICY
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """验证密码策略"""
        return self.password_validator.validate(password)
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """将User对象转换为字典"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "permissions": user.permissions,
            "is_active": user.is_active,
            "mfa_enabled": user.mfa_enabled,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat()
        }


# ============= 使用示例 =============

def example_usage():
    """使用示例"""
    # 初始化安全模块
    auth = SecurityAuthModule()
    
    # 初始化系统（创建默认管理员）
    admin_id = auth.initialize_system()
    print(f"系统初始化完成，管理员ID: {admin_id}")
    
    # 注册用户
    user_id = auth.register_user(
        username="testuser",
        email="test@example.com",
        full_name="测试用户",
        password="TestPassword123!",
        role=UserRole.USER
    )
    print(f"用户注册成功，ID: {user_id}")
    
    # 用户登录
    try:
        result = auth.login(
            username="testuser",
            password="TestPassword123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )
        print(f"登录成功: {result}")
        
        # 验证会话
        session_info = auth.validate_session(result["session_id"])
        if session_info:
            print(f"会话验证成功: {session_info['user']['username']}")
            
            # 检查权限
            if auth.check_permission(user_id, Permission.SALES_CREATE.value):
                print("用户有销售创建权限")
        
        # 用户登出
        auth.logout(result["session_id"])
        print("登出成功")
        
    except Exception as e:
        print(f"登录失败: {e}")
    
    # 获取审计日志
    logs = auth.get_audit_logs(limit=10)
    print(f"审计日志条数: {len(logs)}")


if __name__ == "__main__":
    example_usage()