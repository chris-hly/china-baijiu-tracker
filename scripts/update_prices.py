#!/usr/bin/env python3
"""
A股白酒数据更新脚本
功能：从公开API获取白酒股票最新价格，更新data.json
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
import time

# 白酒股票代码列表
STOCKS = {
    "tier1": [
        {"name": "贵州茅台", "code": "600519", "market": "sh"},
        {"name": "五粮液", "code": "000858", "market": "sz"},
        {"name": "泸州老窖", "code": "000568", "market": "sz"},
    ],
    "tier2": [
        {"name": "山西汾酒", "code": "600809", "market": "sh"},
        {"name": "洋河股份", "code": "002304", "market": "sz"},
        {"name": "古井贡酒", "code": "000596", "market": "sz"},
        {"name": "今世缘", "code": "603369", "market": "sh"},
    ],
    "tier3": [
        {"name": "口子窖", "code": "603589", "market": "sh"},
        {"name": "迎驾贡酒", "code": "604198", "market": "sh"},
        {"name": "水井坊", "code": "600779", "market": "sh"},
        {"name": "舍得酒业", "code": "600702", "market": "sh"},
    ]
}

def get_stock_price_sina(code, market):
    """从新浪财经API获取股价（公开接口）"""
    # 新浪财经接口格式
    symbol = f"{market}{code}"
    url = f"http://hq.sinajs.cn/list={symbol}"
    
    try:
        req = urllib.request.Request(url, headers={
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk')
            
        # 解析返回数据
        if 'hq_str_' in data:
            parts = data.split('"')[1].split(',')
            if len(parts) >= 32:
                name = parts[0]
                current_price = float(parts[3]) if parts[3] else 0
                change_percent = float(parts[32].strip('%')) if parts[32] else 0
                return {
                    "name": name,
                    "price": current_price,
                    "change": change_percent
                }
    except Exception as e:
        print(f"获取 {code} 价格失败: {e}")
    
    return None

def get_stock_price_tushare_style(code):
    """备用：东方财富接口"""
    # 东方财富接口
    secid = f"1.{code}" if code.startswith('6') else f"0.{code}"
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        if data and 'data' in data and data['data']:
            d = data['data']
            price = d.get('f43', 0) / 100 if d.get('f43') else 0
            change = d.get('f170', 0) / 100 if d.get('f170') else 0
            return {
                "price": price,
                "change": change
            }
    except Exception as e:
        print(f"东方财富获取 {code} 失败: {e}")
    
    return None

def is_trading_time():
    """检查是否在交易时间内（A股：周一至周五 9:30-11:30, 13:00-15:00）"""
    now = datetime.now()
    weekday = now.weekday()
    
    # 周末不交易
    if weekday >= 5:
        return False
    
    hour = now.hour
    minute = now.minute
    
    # 上午 9:30-11:30
    if hour == 9 and minute >= 30:
        return True
    if hour == 10:
        return True
    if hour == 11 and minute <= 30:
        return True
    
    # 下午 13:00-15:00
    if hour == 13 or hour == 14:
        return True
    if hour == 15 and minute == 0:
        return True
    
    return False

def update_data():
    """更新data.json文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    data_file = os.path.join(repo_dir, 'data.json')
    
    # 读取现有数据
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查是否在交易时间
    trading = is_trading_time()
    if not trading:
        print("当前非交易时间，仅更新时间戳")
        data['updateTime'] = datetime.now().strftime('%Y年%m月%d日 %H:%M') + " (休市)"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return False
    
    # 更新时间
    data['updateTime'] = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    
    updated = False
    
    # 更新每个梯队的股价
    for tier_name, stocks in STOCKS.items():
        for stock in stocks:
            # 尝试获取股价
            price_data = get_stock_price_tushare_style(stock['code'])
            
            if price_data and price_data['price'] > 0:
                # 更新对应公司的数据
                for company in data['companies'][tier_name]:
                    if company['code'].startswith(stock['code']):
                        old_price = company['price']
                        company['price'] = round(price_data['price'], 2)
                        company['change'] = round(price_data['change'], 2)
                        
                        if old_price != company['price']:
                            updated = True
                            print(f"更新 {stock['name']}: {old_price} -> {company['price']}")
                        break
                
                time.sleep(0.3)  # 避免请求过快
    
    # 保存更新后的数据
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return updated

if __name__ == '__main__':
    print(f"开始更新数据: {datetime.now()}")
    updated = update_data()
    if updated:
        print("数据已更新")
    else:
        print("无数据变更")
