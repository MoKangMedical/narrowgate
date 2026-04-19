# 窄门 NarrowGate — Hermes Agent 接手文档

> 更新时间：2026-04-19 17:00 GMT+8
> 当前状态：v2.3 高级感视觉升级完成

---

## 一、项目概述

窄门是一个**灵魂成长训练平台**。帮助人看见自己的枷锁，穿越窄门，从凡人进化到封神。

**技术栈：**
- 后端：Python + FastAPI（端口8090）
- 前端：单文件HTML + TailwindCSS + 纯JS（无框架）
- 数据库：SQLite
- AI：MIMO API（小米大模型，无限额度）
- 域名：narrowgatemind.top（HTTPS，nginx反向代理）
- GitHub：https://github.com/MoKangMedical/narrowgate

---

## 二、文件结构

```
/root/narrowgate/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI后端（900+行，所有API端点）
│   ├── core/
│   │   ├── __init__.py
│   │   ├── soul_audit.py        # 灵魂审计引擎（476行，6维度）
│   │   ├── masters.py           # 7位大师引导者
│   │   ├── crossing.py          # 穿越训练引擎（含四周结构+每日挑战）
│   │   ├── gate_finder.py       # 窄门发现器
│   │   ├── evolution.py         # 五层进化金字塔
│   │   ├── witness.py           # 见证人网络
│   │   ├── database.py          # SQLite数据库
│   │   ├── mimo_client.py       # MIMO AI客户端
│   │   └── mimo_challenges.py   # AI挑战生成
│   └── ui/
│       └── index.html           # 前端唯一文件（982行）
├── data/
│   └── narrowgate.db            # SQLite数据库
├── docs/
│   ├── KNOWLEDGE_BASE.md        # 知识库（含与神对话CWG体系）
│   ├── THEORY.md                # 理论体系（含7.4灵性根基）
│   └── HANDOFF.md               # ← 你正在读的文件
├── scripts/
│   └── update_frontend.py       # 前端更新脚本
├── requirements.txt
└── README.md
```

---

## 三、API端点清单（29个）

### 用户
- `POST /api/user/register` — 注册
- `GET /api/user/{user_id}` — 获取用户

### 灵魂审计（核心交互）
- `POST /api/audit/start` — 开始审计
- `POST /api/audit/answer` — 提交回答（支持master_id参数指定大师）
- `POST /api/audit/complete` — 完成审计
- `GET /api/audit/{audit_id}` — 获取审计详情
- `GET /api/audit/{audit_id}/gates` — 获取发现的窄门

### 大师引导者
- `GET /api/masters` — 大师列表
- `GET /api/masters/{master_id}` — 大师详情
- `POST /api/masters/choose` — 选择大师

### 穿越训练
- `POST /api/crossing/start` — 开始穿越
- `POST /api/crossing/complete` — 完成穿越
- `GET /api/crossing/{crossing_id}` — 穿越详情

### 30天训练计划
- `GET /api/training/plan` — 完整30天计划
- `GET /api/training/week/{day}` — 根据天数返回当前周
- `GET /api/training/challenge/{gate_id}/day/{day}` — 每日挑战

### 见证人
- `POST /api/witness/add` — 添加见证人
- `GET /api/witness/list` — 见证人列表
- `POST /api/witness/verify` — 验证
- `GET /api/witness/report/{crossing_id}` — 见证报告

### 进化系统
- `GET /api/evolution/{user_id}` — 进化状态
- `GET /api/evolution/{user_id}/pyramid` — 金字塔
- `POST /api/evolution/breakthrough` — 突破记录
- `POST /api/evolution/crossing-complete` — 穿越完成+经验值

### 系统
- `GET /health` — 健康检查
- `GET /api/stats` — 统计数据

---

## 四、7位大师数据

