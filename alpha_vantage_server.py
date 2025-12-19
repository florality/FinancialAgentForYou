#!/usr/bin/env python3
"""
简化的Alpha Vantage服务器 - 避免与系统MCP包冲突
"""
import os
import sys
import json
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators


def get_stock_data(symbol, function="TIME_SERIES_DAILY", interval="daily"):
    """获取股票数据"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY') or os.getenv('Alpha_Vantage_API_Key')
    if not api_key:
        return {"error": "API密钥未设置"}
    
    try:
        ts = TimeSeries(key=api_key)
        
        if function == "TIME_SERIES_INTRADAY":
            data, meta_data = ts.get_intraday(symbol, interval=interval)
        elif function == "TIME_SERIES_DAILY":
            data, meta_data = ts.get_daily(symbol)
        elif function == "TIME_SERIES_WEEKLY":
            data, meta_data = ts.get_weekly(symbol)
        elif function == "TIME_SERIES_MONTHLY":
            data, meta_data = ts.get_monthly(symbol)
        else:
            return {"error": f"不支持的函数: {function}"}
        
        return {
            "symbol": symbol,
            "function": function,
            "data": data.head(10).to_dict(),
            "metadata": meta_data
        }
    except Exception as e:
        return {"error": str(e)}


def get_fundamental_data(symbol, function="OVERVIEW"):
    """获取基本面数据"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY') or os.getenv('Alpha_Vantage_API_Key')
    if not api_key:
        return {"error": "API密钥未设置"}
    
    try:
        fd = FundamentalData(key=api_key)
        
        if function == "OVERVIEW":
            data, meta_data = fd.get_company_overview(symbol)
        elif function == "INCOME_STATEMENT":
            data, meta_data = fd.get_income_statement_annual(symbol)
        elif function == "BALANCE_SHEET":
            data, meta_data = fd.get_balance_sheet_annual(symbol)
        elif function == "CASH_FLOW":
            data, meta_data = fd.get_cash_flow_annual(symbol)
        else:
            return {"error": f"不支持的基本面函数: {function}"}
        
        return {
            "symbol": symbol,
            "function": function,
            "data": data.to_dict() if hasattr(data, 'to_dict') else data,
            "metadata": meta_data
        }
    except Exception as e:
        return {"error": str(e)}


def get_technical_indicator(symbol, indicator, interval="daily", time_period=14):
    """获取技术指标"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY') or os.getenv('Alpha_Vantage_API_Key')
    if not api_key:
        return {"error": "API密钥未设置"}
    
    try:
        ti = TechIndicators(key=api_key)
        
        if indicator.upper() == "RSI":
            data, meta_data = ti.get_rsi(symbol, interval=interval, time_period=time_period)
        elif indicator.upper() == "MACD":
            data, meta_data = ti.get_macd(symbol, interval=interval)
        elif indicator.upper() == "BBANDS":
            data, meta_data = ti.get_bbands(symbol, interval=interval, time_period=time_period)
        else:
            return {"error": f"不支持的技术指标: {indicator}"}
        
        return {
            "symbol": symbol,
            "indicator": indicator,
            "data": data.head(10).to_dict(),
            "metadata": meta_data
        }
    except Exception as e:
        return {"error": str(e)}


def handle_request(request_data):
    """处理JSON请求"""
    try:
        request = json.loads(request_data)
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "get_stock_data":
            result = get_stock_data(
                symbol=params.get("symbol"),
                function=params.get("function", "TIME_SERIES_DAILY"),
                interval=params.get("interval", "daily")
            )
        elif method == "get_fundamental_data":
            result = get_fundamental_data(
                symbol=params.get("symbol"),
                function=params.get("function", "OVERVIEW")
            )
        elif method == "get_technical_indicator":
            result = get_technical_indicator(
                symbol=params.get("symbol"),
                indicator=params.get("indicator"),
                interval=params.get("interval", "daily"),
                time_period=params.get("time_period", 14)
            )
        else:
            result = {"error": f"未知的方法: {method}"}
        
        return json.dumps({"result": result, "id": request.get("id")})
    
    except Exception as e:
        return json.dumps({"error": str(e), "id": request.get("id")})


def main():
    """简单的STDIO服务器"""
    print("Alpha Vantage服务器已启动 (STDIO模式)", file=sys.stderr)
    
    while True:
        try:
            # 读取输入
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            # 处理请求
            response = handle_request(line)
            
            # 输出响应
            print(response)
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = json.dumps({"error": str(e)})
            print(error_response)
            sys.stdout.flush()


if __name__ == "__main__":
    main()