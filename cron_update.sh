#!/bin/bash
# 白酒数据定时更新入口脚本

cd /Users/fang/.openclaw/workspace/china-baijiu-tracker

# 运行Python更新脚本
python3 scripts/update_prices.py

# 检查是否有变更并提交
TIMESTAMP=$(date '+%Y年%m月%d日 %H:%M')

if git diff --quiet data.json; then
    echo "[$TIMESTAMP] 无数据变更"
else
    git add data.json
    git commit -m "自动更新股价数据 - $TIMESTAMP"
    git push origin main
    echo "[$TIMESTAMP] 数据已更新并推送"
fi
