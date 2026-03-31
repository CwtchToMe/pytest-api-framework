"""
安全模块 - 敏感信息过滤和脱敏

提供敏感信息过滤功能，防止密码、token等敏感信息泄露到日志中
"""
import re
import logging
from typing import List, Pattern


class SensitiveDataFilter(logging.Filter):
    """
    敏感信息过滤器 - 自动过滤日志中的敏感数据
    """
    
    SENSITIVE_FIELDS = [
        'password', 'passwd', 'pwd', 'secret', 'token', 'apikey', 
        'api_key', 'authorization', 'auth', 'credential', 'credit_card'
    ]
    
    def __init__(self):
        super().__init__()
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[Pattern]:
        """编译正则表达式模式"""
        patterns = []
        
        # 匹配 JSON 中的敏感字段
        for field in self.SENSITIVE_FIELDS:
            pattern = re.compile(
                r'(' + field + r'["\s]*[:=]["\s]*)([^",}\s]+)',
                re.IGNORECASE
            )
            patterns.append(pattern)
        
        # 匹配 URL 中的敏感参数
        url_pattern = re.compile(
            r'(' + '|'.join(self.SENSITIVE_FIELDS) + r')=[^&\s]+',
            re.IGNORECASE
        )
        patterns.append(url_pattern)
        
        # 匹配 Bearer Token
        bearer_pattern = re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE)
        patterns.append(bearer_pattern)
        
        return patterns
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录中的敏感信息
        
        Args:
            record: 日志记录
            
        Returns:
            bool: 是否允许记录
        """
        if record.msg:
            record.msg = self._sanitize_data(str(record.msg))
        
        if hasattr(record, 'args') and record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, (dict, str)):
                    new_args.append(self._sanitize_data(str(arg)))
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        
        return True
    
    def _sanitize_data(self, data: str) -> str:
        """
        清理数据中的敏感信息
        
        Args:
            data: 原始数据
            
        Returns:
            str: 清理后的数据
        """
        sanitized = data
        
        for pattern in self.patterns:
            sanitized = pattern.sub(r'\1***', sanitized)
        
        return sanitized


def setup_sensitive_data_filter(logger: logging.Logger):
    """
    为日志器设置敏感信息过滤器
    
    Args:
        logger: 日志器对象
    """
    sensitive_filter = SensitiveDataFilter()
    logger.addFilter(sensitive_filter)


class DataMasker:
    """数据脱敏工具类"""
    
    @staticmethod
    def mask_password(password: str, visible_chars: int = 0) -> str:
        """
        脱敏密码
        
        Args:
            password: 原始密码
            visible_chars: 可见字符数
            
        Returns:
            str: 脱敏后的密码
        """
        if not password:
            return "***"
        
        if visible_chars <= 0:
            return "***"
        
        if len(password) <= visible_chars:
            return password[0] + "*" * (len(password) - 1)
        
        return password[:visible_chars] + "*" * (len(password) - visible_chars)
    
    @staticmethod
    def mask_email(email: str) -> str:
        """
        脱敏邮箱
        
        Args:
            email: 原始邮箱
            
        Returns:
            str: 脱敏后的邮箱
        """
        if not email or '@' not in email:
            return "***@***.***"
        
        local, domain = email.split('@', 1)
        
        if len(local) > 2:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        else:
            masked_local = "*" * len(local)
        
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            masked_domain = domain_parts[0][0] + "*" * (len(domain_parts[0]) - 1)
            masked_domain += "." + ".".join(domain_parts[1:])
        else:
            masked_domain = domain[0] + "*" * (len(domain) - 1)
        
        return f"{masked_local}@{masked_domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        脱敏电话号码
        
        Args:
            phone: 原始电话号码
            
        Returns:
            str: 脱敏后的电话号码
        """
        if not phone:
            return "***"
        
        cleaned = re.sub(r'[^\d]', '', phone)
        
        if len(cleaned) <= 4:
            return "*" * len(cleaned)
        
        return cleaned[:3] + "*" * (len(cleaned) - 6) + cleaned[-3:]
    
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """
        脱敏信用卡号
        
        Args:
            card_number: 原始信用卡号
            
        Returns:
            str: 脱敏后的信用卡号
        """
        if not card_number:
            return "**** **** **** ****"
        
        cleaned = re.sub(r'[^\d]', '', card_number)
        
        if len(cleaned) < 4:
            return "*" * len(cleaned)
        
        return "*" * (len(cleaned) - 4) + cleaned[-4:]
    
    @staticmethod
    def mask_dict(data: dict, sensitive_keys: List[str] = None) -> dict:
        """
        脱敏字典中的敏感字段
        
        Args:
            data: 原始字典
            sensitive_keys: 敏感字段列表
            
        Returns:
            dict: 脱敏后的字典
        """
        if sensitive_keys is None:
            sensitive_keys = SensitiveDataFilter.SENSITIVE_FIELDS
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, str):
                    if 'password' in key.lower():
                        masked_data[key] = DataMasker.mask_password(value)
                    elif 'email' in key.lower():
                        masked_data[key] = DataMasker.mask_email(value)
                    elif 'phone' in key.lower():
                        masked_data[key] = DataMasker.mask_phone(value)
                    else:
                        masked_data[key] = "***"
        
        return masked_data