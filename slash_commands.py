import asyncio
from agents import SQLiteSession
from session_manager import get_session_database_path, generate_session_id

async def process_slash_command(user_input, display_manager):
    """处理斜杠命令"""
    if user_input.startswith('/help'):
        display_manager.console.print("""
可用命令:
/help - 显示此帮助信息
/exit - 退出程序
/new - 开始新会话
/resume <session_id> - 恢复指定会话
        """)
        return None, None
    
    elif user_input.startswith('/new'):
        new_session_id = generate_session_id()
        new_session = SQLiteSession(new_session_id, get_session_database_path())
        display_manager.display_info(f"已创建新会话: {new_session_id}")
        return new_session_id, new_session
    
    elif user_input.startswith('/resume'):
        # 简化实现
        display_manager.display_info("恢复会话功能暂未实现")
        return None, None
    
    return None, None