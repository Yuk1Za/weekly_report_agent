# 快速开始指南 (5 分钟上手)

## 方案概览

这个项目使用 Claude AI Agent 自动生成周报，支持：
- ✅ 多数据源集成（Analytics、Ads、CRM）
- ✅ 智能分析和洞察
- ✅ Markdown 报告生成
- ✅ 定时 Slack 推送

## 快速安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API 密钥
cp .env.template .env
# 编辑 .env，填入 ANTHROPIC_API_KEY
nano .env

# 3. 运行生成周报
python weekly_report_agent.py
```

## 代码文件说明

| 文件 | 作用 | 何时使用 |
|------|------|--------|
| `weekly_report_agent.py` | 核心 Agent 逻辑，包含数据模拟和报告生成 | 首次运行、单次生成 |
| `scheduler.py` | 定时任务调度器 | 生产环境，每周一定时执行 |
| `advanced_data_sources.py` | 真实 API 集成（GA4、Facebook Ads、Salesforce） | 需要真实数据时 |
| `requirements.txt` | Python 依赖包 | 安装环境 |
| `.env.template` | 环境变量模板 | 配置 API 密钥 |
| `Dockerfile` | Docker 镜像定义 | 容器化部署 |
| `docker-compose.yml` | 容器编排配置 | Docker 部署 |

## 工作流程

```
┌─────────────────────┐
│  Agent 启动         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  并行获取三个数据源 │
│  - Analytics        │
│  - Ads              │
│  - CRM              │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Claude 分析数据    │
│  - 趋势识别         │
│  - 异常检测         │
│  - 洞察挖掘         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  生成 Markdown 报告 │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  推送到 Slack       │
│  (可选)             │
└─────────────────────┘
```

## 实际示例输出

### 输入命令
```bash
$ python weekly_report_agent.py
```

### 输出报告
```markdown
# 周报 - 2024 年 05 月 03 日

## 概述
本周整体业务表现稳定，流量环比增长 12.3%，广告投资回报率保持高水平。
销售团队成交 35 个订单，创造 58 万元收入，环比增长 11.5%。

## 关键指标

| 指标 | 本周 | 上周 | 变化 |
|------|------|------|------|
| 页面浏览量 (PV) | 55,000 | 50,000 | +10.0% |
| 独立访客 (UV) | 13,000 | 12,000 | +8.3% |
| 转化率 | 3.5% | 3.2% | +0.3pp |
| 广告花费 | ¥18,000 | ¥16,000 | +12.5% |
| 广告 ROAS | 2.35x | 2.10x | +11.9% |
| 新增线索 | 470 | 450 | +4.4% |
| 成交订单 | 35 | 32 | +9.4% |
| 成交金额 | ¥580,000 | ¥520,000 | +11.5% |

## 核心洞察

- 🚀 **流量增长势头良好**: PV 环比增长 10%，转化率同步提升 0.3%，说明优化措施有效
- 📈 **广告投资回报率提升**: ROAS 从 2.10x 增至 2.35x，单位成本下降 8%
- 📞 **销售漏斗健康**: 线索转化率 38.3%，环比提升 2.1 个百分点
- 💰 **收入突破历史高位**: 周收入破 58 万，再创新高

## 发现的异常

- ⚠️ 周三 (5月1日) 流量异常低，分析原因为国际劳动节活动周期

## 改进建议

1. **加强搜索引擎优化**: 目前自然流量占比 35%，建议增加 SEO 投入，目标提升至 45%
2. **优化广告投放**: Facebook 广告 ROAS 为 2.5x，Google Ads 为 2.1x，建议加大 Facebook 预算占比
3. **完善客户跟进流程**: 线索库中有 185 个待跟进线索，建议 24 小时内完成首次接触
4. **扩大高客单价产品推广**: 企业版客户 LTV 是个人版的 4.2 倍，建议增加企业版权重

