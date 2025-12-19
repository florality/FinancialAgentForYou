class InputManager:
    """管理用户输入"""
    
    def __init__(self, console):
        self.console = console
    
    def get_input(self):
        """获取用户输入"""
        try:
            user_input = input("\n💬 请输入问题: ").strip()
            return user_input, None, None
        except (EOFError, KeyboardInterrupt):
            return "/exit", None, None
    
    def is_exit_command(self, user_input):
        """检查是否为退出命令"""
        return user_input.lower() in ['/exit', '/quit', 'exit', 'quit']