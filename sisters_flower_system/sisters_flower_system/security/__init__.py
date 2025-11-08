"""
安全认证模块包

基于ISO/IEC 15408和NIST SP 800-63B标准实现的安全认证系统
"""

from .auth_module import (
    SecurityAuthModule,
    PasswordPolicy,
    UserManager,
    SessionManager,
    AuditLogger,
    AccountLockout,
    MultiFactorAuth,
    PermissionManager,
    SecurityException,
    AuthenticationException,
    AuthorizationException,
    PasswordException,
    SessionException
)

__all__ = [
    'SecurityAuthModule',
    'PasswordPolicy',
    'UserManager', 
    'SessionManager',
    'AuditLogger',
    'AccountLockout',
    'MultiFactorAuth',
    'PermissionManager',
    'SecurityException',
    'AuthenticationException',
    'AuthorizationException',
    'PasswordException',
    'SessionException'
]

__version__ = '1.0.0'
__author__ = 'Security Team'