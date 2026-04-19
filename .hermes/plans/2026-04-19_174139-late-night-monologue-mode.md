# 深夜独白模式 — 实现计划

> 创建时间：2026-04-19 17:41

## 目标

为窄门平台实现"深夜独白模式"功能，让用户在深夜（22:00-05:00）可以进入一个沉浸式的写作空间，与自己的灵魂对话，记录内心最真实的想法。

## 设计理念

深夜是人最脆弱、最真实的时刻。独白模式提供：
- **氛围感**：暗色调、星夜背景、轻柔动效
- **引导性**：AI生成灵魂提问，引导深度反思
- **私密性**：只属于用户自己的空间，不对外分享
- **仪式感**：每次独白都是一次与自己的约定

## 实现方案

### 1. 数据库扩展 (`src/core/database.py`)

新增 `monologues` 表：
```sql
CREATE TABLE IF NOT EXISTS monologues (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    prompt TEXT,           -- AI生成的引导问题
    content TEXT,          -- 用户的独白内容
    mood TEXT,             -- 情绪标签（忧郁/平静/愤怒/释然...）
    word_count INTEGER DEFAULT 0,
    created_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

新增方法：
- `create_monologue(user_id, prompt)` — 创建独白记录
- `save_monologue(monologue_id, content, mood)` — 保存独白
- `get_monologues(user_id, limit=10)` — 获取独白历史
- `get_monologue_stats(user_id)` — 统计数据

### 2. 后端API (`src/api/main.py`)

新增端点：
- `POST /api/monologue/start` — 开始独白（AI生成引导问题）
- `POST /api/monologue/save` — 保存独白内容
- `GET /api/monologue/history/{user_id}` — 获取独白历史
- `GET /api/monologue/stats/{user_id}` — 获取独白统计

### 3. AI引导模块 (`src/core/monologue_prompts.py`)

预设灵魂引导问题库（按主题分类）：
- 存在与意义
- 恐惧与渴望
- 关系与孤独
- 过去与未来
- 真实与伪装

可选：调用MIMO API生成个性化引导

### 4. 前端界面 (`src/ui/index.html`)

#### UI设计
- 入口：导航栏"🌙 独白"按钮
- 全屏沉浸模式（遮罩层）
- 星夜粒子背景动画
- 居中写作区域（半透明卡片）
- 引导问题显示在顶部
- 字数统计和时间显示
- 情绪标签选择（保存时）
- 优雅的退出动画

#### CSS样式
```css
.monologue-overlay {
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse at center, #0a0a15 0%, #050508 100%);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.monologue-card {
    background: rgba(12, 12, 18, 0.85);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(184, 148, 46, 0.15);
    max-width: 700px;
    width: 90%;
}

.monologue-textarea {
    background: transparent;
    border: none;
    color: var(--text);
    font-family: 'Noto Serif SC', serif;
    font-size: 1.1rem;
    line-height: 2;
    resize: none;
}
```

#### JavaScript函数
- `openMonologue()` — 打开独白模式
- `startMonologue()` — 获取AI引导问题
- `saveMonologue()` — 保存独白
- `closeMonologue()` — 关闭独白模式
- `updateWordCount()` — 实时字数统计
- `createStars()` — 星夜粒子效果

### 5. 情绪标签系统

6种情绪状态：
- 🌑 忧郁
- 🌊 平静
- 🔥 愤怒
- 💧 释然
- 🌪️ 迷茫
- ✨ 希望

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/core/database.py` | 修改 | 新增 monologues 表和方法 |
| `src/api/main.py` | 修改 | 新增4个API端点 |
| `src/core/monologue_prompts.py` | 新建 | 灵魂引导问题库 |
| `src/ui/index.html` | 修改 | 新增独白模式UI和JS |

## 实现步骤

1. 创建 `monologue_prompts.py` 引导问题库
2. 扩展 `database.py` 添加 monologues 表
3. 在 `main.py` 添加4个API端点
4. 在 `index.html` 添加独白模式前端
5. 测试后端API
6. 测试前端交互
7. 提交代码并部署

## 验证标准

- [ ] 独白模式可以正常打开和关闭
- [ ] AI引导问题可以正常获取
- [ ] 用户输入内容后可以保存
- [ ] 历史记录可以查看
- [ ] 字数统计实时更新
- [ ] 情绪标签可以选择
- [ ] 星夜背景动画正常显示
- [ ] 移动端适配良好

## 风险与注意事项

- 深夜模式仅在22:00-05:00开放，其他时间显示提示
- 独白内容高度私密，不参与任何分享功能
- 字数上限建议5000字，防止过长
- 星夜动画需要性能优化，低端设备可能卡顿
