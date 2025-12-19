#!/usr/bin/env python3
"""Alpha Vantage金融分析代理 - 简化版（直接使用LangChain）"""

import os
import asyncio
import sys
import datetime
from dotenv import load_dotenv
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# 加载环境变量
load_dotenv()

# 导入MCP相关模块
from mcp_server_manager import MCPServerManager
from agent_display_manager import AgentDisplayManager
from input_manager import InputManager
from session_manager import get_session_database_path, generate_session_id, find_session_by_prefix
from slash_commands import process_slash_command
from financial_agent import FinancialReportAgent

# 导入MCP服务器类
from agents.mcp.server import MCPServerStdio, MCPServerSse, MCPServerStreamableHttp
from agents.mcp.util import MCPUtil


async def main_agent(original_session_id=None, model='Qwen/Qwen3-VL-32B-Instruct', verbose=False):
    """运行交互式金融查询会话，使用Alpha Vantage MCP服务器"""
    
    # 获取当前日期
    current_date = datetime.datetime.now().strftime("%Y年%m月%d日")
    
    # 配置LangChain ChatOpenAI客户端（兼容SiliconFlow API）
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    openrouter_base_url = os.getenv('OPENROUTER_BASE_URL')
    openrouter_model_name = os.getenv('OPENROUTER_MODEL_NAME')
    
    if openrouter_api_key and openrouter_base_url:
        # 使用LangChain ChatOpenAI客户端
        llm = ChatOpenAI(
            model=openrouter_model_name if openrouter_model_name else model,
            api_key=openrouter_api_key,
            base_url=openrouter_base_url,
            temperature=0.7
        )
        
        logger.info(f"使用LangChain客户端配置: {openrouter_base_url}, 模型: {openrouter_model_name if openrouter_model_name else model}")
    else:
        logger.error("未找到有效的API密钥配置")
        return
    
    # 生成会话ID
    if not original_session_id:
        session_id = generate_session_id()
    else:
        matching_session = find_session_by_prefix(original_session_id)
        session_id = matching_session if matching_session else original_session_id
    
    # 配置日志
    if not verbose:
        logger.disable("mcp_server_manager")
    
    # 初始化MCP服务器管理器
    mcp_manager = MCPServerManager("mcp.json")
    
    # 初始化显示管理器和输入管理器
    display_manager = AgentDisplayManager()
    input_manager = InputManager(display_manager.console)
    
    # 初始化金融分析代理（用于Alpha Vantage API调用）
    financial_agent = FinancialReportAgent()
    
    async with mcp_manager:
        # 获取初始化的服务器
        servers = mcp_manager.get_servers()
        
        # 打印MCP服务器信息和可用工具
        display_manager.console.print("[bold green]📊 已连接的MCP服务器:[/bold green]")
        for i, server in enumerate(servers):
            display_manager.console.print(f"  {i+1}. {server.name}")
            
            # 获取服务器的工具列表
            try:
                tools = await server.list_tools()
                display_manager.console.print(f"     可用工具 ({len(tools)}个):")
                for tool in tools:
                    display_manager.console.print(f"       - {tool.name}: {tool.description}")
            except Exception as e:
                display_manager.console.print(f"     获取工具列表失败: {e}")
        
        # 欢迎消息
        if not original_session_id:
            display_manager.display_welcome(session_id)
        
        # 交互循环
        conversation_history = []
        
        while True:
            try:
                # 获取用户输入
                user_input, _, _ = input_manager.get_input()
                
                # 检查退出命令
                if input_manager.is_exit_command(user_input):
                    display_manager.display_goodbye()
                    break
                
                if not user_input.strip():
                    continue
                
                # 检查斜杠命令
                if user_input.startswith('/'):
                    new_session_id, new_session = await process_slash_command(user_input, display_manager)
                    if new_session_id and new_session:
                        session_id = new_session_id
                        # 重置对话历史
                        conversation_history = []
                    continue
                
                # 添加用户输入到对话历史
                conversation_history.append(HumanMessage(content=user_input))
                
                # 构建系统提示
                system_prompt = f"""你是一个专业的金融分析师。使用Alpha Vantage数据来回答关于股票、外汇和其他金融市场的问题。

今天是{current_date}，请基于最新的数据进行分析。

请遵循以下指导原则：
1. 使用Alpha Vantage工具获取准确的金融数据
2. 提供详细的分析和解释
3. 当被问及股票时，提供技术分析和基本面分析
4. 对于投资建议，请强调风险并建议用户咨询专业顾问
5. 使用清晰、专业的语言进行沟通

你可以使用以下工具：
1. 获取公司财务数据 - 通过调用 financial_agent.get_comprehensive_alpha_vantage_data(symbol) 获取公司的全面财务数据
2. 获取特定类型的财务数据 - 通过调用 financial_agent.get_alpha_vantage_data(symbol, function) 获取特定类型的财务数据

在需要具体数据时，请使用这些工具获取最新、最准确的信息。

注意数据时效性：
- 财务报表数据（收入报表、资产负债表、现金流）通常按季度更新，可能存在1-2个月的延迟
- 实时股价数据更新频率更高
- 在分析时请明确指出数据的时间范围和最新更新日期
- 请优先使用最近一个交易日的数据进行分析

报告结构要求：
1. 执行摘要（核心结论先行）
2. 市场表现与估值快照
3. 技术分析：趋势、动能与关键位（需包含关键价位与情景推演）
4. 基本面深度剖析（每个财务数据后添加分析要点）
5. 行业动力与竞争格局
6. 风险评估矩阵（用表格形式呈现）
7. 市场共识
8. 投资建议与策略（按投资者类型分别阐述）

请确保：
- 使用同比/环比增长率、百分比、与行业对比来强化观点
- 保持客观、专业的分析师语气
- 确保各部分分析最终能支撑"投资建议"的结论
"""

                # 构建消息列表
                messages = [SystemMessage(content=system_prompt)] + conversation_history
                
                # 调用模型生成回复（流式输出）
                display_manager.console.print("\n[bold blue]💡 分析结果:[/bold blue]")
                response_content = ""
                
                # 流式输出响应
                for chunk in llm.stream(messages):
                    if hasattr(chunk, 'content'):
                        chunk_content = chunk.content
                        print(chunk_content, end='', flush=True)
                        response_content += chunk_content
                
                print()  # 换行
                
                # 添加助手回复到对话历史
                conversation_history.append(HumanMessage(content=response_content))
                
                # 保持对话历史在一个合理的长度
                if len(conversation_history) > 10:  # 保留最近5轮对话
                    conversation_history = conversation_history[-10:]
                
            except KeyboardInterrupt:
                display_manager.display_goodbye()
                break
            except Exception as e:
                display_manager.display_error(f"发生错误: {str(e)}")


if __name__ == "__main__":
    # 解析命令行参数
    session_id = None
    model = 'Qwen/Qwen3-VL-32B-Instruct'
    verbose = False
    
    for arg in sys.argv[1:]:
        if arg.startswith('--session='):
            session_id = arg.split('=')[1]
        elif arg.startswith('--model='):
            model = arg.split('=')[1]
        elif arg == '--verbose':
            verbose = True
    
    # 运行主程序
    asyncio.run(main_agent(session_id, model, verbose))