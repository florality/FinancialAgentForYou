import os
import uuid
from agents import SQLiteSession
from datetime import datetime

def get_session_database_path():
    """获取会话数据库路径"""
    return os.path.join(os.path.dirname(__file__), "sessions.db")

def generate_session_id():
    """生成唯一的会话ID"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def find_session_by_prefix(prefix):
    """根据前缀查找会话ID"""
    # 简化实现，实际应该查询数据库
    return None  # 返回匹配的会话ID或None