#!/bin/bash
# A股白酒数据更新脚本
# 每小时执行一次，更新股价数据

set -e

REPO_DIR="/Users/fang/.openclaw/workspace/china-baijiu-tracker"
LOG_FILE="$REPO_DIR/update.log"

echo "========================================" >> "$LOG_FILE"
echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

cd "$REPO_DIR"

# 生成当前时间戳
TIMESTAMP=$(date '+%Y年%m月%d日 %H:%M')

# 更新 data.json 中的时间
# 注意：实际股价数据需要接入真实API，这里模拟更新时间
if command -v jq &> /dev/null; then
    jq --arg time "$TIMESTAMP" '.updateTime = $time' data.json > data.json.tmp && mv data.json.tmp data.json
    echo "更新时间戳: $TIMESTAMP" >> "$LOG_FILE"
fi

# 模拟股价波动（实际应接入真实API）
# python3 scripts/update_prices.py

# 检查是否有变更
if git diff --quiet data.json; then
    echo "无数据变更" >> "$LOG_FILE"
else
    echo "检测到数据变更，准备提交..." >> "$LOG_FILE"
    
    git add data.json
    git commit -m "自动更新数据 - $TIMESTAMP"
    git push origin main
    
    echo "数据已推送到GitHub" >> "$LOG_FILE"
fi

echo "更新完成" >> "$LOG_FILE"
