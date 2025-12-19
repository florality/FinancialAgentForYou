#!/usr/bin/env python3
"""简化的Alpha Vantage金融分析代理 - 直接使用LangChain客户端"""

import os
import asyncio
from dotenv import load_dotenv
from financial_agent import FinancialReportAgent

# 加载环境变量
load_dotenv()

async def main():
    """运行简化的金融分析代理"""
    try:
        # 初始化金融分析代理
        agent = FinancialReportAgent()
        print("✅ 金融分析代理初始化成功")
        
        # 测试API连接
        print("\n🔧 正在测试Alpha Vantage API连接...")
        agent.test_alpha_vantage_api("AAPL")
        
        # 交互式循环
        print("\n🤖 金融分析代理已就绪，请输入您的问题（输入'退出'结束）")
        
        while True:
            try:
                user_input = input("\n💬 请输入问题: ").strip()
                
                if user_input.lower() in ['退出', 'exit', 'quit']:
                    print("👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理用户输入
                if user_input.lower() == "ai行业":
                    user_input = "我想看ai行业的情况，请为我查看一下相关行业和公司的情况和投资建议"
                
                print(f"\n📊 正在分析: {user_input}")
                
                # 使用LangChain客户端直接生成回答
                from langchain_core.prompts import ChatPromptTemplate
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """你是一个专业的金融分析师。使用Alpha Vantage数据来回答关于股票、外汇和其他金融市场的问题。

请遵循以下指导原则：
1. 使用Alpha Vantage工具获取准确的金融数据
2. 提供详细的分析和解释
3. 当被问及股票时，提供技术分析和基本面分析
4. 对于投资建议，请强调风险并建议用户咨询专业顾问
5. 使用清晰、专业的语言进行沟通

在分析财务数据时，请注意：
1. 财务报表数据（收入报表、资产负债表、现金流）通常按季度更新，可能存在1-2个月的延迟
2. 实时股价数据更新频率更高
3. 在分析时请明确指出数据的时间范围和最新更新日期

当需要具体数据时，您可以使用以下方法获取：
- 获取公司全面财务数据：financial_agent.get_comprehensive_alpha_vantage_data(symbol)
- 获取特定类型财务数据：financial_agent.get_alpha_vantage_data(symbol, function)"""),
                    ("human", "{question}")
                ])
                
                # 创建链式调用
                chain = prompt | agent.llm
                
                # 获取回答
                response = chain.invoke({"question": user_input})
                print(f"\n💡 分析结果:\n{response.content}")
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())