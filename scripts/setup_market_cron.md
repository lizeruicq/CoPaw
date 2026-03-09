# 市场数据定时任务设置指南

## 1. 设置环境变量

编辑你的 shell 配置文件（`~/.zshrc` 或 `~/.bash_profile`）：

```bash
# Finnhub API Key
export FINNHUB_API_KEY="d6lutbpr01quej91jtbgd6lutbpr01quej91jtc0"

# 可选：CoPaw 服务地址
export COPAW_BASE_URL="http://127.0.0.1:8088"
```

然后加载配置：
```bash
source ~/.zshrc  # 或 source ~/.bash_profile
```

## 2. 测试脚本

```bash
cd /Users/zeruili/projects/copaw
python3 scripts/market_data_cron.py
```

## 3. 获取飞书用户标识

在 CoPaw 运行时，查看日志获取你的 open_id 和 session_id。

或者通过 API 查询：
```bash
# 列出所有会话
curl http://127.0.0.1:8088/api/chats
```

## 4. 创建定时任务（推荐方式）

### 方式一：使用 CoPaw 内置 Cron（推荐）

```bash
# 每小时整点发送
copaw cron create \
  --type agent \
  --name "每小时市场播报" \
  --cron "0 * * * *" \
  --channel feishu \
  --target-user "YOUR_OPEN_ID" \
  --target-session "YOUR_SESSION_ID" \
  --text "请获取当前黄金价格、纳斯达克100、标普500、道琼斯指数的价格，并整理成简洁的市场播报发送给我。"
```

### 方式二：使用系统 Crontab

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时执行一次）
0 * * * * cd /Users/zeruili/projects/copaw && FINNHUB_API_KEY="d6lutbpr01quej91jtbgd6lutbpr01quej91jtc0" python3 scripts/market_data_cron.py >> /tmp/market_cron.log 2>&1
```

## 5. 查看和管理任务

```bash
# 列出所有定时任务
copaw cron list

# 查看任务详情
copaw cron get <job_id>

# 暂停任务
copaw cron pause <job_id>

# 恢复任务
copaw cron resume <job_id>

# 删除任务
copaw cron delete <job_id>

# 立即执行一次
copaw cron run <job_id>
```

## 6. Cron 表达式参考

| 表达式 | 说明 |
|--------|------|
| `0 * * * *` | 每小时整点 |
| `0 */2 * * *` | 每2小时 |
| `0 9 * * *` | 每天上午9点 |
| `0 9,15 * * *` | 每天上午9点和下午3点 |
| `0 9 * * 1-5` | 工作日上午9点 |
| `*/30 * * * *` | 每30分钟 |

## 7. 查看日志

```bash
# 如果使用 crontab
tail -f /tmp/market_cron.log

# CoPaw 日志
tail -f ~/.copaw/logs/copaw.log
```

## 注意事项

1. **确保 CoPaw 正在运行** 时定时任务才能执行
2. **飞书 channel 已配置** 并启用了长连接
3. **API Key 安全**：不要提交到 Git，使用环境变量
4. **频率限制**：Finnhub 免费版 60次/分钟，每小时一次完全够用
