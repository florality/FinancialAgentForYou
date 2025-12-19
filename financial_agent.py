import os
import requests
import json
import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class FinancialReportAgent:
    def __init__(self):
        # 从环境变量获取配置
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL_NAME")
        self.base_url = os.getenv("OPENROUTER_BASE_URL")
        self.alpha_vantage_key = os.getenv("Alpha_Vantage_API_Key") or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.alpha_vantage_key2 = os.getenv("Alpha_Vantage_API_Key2")
        
        if not self.api_key:
            raise ValueError("请设置OPENROUTER_API_KEY环境变量")
        
        if not self.alpha_vantage_key:
            raise ValueError("请设置Alpha_Vantage_API_Key环境变量")

        # 初始化ChatOpenAI客户端
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0.7
        )

    def test_alpha_vantage_api(self, symbol: str = "AAPL"):
        """测试Alpha Vantage API连接和可用性"""
        print("=" * 50)
        print("开始测试Alpha Vantage API...")
        print("=" * 50)
        
        # 测试不同的API密钥
        api_keys = [self.alpha_vantage_key]
        if self.alpha_vantage_key2:
            api_keys.append(self.alpha_vantage_key2)
        
        # 测试不同的函数类型
        functions = [
            'OVERVIEW',           # 公司概览
            'TIME_SERIES_DAILY',  # 日线数据
            'GLOBAL_QUOTE',       # 实时报价
            'INCOME_STATEMENT'    # 收入报表
        ]
        
        for i, api_key in enumerate(api_keys):
            print(f"\n测试API密钥 {i+1}: {api_key[:8]}...")
            
            for function in functions:
                print(f"\n测试函数: {function}")
                
                base_url = "https://www.alphavantage.co/query"
                params = {
                    'function': function,
                    'symbol': symbol,
                    'apikey': api_key,
                    'outputsize': 'compact',
                    'datatype': 'json'
                }
                
                try:
                    response = requests.get(base_url, params=params)
                    print(f"  HTTP状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'Error Message' in data:
                            print(f"  ❌ API错误: {data['Error Message'][:100]}...")
                        elif 'Note' in data:
                            print(f"  ⚠️  API提示: {data['Note'][:100]}...")
                        elif 'Information' in data:
                            print(f"  ℹ️  API信息: {data['Information'][:100]}...")
                        else:
                            print(f"  ✅ 成功获取数据，响应包含键: {list(data.keys())}")
                            
                    else:
                        print(f"  ❌ HTTP错误: {response.status_code} - {response.reason}")
                        
                except Exception as e:
                    print(f"  ❌ 请求异常: {e}")
                
                # 避免请求频率限制
                time.sleep(1)
        
        print("\n" + "=" * 50)
        print("API测试完成")
        print("=" * 50)

    def get_comprehensive_alpha_vantage_data(self, symbol: str) -> Dict[str, Any]:
        """获取多种Alpha Vantage金融数据，提供更全面的分析基础"""
        print(f"正在获取 {symbol} 的全面金融数据...")
        
        # 定义要获取的数据类型
        data_functions = {
            'overview': 'OVERVIEW',           # 公司概览
            'income_statement': 'INCOME_STATEMENT',  # 收入报表
            'balance_sheet': 'BALANCE_SHEET',        # 资产负债表
            'cash_flow': 'CASH_FLOW',                # 现金流
            'global_quote': 'GLOBAL_QUOTE'           # 实时报价
        }
        
        comprehensive_data = {}
        successful_requests = 0
        
        for data_name, function in data_functions.items():
            print(f"\n获取 {data_name} 数据...")
            
            try:
                data = self.get_alpha_vantage_data(symbol, function)
                
                if data and 'Error Message' not in data and 'Information' not in data:
                    # 添加数据时间信息
                    data_info = {
                        "data": data,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "function": function
                    }
                    comprehensive_data[data_name] = data_info
                    successful_requests += 1
                    print(f"✅ {data_name} 数据获取成功")
                else:
                    print(f"⚠️ {data_name} 数据获取失败或受限")
                    comprehensive_data[data_name] = {"status": "failed"}
                
            except Exception as e:
                print(f"❌ {data_name} 数据获取异常: {e}")
                comprehensive_data[data_name] = {"status": "error", "message": str(e)}
            
            # 避免频率限制
            if successful_requests > 0:
                time.sleep(12)  # 免费版限制5次/分钟，每次请求后等待12秒
        
        print(f"\n数据获取完成: {successful_requests}/{len(data_functions)} 种数据类型获取成功")
        return comprehensive_data

    def analyze_financial_data_timestamps(self, data: Dict[str, Any]) -> str:
        """分析财务数据的时间戳信息"""
        analysis = []
        
        for key, value in data.items():
            if isinstance(value, dict) and "data" in value:
                function = value.get("function", "Unknown")
                timestamp = value.get("timestamp", "Unknown")
                data_content = value.get("data", {})
                
                analysis.append(f"- {key} ({function}): 获取时间 {timestamp}")
                
                # 对于财务报表，尝试找出最新的报告期
                if function in ['INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW']:
                    if 'annualReports' in data_content and data_content['annualReports']:
                        latest_year = list(data_content['annualReports'].keys())[0]
                        analysis.append(f"  最新年报: {latest_year}")
                    if 'quarterlyReports' in data_content and data_content['quarterlyReports']:
                        latest_quarter = list(data_content['quarterlyReports'].keys())[0]
                        analysis.append(f"  最新季报: {latest_quarter}")
        
        return "\n".join(analysis)

    def get_alpha_vantage_data(self, symbol: str, function: str = 'TIME_SERIES_DAILY') -> Dict[str, Any]:
        """从Alpha Vantage API获取金融数据"""
        try:
            print(f"正在从Alpha Vantage获取 {symbol} 的 {function} 数据...")
            base_url = "https://www.alphavantage.co/query"

            params = {
                'function': function,
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'compact',
                'datatype': 'json'
            }

            print(f"请求参数: {params}")
            
            response = requests.get(base_url, params=params)
            print(f"HTTP状态码: {response.status_code}")
            
            response.raise_for_status()

            # 处理可能的编码问题
            try:
                data = response.json()
            except UnicodeDecodeError:
                # 如果遇到编码问题，尝试使用不同的编码方式
                content = response.content.decode('utf-8', errors='ignore')
                data = json.loads(content)
            
            # 详细的API响应分析
            print(f"API响应键: {list(data.keys()) if data else '无数据'}")
            
            if 'Error Message' in data:
                error_msg = data['Error Message']
                print(f"❌ API错误信息: {error_msg}")
                
                # 分析常见错误类型
                if 'Invalid API call' in error_msg:
                    print("💡 可能原因: 函数类型或股票代码不正确")
                elif 'Thank you for using Alpha Vantage' in error_msg:
                    print("💡 可能原因: API调用频率限制，请稍后重试")
                elif 'apikey' in error_msg.lower():
                    print("💡 可能原因: API密钥无效或过期")
                    
            if 'Note' in data:
                print(f"⚠️ API提示信息: {data['Note']}")
            if 'Information' in data:
                print(f"ℹ️ API信息: {data['Information']}")
            
            # 检查是否成功获取数据
            if 'Time Series (Daily)' in data:
                daily_data = data['Time Series (Daily)']
                print(f"✅ 获取到 {len(daily_data)} 天的日线数据")
                if daily_data:
                    first_date = list(daily_data.keys())[0]
                    print(f"最近一天数据 ({first_date}): {daily_data[first_date]}")
            elif 'Global Quote' in data:
                quote = data['Global Quote']
                print(f"✅ 获取到实时报价: {quote}")
            elif 'Symbol' in data:
                print(f"✅ 获取到公司概览数据")
            
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求错误: {e}")
            return {"error": f"请求错误: {e}"}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return {"error": f"JSON解析错误: {e}"}
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return {"error": f"未知错误: {e}"}

    def generate_report(self, company_name: str, symbol: str = None) -> str:
        """生成基于Alpha Vantage数据的金融分析报告"""
        try:
            # 如果没有提供股票代码，使用公司名称作为默认
            if not symbol:
                symbol = company_name.upper()[:4]
            
            print(f"正在获取 {symbol} 的金融数据...")
            
            # 先测试API连接
            self.test_alpha_vantage_api(symbol)
            
            # 获取全面的金融数据
            api_data = self.get_comprehensive_alpha_vantage_data(symbol)
            
            # 显示数据时间戳信息
            print("\n" + "=" * 50)
            print("数据时间戳分析:")
            print("=" * 50)
            timestamp_analysis = self.analyze_financial_data_timestamps(api_data)
            print(timestamp_analysis)
            print("=" * 50)
            
            # 检查是否获取到有效数据
            successful_data_count = sum(1 for data in api_data.values() 
                                      if isinstance(data, dict) and 
                                      'Error Message' not in data and 
                                      'Information' not in data and
                                      'status' not in data)
            
            if successful_data_count == 0:
                return "获取金融数据失败: 所有API调用都返回错误或受限信息"
            
            print(f"成功获取 {successful_data_count} 种金融数据类型，正在生成报告...")
            
            # 创建包含API数据的提示模板，使用新的分析框架
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的金融分析师，请基于提供的原始财务数据生成详细的金融分析报告。"),
                ("human", """
请为{company_name}({symbol})生成一份专业的金融分析报告，采用以下结构：

# 金融分析报告 - {company_name}({symbol})

## 执行摘要
用一段话概括核心结论，必须包含：
1) 核心观点（看涨/中性/谨慎）
2) 核心数据依据（如增长、估值）
3) 关键风险
4) 最终策略建议

## 市场表现与估值快照
提供关键市场数据和估值指标

## 技术分析：趋势、动能与关键位
分析技术指标，并添加"关键价位与情景推演"小节：
1) 近期支撑位/阻力位
2) 基于指标的短期情景推演（如果…则…）

## 基本面深度剖析
深入分析财务数据，每个财务数据表格或段落下方需添加"分析要点"：
- 用2-3个要点提炼趋势、增长率、盈利能力变化的洞察
- 计算并指出营收与净利润的同比增速、毛利率变化趋势的意义

## 行业动力与竞争格局
分析行业趋势和公司在行业中的地位

## 风险评估矩阵
用表格呈现风险，列包括：风险类别、发生概率(高/中/低)、潜在影响(高/中/低)、简要评述

## 市场共识
总结市场对该公司的一致预期

## 投资建议与策略
按投资者类型（如激进型、稳健型、保守型）分别阐述：
1) 核心逻辑
2) 具体策略（如"分批建仓于$X以下"）
3) 关键监测指标

原始财务数据（JSON格式）：
{financial_data}

请特别注意以下几点：
1. 注意财务数据的时效性，明确指出最新数据的报告期
2. 解释为什么某些数据可能不是最新的（如季度财报的自然延迟）
3. 基于原始数据进行专业、客观的分析，并自动提取关键信息
4. 使用同比/环比增长率、百分比、与行业对比来强化观点
5. 保持客观、专业的分析师语气
6. 确保各部分分析最终能支撑"投资建议"的结论
""")
            ])
            
            # 格式化提示词，直接传递原始JSON数据，处理可能的编码问题
            try:
                prompt = prompt_template.format_messages(
                    company_name=company_name,
                    symbol=symbol,
                    financial_data=json.dumps(api_data, ensure_ascii=False, indent=2)
                )
            except UnicodeEncodeError:
                # 如果遇到编码问题，使用ASCII安全的编码方式
                prompt = prompt_template.format_messages(
                    company_name=company_name,
                    symbol=symbol,
                    financial_data=json.dumps(api_data, ensure_ascii=True, indent=2)
                )

            # 调用模型生成报告（流式输出）
            response = ""
            try:
                for chunk in self.llm.stream(prompt):
                    if hasattr(chunk, 'content'):
                        chunk_content = chunk.content
                        print(chunk_content, end='', flush=True)
                        response += chunk_content
            except UnicodeEncodeError as e:
                # 处理输出时的编码问题
                print(f"\n编码错误已处理: {str(e)[:50]}...")
                pass  # 继续执行而不中断
            
            return response

        except Exception as e:
            return f"生成报告时出错: {str(e)}"


# 使用示例
if __name__ == "__main__":
    # 创建agent
    agent = FinancialReportAgent()

    # 测试数据
    company_name = "苹果公司"
    symbol = "AAPL"  # 苹果公司的股票代码
    
    # 生成报告（流式输出）
    print(f"正在为 {company_name}({symbol}) 生成金融分析报告...")
    print("=" * 60)
    
    report = agent.generate_report(company_name, symbol)
    
    print("\n" + "=" * 60)
    print("报告生成完成！")

    # 保存到文件
    filename = f"{company_name}_金融分析报告.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n报告已保存到 '{filename}'")