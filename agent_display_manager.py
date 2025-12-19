from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
import json

class AgentDisplayManager:
    """管理代理的显示输出"""
    
    def __init__(self):
        self.console = Console()
    
    def display_welcome(self, session_id):
        """显示欢迎信息"""
        welcome_text = Text()
        welcome_text.append("🤖 Alpha Vantage 金融分析代理\n", style="bold blue")
        welcome_text.append(f"会话ID: {session_id}\n", style="green")
        welcome_text.append("请输入您的金融查询问题，或输入 /help 查看可用命令", style="italic")
        
        self.console.print(Panel(welcome_text, title="欢迎使用", border_style="blue"))
    
    def display_agent_config(self, agent_config):
        """显示代理配置"""
        self.console.print(f"📋 代理配置: {agent_config.name}")
    
    def display_tool_execution(self, tool_name, arguments, call_id):
        """显示工具执行信息"""
        table = Table(title=f"🛠️ 执行工具: {tool_name}", show_header=False)
        table.add_column("字段", style="cyan")
        table.add_column("值", style="white")
        
        table.add_row("工具名称", tool_name)
        if arguments:
            table.add_row("参数", json.dumps(arguments, indent=2, ensure_ascii=False))
        if call_id:
            table.add_row("调用ID", call_id)
        
        self.console.print(table)
    
    def display_tool_result(self, output_str, call_id):
        """显示工具执行结果"""
        try:
            # 尝试解析JSON输出
            output_data = json.loads(output_str)
            formatted_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        except:
            formatted_output = output_str
        
        panel = Panel(
            formatted_output,
            title=f"📊 工具执行结果",
            border_style="green"
        )
        self.console.print(panel)
    
    def display_agent_response(self, content):
        """显示代理响应"""
        if isinstance(content, list):
            for item in content:
                if hasattr(item, 'text'):
                    self.console.print(Markdown(item.text))
        elif hasattr(content, 'text'):
            self.console.print(Markdown(content.text))
        else:
            self.console.print(Markdown(str(content)))
    
    def display_info(self, message):
        """显示信息消息"""
        self.console.print(f"ℹ️ {message}", style="blue")
    
    def display_error(self, message):
        """显示错误消息"""
        self.console.print(f"❌ {message}", style="red")
    
    def display_goodbye(self):
        """显示退出信息"""
        self.console.print("👋 感谢使用Alpha Vantage金融分析代理！", style="bold green")
    
    def display_session_items(self, items):
        """显示会话历史"""
        self.console.print("📚 加载会话历史...", style="bold")