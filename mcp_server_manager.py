import json
import asyncio
from contextlib import AsyncExitStack
from agents.mcp import MCPServer
from loguru import logger

class MCPServerManager:
    """管理MCP服务器的生命周期"""
    
    def __init__(self, config_path="mcp.json"):
        self.config_path = config_path
        self.servers = {}
        self.exit_stack = AsyncExitStack()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.load_servers()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.exit_stack.aclose()
    
    async def load_servers(self):
        """从配置文件加载MCP服务器"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            servers_config = config.get('servers', {})
            
            for server_name, server_config in servers_config.items():
                try:
                    server_type = server_config.get('type')
                    
                    if server_type == 'stdio':
                        server = MCPServer.create_stdio_server(
                            command=server_config['command'],
                            args=server_config.get('args', [])
                        )
                    elif server_type == 'http':
                        server = MCPServer.create_http_server(
                            url=server_config['url']
                        )
                    else:
                        logger.warning(f"未知的服务器类型: {server_type}")
                        continue
                    
                    # 启动服务器
                    await self.exit_stack.enter_async_context(server)
                    self.servers[server_name] = server
                    logger.info(f"已加载MCP服务器: {server_name}")
                    
                except Exception as e:
                    logger.error(f"加载服务器 {server_name} 失败: {e}")
        
        except FileNotFoundError:
            logger.error(f"MCP配置文件未找到: {self.config_path}")
        except json.JSONDecodeError:
            logger.error(f"MCP配置文件格式错误: {self.config_path}")
        except Exception as e:
            logger.error(f"加载MCP配置失败: {e}")
    
    def get_servers(self):
        """获取已加载的服务器列表"""
        return list(self.servers.values())