---
*报告生成时间: 2024-05-03 09:15:32*
*数据源: Google Analytics 4, Facebook Ads, Salesforce CRM*
*模型: Claude Opus 4.6*
```

## 集成到 Slack

### 1. 创建 Slack Webhook

```
1. 打开 https://api.slack.com/apps
2. Create New App → From scratch
3. 输入应用名称和 workspace
4. 左侧菜单 → Incoming Webhooks → 激活
5. Add New Webhook to Workspace
6. 选择想要接收报告的 Channel
7. 复制 Webhook URL
```

### 2. 配置到 .env

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. 自动推送

```bash
python scheduler.py
```

每周一 09:00 会自动在 Slack 发送周报。

## 定制化开发

### 修改报告格式

编辑 `weekly_report_agent.py` 中的 `generate_markdown_report` 函数：

```python
def execute_tool(tool_name: str, tool_input: dict) -> str:
    # ...
    elif tool_name == "generate_markdown_report":
        report = f"""# 我的自定义报告格式
        
## 关键数据
...
"""
```

### 增加新的数据源

在 `DataSourceManager` 类中添加新方法：

```python
@staticmethod
def fetch_my_custom_data(week_num: int) -> dict:
    """获取自定义数据"""
    return {
        "source": "My Data Source",
        "data": {...}
    }
```

然后在 `define_tools()` 中添加对应工具：

```python
{
    "name": "fetch_custom",
    "description": "从我的数据源获取数据",
    "input_schema": {...}
}
```

### 修改 Agent 行为

编辑 `system_prompt` 变量，调整分析策略：

```python
system_prompt = """你是周报分析专家。
你的目标是：
1. 关注与业务目标相关的指标
2. 提出可以在一周内实施的建议
3. 使用数据驱动的论证
"""
```

## 性能优化

### Token 消耗优化

```python
# 减少数据量
# 改为：只返回必要的字段
return {
    "pv": 55000,
    "conversion_rate": 0.035,
    # 不需要返回所有字段
}

# 优化 Prompt
# 使用更简洁的 system prompt，减少前置 token 消耗
```

### 加速执行

```python
# 并行获取数据（如果改用 async）
import asyncio

async def fetch_all_data():
    results = await asyncio.gather(
        fetch_analytics(),
        fetch_ads(),
        fetch_crm()
    )
    return results
```

## 故障排查

### 问题：API Key 无效

```
Error: Invalid API key
```

**解决方案：**
```bash
# 确认 .env 文件存在
ls -la .env

# 确认 API key 格式正确
cat .env | grep ANTHROPIC

# 从 https://console.anthropic.com 重新获取
```

### 问题：超时

```
Error: Request timeout after 30s
```

**解决方案：**
- 减少 system_prompt 长度
- 简化数据返回格式
- 增加 timeout 值

### 问题：工具循环过多

```
Warning: Reached max iterations (10)
```

**解决方案：**
```python
# 在 system_prompt 中明确步骤
system_prompt = """
步骤 1: 调用 fetch_analytics, fetch_ads, fetch_crm (共 3 个工具)
步骤 2: 调用 analyze_data (1 个工具)
步骤 3: 调用 generate_markdown_report (1 个工具)
总共 5 个工具调用，不能超过。
"""
```

## 常见问题

**Q: 数据是模拟的吗？**  
A: 是的，演示代码使用模拟数据。生产环境需要集成真实 API（见 `advanced_data_sources.py`）

**Q: 支持其他编程语言吗？**  
A: Claude API 支持任何语言。可以用 Node.js、Java、Go 等重新实现。

**Q: 能处理多个业务线吗？**  
A: 可以。传入 `business_line` 参数，过滤对应数据：
```python
run_weekly_report_agent(business_line="sales")
```

**Q: 如何自定义分析逻辑？**  
A: 修改 `system_prompt` 或在 `analyze_data` 工具中加入自定义逻辑。

**Q: 能实时监控而不是周报吗？**  
A: 可以。改 scheduler 为每小时运行一次：
```python
schedule.every().hour.at(":00").do(job_callback)
```

## 下一步

1. **配置真实数据源** → `advanced_data_sources.py`
2. **启动定时任务** → `python scheduler.py`
3. **集成 Slack** → 配置 `SLACK_WEBHOOK_URL`
4. **Docker 部署** → `docker-compose up -d`
5. **监控和告警** → 添加 logging 和错误处理

## 相关资源

- [Anthropic 文档](https://docs.anthropic.com)
- [Claude API 参考](https://docs.anthropic.com/en/api/messages)
- [Agent 最佳实践](https://docs.anthropic.com/en/docs/build-with-claude/agents)

---

**需要帮助？** 查看 `README.md` 获取详细文档。
