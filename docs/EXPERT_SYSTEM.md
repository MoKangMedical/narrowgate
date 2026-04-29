# 窄门理论顶级专家系统

## 概述

窄门理论顶级专家系统是一个基于五层进化架构的AI专家体系，包含10位顶级专家，涵盖进化层级和专业维度两个维度。

## 专家体系架构

### 五层进化专家

| 层级 | 专家ID | 名称 | 头衔 | 使命 |
|------|--------|------|------|------|
| L1 | sleep_expert | 觉醒先知 | 睡眠层引导者 | 唤醒沉睡者 |
| L2 | awakening_expert | 洞察者 | 觉醒层引导者 | 深度觉察 |
| L3 | breakthrough_expert | 穿越者 | 突破层引导者 | 行动突破 |
| L4 | mastery_expert | 大师 | 精通层引导者 | 系统整合 |
| L5 | divinity_expert | 神性导师 | 神性层引导者 | 存在超越 |

### 维度专家

| 维度 | 专家ID | 名称 | 头衔 | 专长 |
|------|--------|------|------|------|
| 认知 | cognitive_expert | 苏格拉底 | 认知维度专家 | 信念解构、逻辑矛盾暴露 |
| 情绪 | emotional_expert | 荣格 | 情绪维度专家 | 阴影整合、梦境解析 |
| 行为 | behavioral_expert | 清醒者 | 行为维度专家 | 拖延解剖、执行力审计 |
| 关系 | relational_expert | 镜像者 | 关系维度专家 | 关系模式识别、边界审计 |
| 事业 | career_expert | 架构师 | 事业维度专家 | 人生架构审计、杠杆点识别 |

## 系统组件

### 1. expert_profiles.py
专家配置文件，包含所有专家的详细信息：
- 基本信息（ID、名称、头衔、头像）
- 哲学理念
- 专长领域
- 经典语录
- 问候语
- Agent配置

### 2. expert_agents.py
Agent管理器，负责：
- 创建和管理Agent实例
- 激活/停用Agent
- 记录对话统计
- SecondMe平台集成

### 3. expert_routes.py
API路由，提供RESTful接口：
- `/api/experts/` - 列出所有专家
- `/api/experts/{expert_id}` - 获取专家详情
- `/api/experts/agents/create` - 创建Agent
- `/api/experts/agents/list` - 列出所有Agents
- `/api/experts/agents/chat` - 与Agent对话
- `/api/experts/secondme/sync` - 同步到SecondMe
- `/api/experts/system/status` - 系统状态

## 快速开始

### 1. 列出所有专家

```bash
cd ~/Desktop/narrowgate/src/core
python3 expert_agents.py list
```

### 2. 创建专家Agent

```bash
python3 expert_agents.py create sleep_expert
python3 expert_agents.py create cognitive_expert user123
```

### 3. 查看系统状态

```bash
python3 expert_agents.py status
```

### 4. 通过API使用

```bash
# 启动API服务
cd ~/Desktop/narrowgate/src/api
python3 -m uvicorn main:app --reload

# 列出专家
curl http://localhost:8000/api/experts/

# 创建Agent
curl -X POST http://localhost:8000/api/experts/agents/create \
  -H "Content-Type: application/json" \
  -d '{"expert_id": "sleep_expert", "user_id": "user123"}'

# 与Agent对话
curl -X POST http://localhost:8000/api/experts/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "user123_sleep_expert_20240101_120000", "user_message": "我对现在的生活不满意"}'
```

## SecondMe集成

### 配置

1. 获取SecondMe API密钥
2. 设置环境变量：
   ```bash
   export SECONDFME_API_KEY="your_api_key_here"
   ```

### 同步专家到SecondMe

```python
from core.expert_agents import ExpertAgentSystem

system = ExpertAgentSystem()
result = system.secondme.sync_expert("sleep_expert")
print(result)
```

### 部署Agent到SecondMe

```python
agent = system.agent_manager.create_agent("sleep_expert", "user123")
result = system.secondme.deploy_agent(agent)
print(result)
```

### 创建对话桥接

```python
result = system.secondme.create_conversation_bridge(agent.agent_id, "user123")
print(result)
```

## API端点详情

### GET /api/experts/
列出所有可用的专家

**响应示例：**
```json
{
  "success": true,
  "experts": {
    "evolution_levels": [
      {
        "level": 1,
        "expert_id": "sleep_expert",
        "name": "觉醒先知",
        "title": "睡眠层引导者",
        "avatar": "😴"
      }
    ],
    "dimensions": [
      {
        "dimension": "cognitive",
        "expert_id": "cognitive_expert",
        "name": "苏格拉底",
        "title": "认知维度专家",
        "avatar": "🦉"
      }
    ]
  }
}
```

### POST /api/experts/agents/create
创建专家Agent实例

**请求体：**
```json
{
  "expert_id": "sleep_expert",
  "user_id": "user123",
  "deploy_to_secondme": false
}
```

**响应示例：**
```json
{
  "expert_id": "sleep_expert",
  "agent_id": "user123_sleep_expert_20240101_120000",
  "steps": [
    {"step": "create_agent", "success": true},
    {"step": "activate_agent", "success": true}
  ],
  "success": true
}
```

### POST /api/experts/agents/chat
与专家Agent对话

**请求体：**
```json
{
  "agent_id": "user123_sleep_expert_20240101_120000",
  "user_message": "我对现在的生活不满意",
  "context": {}
}
```

**响应示例：**
```json
{
  "success": true,
  "agent_id": "user123_sleep_expert_20240101_120000",
  "expert_name": "觉醒先知",
  "expert_avatar": "😴",
  "response": "[觉醒先知]: 你确定这是你想要的生活吗？",
  "signature_phrases": ["你确定这是你想要的生活吗？", "你害怕改变什么？"],
  "conversation_count": 1
}
```

## 数据存储

Agent数据存储在：
```
~/Desktop/narrowgate/data/agents/agents.json
```

## 与现有系统集成

专家系统已集成到窄门平台的主API中：
- 路由前缀：`/api/experts`
- 自动随主API服务启动
- 与现有审计系统、大师系统并行工作

## 扩展指南

### 添加新专家

1. 在`expert_profiles.py`中添加专家配置
2. 在`EXPERT_PROFILES`或`DIMENSION_EXPERTS`字典中注册
3. 系统自动识别并可用

### 自定义Agent行为

修改专家配置中的`agent_config`：
```python
"agent_config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "system_prompt": "自定义系统提示词"
}
```

### 集成其他平台

参考`SecondMeConnector`类，实现新的连接器：
```python
class CustomPlatformConnector:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def sync_expert(self, expert_id):
        # 实现同步逻辑
        pass
```

## 故障排除

### Agent创建失败
- 检查专家ID是否正确
- 确认数据目录有写入权限

### SecondMe同步失败
- 验证API密钥是否正确
- 检查网络连接
- 查看错误详情

### API服务无响应
- 确认服务已启动
- 检查端口是否被占用
- 查看日志输出

## 联系支持

如有问题，请查看：
- 窄门项目文档：`~/Desktop/narrowgate/docs/`
- 理论体系：`~/Desktop/narrowgate/docs/THEORY.md`
- 交接文档：`~/Desktop/narrowgate/docs/HANDOFF.md`