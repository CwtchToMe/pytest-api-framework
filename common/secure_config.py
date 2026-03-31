"""
安全配置管理 - 支持敏感信息加密存储

使用 Fernet 对称加密保护敏感配置信息
"""
import os
from typing import Optional
from cryptography.fernet import Fernet
import base64
import hashlib
import logging


logger = logging.getLogger(__name__)


class SecureConfig:
    """安全配置管理器 - 支持敏感信息加密"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化安全配置管理器
        
        Args:
            encryption_key: 加密密钥，如果为None则从环境变量获取或自动生成
        """
        if encryption_key is None:
            encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if encryption_key is None:
            # 自动生成密钥（仅用于开发环境）
            logger.warning("未提供加密密钥，使用自动生成的密钥（仅适用于开发环境）")
            encryption_key = Fernet.generate_key().decode()
        
        # 确保密钥是32字节的base64编码
        if len(encryption_key) != 44:
            # 使用SHA256哈希生成32字节密钥
            key_hash = hashlib.sha256(encryption_key.encode()).digest()
            encryption_key = base64.urlsafe_b64encode(key_hash).decode()
        
        try:
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"无效的加密密钥: {e}")
        
        logger.info("安全配置管理器初始化成功")
    
    def encrypt_value(self, value: str) -> str:
        """
        加密配置值
        
        Args:
            value: 要加密的字符串
            
        Returns:
            str: 加密后的字符串（base64编码）
        """
        if not value:
            return ""
        
        try:
            encrypted = self.cipher.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise
    
    def decrypt_value(self, encrypted: str) -> str:
        """
        解密配置值
        
        Args:
            encrypted: 加密的字符串
            
        Returns:
            str: 解密后的原始字符串
        """
        if not encrypted:
            return ""
        
        try:
            decrypted = self.cipher.decrypt(encrypted.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise ValueError(f"解密失败: {e}")
    
    def encrypt_dict(self, data: dict, sensitive_keys: list = None) -> dict:
        """
        加密字典中的敏感字段
        
        Args:
            data: 原始字典
            sensitive_keys: 需要加密的字段列表
            
        Returns:
            dict: 加密后的字典
        """
        if sensitive_keys is None:
            sensitive_keys = ['password', 'token', 'secret', 'apikey', 'api_key', 'authorization']
        
        encrypted_data = data.copy()
        
        for key, value in data.items():
            if isinstance(value, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
                try:
                    encrypted_data[key] = self.encrypt_value(value)
                    logger.debug(f"已加密字段: {key}")
                except Exception as e:
                    logger.warning(f"加密字段 {key} 失败: {e}")
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, sensitive_keys: list = None) -> dict:
        """
        解密字典中的敏感字段
        
        Args:
            data: 加密的字典
            sensitive_keys: 需要解密的字段列表
            
        Returns:
            dict: 解密后的字典
        """
        if sensitive_keys is None:
            sensitive_keys = ['password', 'token', 'secret', 'apikey', 'api_key', 'authorization']
        
        decrypted_data = data.copy()
        
        for key, value in data.items():
            if isinstance(value, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
                try:
                    decrypted_data[key] = self.decrypt_value(value)
                    logger.debug(f"已解密字段: {key}")
                except Exception as e:
                    # 如果解密失败，可能已经是明文，保持原样
                    logger.debug(f"解密字段 {key} 失败，可能已是明文: {e}")
                    decrypted_data[key] = value
        
        return decrypted_data
    
    def is_encrypted(self, value: str) -> bool:
        """
        检查值是否已加密
        
        Args:
            value: 要检查的值
            
        Returns:
            bool: 是否已加密
        """
        if not value:
            return False
        
        try:
            # 尝试解密，如果成功则说明已加密
            self.cipher.decrypt(value.encode())
            return True
        except:
            return False


# 全局实例
_global_secure_config = None


def get_secure_config(encryption_key: Optional[str] = None) -> SecureConfig:
    """
    获取全局安全配置实例
    
    Args:
        encryption_key: 加密密钥
        
    Returns:
        SecureConfig: 安全配置实例
    """
    global _global_secure_config
    if _global_secure_config is None:
        _global_secure_config = SecureConfig(encryption_key)
    return _global_secure_config


def generate_encryption_key() -> str:
    """
    生成新的加密密钥
    
    Returns:
        str: base64编码的加密密钥
    """
    key = Fernet.generate_key()
    return key.decode()


def hash_password(password: str) -> str:
    """
    哈希密码（用于存储）
    
    Args:
        password: 原始密码
        
    Returns:
        str: 哈希后的密码
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()