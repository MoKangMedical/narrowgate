# 🚪 窄门 NarrowGate

> **"引到永生，那门是窄的，路是小的，找着的人也少。"**

让人看见窄门并跨越窄门的进化平台。不是又一个冥想App或目标管理工具——是灵魂的鉴别诊断引擎。

## 🔑 核心哲学

**你不是不知道该做什么。你是不想做你知道该做的事。**

窄门是一个AI驱动的灵魂进化平台：
1. **灵魂审计** — 苏格拉底式追问，识别你的枷锁
2. **大师引导** — 7位大师各有性格，陪你穿越
3. **穿越训练** — 30天每日挑战，做你最不想做的事
4. **见证人网络** — 让真实的人见证你的进化
5. **进化金字塔** — 从睡眠层到神性层的可视化路径

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│           前端 (HTML + Tailwind)          │
│     灵魂审计 / 大师对话 / 穿越训练        │
├─────────────────────────────────────────┤
│          FastAPI 后端 (Python)           │
│  灵魂审计引擎 | 穿越引擎 | 大师引擎       │
├─────────────────────────────────────────┤
│            MIMO AI (小米大模型)           │
│    苏格拉底/荣格/清醒者/镜像者/...        │
├─────────────────────────────────────────┤
│          SQLite 数据库                    │
│  用户 | 审计 | 穿越 | 见证 | 神性档案     │
└─────────────────────────────────────────┘
```

### 核心引擎

| 引擎 | 文件 | 功能 |
|------|------|------|
| 灵魂审计 | `core/soul_audit.py` | 5维度（认知/情绪/行为/关系/使命）逐层追问 |
| 窄门识别 | `core/gate_finder.py` | 根据枷锁生成窄门优先级 |
| 穿越训练 | `core/crossing.py` | 30天每日挑战系统 |
| 大师引导 | `core/masters.py` | 7位大师各有性格和追问风格 |
| 见证人网络 | `core/witness.py` | 真实人类见证你的进化 |
| 进化金字塔 | `core/evolution.py` | 五层进化模型+经验值 |
| MIMO客户端 | `core/mimo_client.py` | 小米MIMO API集成 |
| 数据持久化 | `core/database.py` | SQLite存储 |

## 🧙 7位大师引导者

| 大师 | 身份 | 维度 | 风格 |
|------|------|------|------|
| 🦉 苏格拉底 | 追问者 | 认知 | 逻辑矛盾暴露 |
| 🌑 荣格 | 阴影猎手 | 情绪 | 阴影整合 |
| ⚡ 清醒者 | 执行官 | 行为 | 拖延解剖 |
| 🪞 镜像者 | 关系分析师 | 关系 | 关系模式识别 |
| 🏗️ 架构师 | 系统思维者 | 事业 | 人生架构审计 (L2+) |
| 🔮 炼金术士 | 变形者 | 认知 | 痛苦转化 (L3+) |
| 🚪 守门人 | 窄门本身 | 全部 | 穿越验证 (L4+) |

每位大师通过MIMO API实时生成追问，不再是模板回复。

## 🔺 进化金字塔

```
          ✨  第5层：神性层
        ┌───┐
        │ 4 │  第4层：精通层
      ┌─┴───┴─┐
      │   3   │  第3层：突破层
    ┌─┴───────┴─┐
    │     2     │  第2层：觉醒层
  ┌─┴───────────┴─┐
  │       1       │  第1层：睡眠层
┌─┴───────────────┴─┐
└───────────────────┘
```

**经验值规则**：
- 每日挑战完成：+10
- 突破记录：+50
- 穿越完成：+200

## 🚀 快速开始

### 本地部署

```bash
# 克隆仓库
git clone https://github.com/MoKangMedical/narrowgate.git
cd narrowgate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python src/api/main.py
```

访问 http://localhost:8090

### 生产部署

```bash
# 创建systemd服务
sudo tee /etc/systemd/system/narrowgate.service << 'EOF'
[Unit]
Description=NarrowGate
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/narrowgate/src/api
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 127.0.0.1 --port 8090
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动
sudo systemctl enable narrowgate
sudo systemctl start narrowgate
```

## 📡 API 文档

### 核心端点

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/audit/start` | 开始灵魂审计 |
| POST | `/api/audit/answer` | 提交审计回答 |
| POST | `/api/audit/complete` | 完成审计 |
| GET | `/api/audit/{id}/gates` | 获取窄门候选 |
| GET | `/api/masters` | 获取大师列表 |
| POST | `/api/masters/choose` | 选择大师 |
| POST | `/api/crossing/start` | 开始穿越 |
| POST | `/api/crossing/complete` | 完成挑战 |
| POST | `/api/witness/add` | 添加见证人 |
| GET | `/api/witness/list` | 见证人列表 |
| GET | `/api/evolution/{user_id}` | 进化状态 |
| POST | `/api/evolution/breakthrough` | 记录突破 |

### 示例

```bash
# 开始灵魂审计
curl -X POST http://localhost:8090/api/audit/start \
  -H "Content-Type: application/json" \
  -d '{"username": "小林"}'

# 提交回答（带MIMO AI追问）
curl -X POST http://localhost:8090/api/audit/answer \
  -H "Content-Type: application/json" \
  -d '{
    "audit_id": "audit_xxx",
    "answer": "我最大的成就是完成了医学博士学业",
    "master_id": "socrates"
  }'

# 响应
{
  "evasion_detected": false,
  "ai_reply": "你说'最大'，但医学博士之后，你难道不会追求更高的成就吗？",
  "dimension": "认知",
  "depth": 2
}
```

## 🧪 灵魂审计原理

### 五维度模型

| 维度 | 探索内容 | 核心问题 |
|------|----------|----------|
| 认知 | 信念、思维模式 | 你相信什么是真的？ |
| 情绪 | 情感、压抑、恐惧 | 你在感受什么？ |
| 行为 | 习惯、执行、拖延 | 你在做什么？ |
| 关系 | 人际、边界、讨好 | 你在关系中是谁？ |
| 使命 | 意义、方向、价值 | 你为什么存在？ |

### 回避检测

系统实时检测四种回避模式：
- **否认** — "没有"、"不是"、"还好"
- **转移** — "说起来"、"对了"、"另外"
- **最小化** — "一点点"、"稍微"、"可能有一点"
- **合理化** — "因为"、"没办法"、"大家都这样"

## 📦 依赖

- Python 3.12+
- FastAPI
- Uvicorn
- httpx
- SQLite3

## 📄 许可证

本项目为莫康医生(MoKangMedical)专有项目。

## 🙏 致谢

- 小米MIMO团队 — 提供AI对话能力
- 苏格拉底 — 未经审视的人生不值得过

---

*"不是不知道，是不想做。窄门在等你。"* 🚪