```javascript
const MASTERS = [
    {id:'socrates', name:'苏格拉底', title:'追问者', avatar:'🦉', dimension:'认知', color:'#6366f1', level_required:1},
    {id:'jung', name:'荣格', title:'阴影猎手', avatar:'🌑', dimension:'情绪', color:'#7c3aed', level_required:1},
    {id:'memento', name:'清醒者', title:'执行官', avatar:'⚡', dimension:'行为', color:'#dc2626', level_required:1},
    {id:'mirror', name:'镜像者', title:'关系分析师', avatar:'🪞', dimension:'关系', color:'#059669', level_required:1},
    {id:'architect', name:'架构师', title:'系统思维者', avatar:'🏗️', dimension:'事业', color:'#b8942e', level_required:2},
    {id:'alchemist', name:'炼金术士', title:'变形者', avatar:'🔮', dimension:'认知', color:'#7c3aed', level_required:3},
    {id:'gatekeeper', name:'守门人', title:'窄门本身', avatar:'🚪', dimension:'全部', color:'#b8942e', level_required:4},
]
```

每位大师有完整的 greeting、signature_phrases、specialties 数组（见 index.html 底部 script 段）。

---

## 五、灵魂审计6维度

| 维度 | key | 描述 |
|------|-----|------|
| 认知 | 认知 | 你的信念、思维模式、自我认知 |
| 情绪 | 情绪 | 你的情绪反应、恐惧、压抑 |
| 行为 | 行为 | 你的习惯、拖延、执行力 |
| 关系 | 关系 | 你的人际关系模式 |
| 事业 | 事业 | 你的职业选择、目标系统 |
| 幻觉 | 幻觉 | 你活在哪些人类幻觉中（源自CWG十大幻觉） |

---

## 六、30天训练计划（四周结构）

| 周 | 天数 | 名称 | 难度 | 焦点 |
|---|------|------|------|------|
| 1 | D1-D7 | 面对恐惧 | 3-5 | 建立行动感，突破表层回避 |
| 2 | D8-D14 | 建立节奏 | 5-7 | 建立每日穿越的稳定节奏 |
| 3 | D15-D21 | 突破瓶颈 | 7-8 | 突破核心恐惧，旧模式松动 |
| 4 | D22-D30 | 巩固穿越 | 8+ | 整合新身份，从玩家变导师 |

### 📝 待完成：30天课程详细内容
需要创建文件 `src/core/course_content.py`，包含30天每天的：
- 标题、主题、教学内容（300-500字）
- 具体挑战行动
- 反思问题+引导
- 金句、难度、推荐大师
- 经验值奖励

5级跨越规划：
- D1-D6：回归凡人（认知+情绪）
- D7-D12：学会看见（行为+关系）
- D13-D18：开始穿越（事业+幻觉）
- D19-D24：觉醒之路（身份转变）
- D25-D30：封神仪式（整合与传承）

---

## 七、前端CSS设计体系

### 色彩
```css
--bg: #050508;           /* 深黑底色 */
--bg-card: #0c0c12;      /* 卡片底色 */
--gold: #b8942e;         /* 沉稳金 */
--gold-light: #d4af37;   /* 亮金 */
--gold-glow: rgba(180,148,46,0.15);
--text: #e8e4dc;         /* 暖白文字 */
--text-dim: #6b6860;     /* 暗文字 */
--border: rgba(255,255,255,0.04);
```

### 关键CSS类
- `.text-gold` — 金色渐变文字（webkit-clip-text）
- `.glass` — 玻璃态卡片（hover微光+上浮2px）
- `.btn-gold` — 渐变金按钮（发光阴影）
- `.divider-gold` — 金色分割线
- `.reveal` / `.reveal.visible` — 滚动渐入动画
- `.gate-visual` — 窄门/宽门可视化

### 字体
- Google Fonts（loli.net镜像）：Noto Serif SC（400,700,900）+ Inter（300-700）
- 系统兜底：PingFang SC, Microsoft YaHei

### 动画
- IntersectionObserver 驱动的 `.reveal` 滚动渐入
- `gateGlow` 窄门呼吸发光（4s循环）
- `slideUp` 对话气泡入场
- `bounce` 打字指示器

---

## 八、部署工作流

**每次修改代码后必须执行：**
```bash
cd /root/narrowgate
# 1. 推主分支
git add -A && git commit -m "描述" && git push origin main

# 2. 更新GitHub Pages备份
cp src/ui/index.html index.html
git add index.html && git commit -m "pages: 更新" && git push origin gh-pages

# 3. 前端由nginx直接提供，修改 src/ui/index.html 即刻生效
# 后端修改需重启：
pkill -f "uvicorn main:app" 2>/dev/null
cd src/api && nohup python3 -m uvicorn main:app --host 127.0.0.1 --port 8090 &
```

**nginx配置：**
- `/root/narrowgate/src/ui/` 直接提供静态文件
- API 请求代理到 127.0.0.1:8090
- SSL证书：Let's Encrypt（自动续期）

---

## 九、当前待完成任务

### 🔴 P0：首页打磨（进行中）
用户要求按国际品牌10分标准逐页打磨。当前首页（index.html）已做v2.3高级感升级，但还需进一步精进。

### 🔴 P0：30天课程详细内容
创建 `src/core/course_content.py`，30天每天完整内容（教学+挑战+反思）。

### 🟡 P1：后端课程API增强
- 新增 `/api/course/day/{day}` — 返回单天课程详情
- 新增 `/api/course/progress/{user_id}` — 用户课程进度
- 新增 `/api/course/complete` — 标记某天完成

### 🟡 P1：前端课程交互界面
- 沉浸式课程阅读体验
- 每日课程卡片
- 进度追踪可视化
- 学习日记/反思录入

### 🟢 P2：其他页面打磨
- 灵魂审计对话页面
- 大师引导者页面
- 30天穿越训练页面
- 见证人网络页面
- 进化金字塔页面

---

## 十、理论背景

### 核心哲学
> "你要进窄门。因为引到灭亡，那门是宽的，路是大的，进去的人也多；引到生命，那门是窄的，路是小的，找着的人也少。" — 马太福音 7:13-14

### 五层进化架构
凡人（L1）→ 看见（L2）→ 穿越（L3）→ 觉醒（L4）→ 封神（L5）

### 理论根基
- 哲学：苏格拉底、斯多葛学派、尼采、禅宗、道家
- 心理学：荣格个体化、CBT苏格拉底式提问、跨理论模型、Frankl意义治疗
- 行为科学：Taleb反脆弱、原子习惯、Brené Brown脆弱
- 灵性：Neale Donald Walsch《与神对话》（CWG）— 十大幻觉、三觉知层级、Be-Do-Have范式

详细理论文档：
- `/root/narrowgate/docs/THEORY.md`
- `/root/narrowgate/docs/KNOWLEDGE_BASE.md`

---

## 十一、关键JavaScript函数清单（必须保留）

所有前端交互逻辑在 index.html 底部 `<script>` 中：

```javascript
// 审计系统
startAudit()           // 开始灵魂审计
submitAnswer()         // 提交回答
completeAudit()        // 完成审计，显示结果
resetAudit()           // 重置审计

// 消息系统
addMessage(role, text, subtext)    // 添加对话消息
addEvasionAlert(type, analysis)    // 添加回避检测警告

// 大师系统
renderMasters()        // 渲染大师卡片
openMaster(id)         // 打开大师对话弹窗
closeMasterModal()     // 关闭弹窗
startMasterChat(id)    // 开始大师对话
sendToMaster(id)       // 发送消息给大师

// 见证人
addWitness()           // 添加见证人
loadWitnesses()        // 加载见证人列表

// 进化系统
loadEvolution()        // 加载进化状态

// 通用
apiCall(url, method, body)  // API调用封装
```

MASTERS 常量数组包含7位大师的完整数据（greeting、signature_phrases、specialties）。

---

## 十二、设计参考方向

目标风格：**国际品牌级** — 参考 Apple、Aesop、Headspace、Calm

核心原则：
- 克制 > 丰富（少即是多）
- 大量留白
- 精确的字体层级
- 微动效（不是炫技）
- 温暖但不幼稚
- 哲学感但不故弄玄虚
