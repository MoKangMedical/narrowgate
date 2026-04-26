# 窄门个人评测和验证系统设计

> **"没有测量，就没有改进。"**
> 本文档设计窄门平台的个人评测和验证系统，帮助用户量化成长、验证穿越。

---

## 一、评测系统概述

### 1.1 评测目标

1. **自我认知** — 帮助用户了解自己的当前状态
2. **成长追踪** — 量化用户的进步和变化
3. **动机维持** — 通过可视化进度保持动力
4. **验证穿越** — 客观证明用户确实发生了改变

### 1.2 评测维度

```
┌─────────────────────────────────────────┐
│           窄门评测系统                   │
├─────────────────────────────────────────┤
│  基础评测                               │
│  ├─ 灵魂审计（5维度）                   │
│  ├─ 窄门发现（优先级排序）              │
│  └─ 进化层级（当前状态）                │
├─────────────────────────────────────────┤
│  过程评测                               │
│  ├─ 每日挑战完成度                      │
│  ├─ 对话深度分析                        │
│  └─ 回避模式检测                        │
├─────────────────────────────────────────┤
│  结果评测                               │
│  ├─ 穿越验证                            │
│  ├─ 行为改变                            │
│  └─ 身份转变                            │
└─────────────────────────────────────────┘
```

---

## 二、基础评测系统

### 2.1 灵魂审计评测

#### 评测结构

```python
class SoulAuditAssessment:
    """灵魂审计评测"""
    id: str
    user_id: str
    timestamp: str
    
    # 5维度得分（0-100）
    cognitive_score: float      # 认知维度
    emotional_score: float      # 情绪维度
    behavioral_score: float     # 行为维度
    relational_score: float     # 关系维度
    career_score: float         # 事业维度
    
    # 综合分析
    overall_score: float        # 综合得分
    strengths: List[str]        # 优势维度
    blind_spots: List[str]      # 盲点维度
    shackle_patterns: List[Dict] # 枷锁模式
    
    # 回避分析
    evasion_types: Dict[str, int]  # 回避类型统计
    evasion_severity: float        # 回避严重度
    
    # 建议
    recommended_masters: List[str]  # 推荐大师
    recommended_gates: List[str]    # 推荐窄门
```

#### 评测题目示例

**认知维度（10题）**
1. 你最近一次改变一个重要观点是什么时候？
2. 你有没有一个你一直不愿意质疑的信念？
3. 当别人不同意你的观点时，你的第一反应是什么？
4. 你有没有发现自己在某些事情上自相矛盾？
5. 你如何判断一个信息是否可信？

**情绪维度（10题）**
1. 你上一次哭是什么时候？为什么？
2. 你有没有一直压抑着某种情绪？
3. 什么事情会让你感到愤怒？
4. 你害怕什么？
5. 你有没有因为害怕某种情绪而逃避某件事？

**行为维度（10题）**
1. 你今天做了什么让你感到骄傲的事？
2. 你有没有一直拖延的事情？
3. 你上一次走出舒适区是什么时候？
4. 你的日常习惯中，有哪些你知道不好但还在做的？
5. 你有没有因为害怕失败而没有开始的事情？

**关系维度（10题）**
1. 你最亲近的人，你觉得他们真正了解你吗？
2. 你有没有维持着一段让你不舒服但不敢结束的关系？
3. 你帮过别人最大的忙是什么？你为什么帮？
4. 你有没有因为害怕被拒绝而没有表达的感受？
5. 你在关系中通常扮演什么角色？

**事业维度（10题）**
1. 如果没有任何限制，你真正想做什么？
2. 你觉得自己现在配得上自己想要的位置吗？
3. 你有没有在用"还没准备好"来逃避一个你其实可以开始的事情？
4. 你对成功的定义是什么？
5. 你有没有在追求一个不是你真正想要的目标？

#### 评分算法

```python
def calculate_dimension_score(answers: List[str], dimension: str) -> float:
    """计算维度得分"""
    base_score = 50  # 基础分
    
    # 深度分析
    depth_score = analyze_answer_depth(answers)
    
    # 真实性分析
    authenticity_score = analyze_authenticity(answers)
    
    # 回避检测
    evasion_penalty = detect_evasion(answers)
    
    # 计算最终得分
    final_score = base_score + depth_score + authenticity_score - evasion_penalty
    
    return max(0, min(100, final_score))

def analyze_answer_depth(answers: List[str]) -> float:
    """分析回答深度"""
    # 分析回答的长度、细节、具体性
    avg_length = sum(len(a) for a in answers) / len(answers)
    specificity = calculate_specificity(answers)
    emotion_depth = analyze_emotional_depth(answers)
    
    return (avg_length * 0.3 + specificity * 0.4 + emotion_depth * 0.3)

def analyze_authenticity(answers: List[str]) -> float:
    """分析真实性"""
    # 检测模板化回答、虚假积极、过度消极
    template_score = detect_template_answers(answers)
    balance_score = analyze_emotional_balance(answers)
    
    return (template_score * 0.5 + balance_score * 0.5)

def detect_evasion(answers: List[str]) -> float:
    """检测回避"""
    evasion_types = ["否认", "转移", "最小化", "合理化", "攻击"]
    total_evasion = 0
    
    for answer in answers:
        for evasion_type in evasion_types:
            if detect_evasion_pattern(answer, evasion_type):
                total_evasion += 10  # 每次回避扣10分
    
    return total_evasion
```

### 2.2 窄门发现评测

#### 窄门优先级公式

```
窄门优先级 = 痛苦回避度 × 成长杠杆率
```

#### 评测结构

```python
class GateDiscoveryAssessment:
    """窄门发现评测"""
    id: str
    user_id: str
    timestamp: str
    
    # 发现的窄门
    discovered_gates: List[DiscoveredGate]
    
    # 排序后的窄门
    prioritized_gates: List[DiscoveredGate]
    
    # 推荐的起始窄门
    recommended_start: DiscoveredGate
    
class DiscoveredGate:
    """发现的窄门"""
    id: str
    name: str
    dimension: str  # 认知/情绪/行为/关系/事业
    
    # 窄门指标
    pain_avoidance: float      # 痛苦回避度（0-100）
    growth_leverage: float     # 成长杠杆率（0-100）
    priority_score: float      # 优先级得分
    
    # 详细分析
    description: str           # 描述
    evidence: List[str]        # 证据
    fears: List[str]           # 恐惧
    potential_gains: List[str] # 潜在收益
    
    # 建议
    recommended_master: str    # 推荐大师
    first_challenge: str       # 第一个挑战
```

#### 窄门发现算法

```python
def discover_gates(audit_results: SoulAuditAssessment) -> List[DiscoveredGate]:
    """从审计结果发现窄门"""
    gates = []
    
    # 分析每个维度的盲点
    for dimension in ["认知", "情绪", "行为", "关系", "事业"]:
        blind_spots = audit_results.blind_spots[dimension]
        
        for blind_spot in blind_spots:
            gate = analyze_blind_spot_to_gate(blind_spot, dimension)
            gates.append(gate)
    
    # 计算优先级
    for gate in gates:
        gate.priority_score = gate.pain_avoidance * gate.growth_leverage
    
    # 排序
    gates.sort(key=lambda g: g.priority_score, reverse=True)
    
    return gates

def analyze_blind_spot_to_gate(blind_spot: str, dimension: str) -> DiscoveredGate:
    """将盲点转化为窄门"""
    # 分析盲点的痛苦回避度
    pain_avoidance = calculate_pain_avoidance(blind_spot)
    
    # 分析成长杠杆率
    growth_leverage = calculate_growth_leverage(blind_spot, dimension)
    
    # 生成窄门描述
    description = generate_gate_description(blind_spot, dimension)
    
    # 识别恐惧
    fears = identify_fears(blind_spot)
    
    # 识别潜在收益
    potential_gains = identify_potential_gains(blind_spot)
    
    return DiscoveredGate(
        id=generate_id(),
        name=blind_spot,
        dimension=dimension,
        pain_avoidance=pain_avoidance,
        growth_leverage=growth_leverage,
        priority_score=pain_avoidance * growth_leverage,
        description=description,
        evidence=[],
        fears=fears,
        potential_gains=potential_gains,
        recommended_master=recommend_master(dimension),
        first_challenge=generate_first_challenge(blind_spot)
    )
```

### 2.3 进化层级评测

#### 五层进化模型

```
          ✨  第5层：神性层 — 存在即穿越
        ┌───┐
        │ 4 │  第4层：精通层 — 穿越成为习惯
      ┌─┴───┴─┐
      │   3   │  第3层：突破层 — 第一次穿越
    ┌─┴───────┴─┐
    │     2     │  第2层：觉醒层 — 看见枷锁
  ┌─┴───────────┴─┐
  │       1       │  第1层：睡眠层 — 不知道自己在睡
└───────────────────┘
```

#### 评测结构

```python
class EvolutionLevelAssessment:
    """进化层级评测"""
    id: str
    user_id: str
    timestamp: str
    
    # 当前层级
    current_level: int  # 1-5
    
    # 各层级得分（0-100）
    level_scores: Dict[int, float]
    
    # 层级特征分析
    level_traits: Dict[int, LevelTraits]
    
    # 进化进度
    progress_to_next: float  # 到下一层的进度（0-100）
    
    # 经验值
    total_exp: int
    exp_breakdown: Dict[str, int]

class LevelTraits:
    """层级特征"""
    level: int
    name: str
    description: str
    
    # 特征指标
    self_awareness: float      # 自我觉察
    action_taking: float       # 行动力
    consistency: float         # 一致性
    resilience: float          # 韧性
    wisdom: float              # 智慧
    
    # 行为表现
    behaviors: List[str]
    beliefs: List[str]
    challenges: List[str]
```

#### 层级判定算法

```python
def assess_evolution_level(user_data: Dict) -> EvolutionLevelAssessment:
    """评估进化层级"""
    # 收集指标
    metrics = collect_evolution_metrics(user_data)
    
    # 计算各层级得分
    level_scores = {}
    for level in range(1, 6):
        level_scores[level] = calculate_level_score(metrics, level)
    
    # 确定当前层级
    current_level = determine_current_level(level_scores)
    
    # 计算进度
    progress_to_next = calculate_progress_to_next(level_scores, current_level)
    
    # 分析层级特征
    level_traits = analyze_level_traits(metrics, current_level)
    
    return EvolutionLevelAssessment(
        id=generate_id(),
        user_id=user_data["user_id"],
        timestamp=get_timestamp(),
        current_level=current_level,
        level_scores=level_scores,
        level_traits=level_traits,
        progress_to_next=progress_to_next,
        total_exp=calculate_total_exp(user_data),
        exp_breakdown=breakdown_exp(user_data)
    )

def collect_evolution_metrics(user_data: Dict) -> Dict:
    """收集进化指标"""
    return {
        # 审计相关
        "audits_completed": user_data.get("audits_completed", 0),
        "audit_depth_avg": user_data.get("audit_depth_avg", 0),
        "evasion_detection_rate": user_data.get("evasion_detection_rate", 0),
        
        # 挑战相关
        "challenges_completed": user_data.get("challenges_completed", 0),
        "challenge_difficulty_avg": user_data.get("challenge_difficulty_avg", 0),
        "streak_days": user_data.get("streak_days", 0),
        
        # 穿越相关
        "crossings_completed": user_data.get("crossings_completed", 0),
        "crossing_records": user_data.get("crossing_records", 0),
        "witness_verifications": user_data.get("witness_verifications", 0),
        
        # 社区相关
        "helped_others": user_data.get("helped_others", 0),
        "shared_insights": user_data.get("shared_insights", 0),
        
        # 时间相关
        "days_active": user_data.get("days_active", 0),
        "total_time_spent": user_data.get("total_time_spent", 0)
    }
```

---

## 三、过程评测系统

### 3.1 每日挑战评测

#### 评测指标

```python
class DailyChallengeAssessment:
    """每日挑战评测"""
    id: str
    user_id: str
    challenge_id: str
    date: str
    
    # 完成情况
    status: str  # pending, in_progress, completed, skipped
    completion_time: str  # 完成时间
    difficulty_rating: int  # 用户自评难度（1-10）
    
    # 质量评估
    effort_level: int  # 努力程度（1-10）
    authenticity: int  # 真实性（1-10）
    learning_value: int  # 学习价值（1-10）
    
    # 穿越记录
    fear_before: str  # 之前的恐惧
    action_taken: str  # 采取的行动
    reality_after: str  # 之后的现实
    insight_gained: str  # 获得的洞见
    
    # 验证
    witness_verification: bool  # 见证人验证
    evidence_provided: bool  # 提供证据
```

#### 质量评分算法

```python
def assess_challenge_quality(challenge_data: DailyChallengeAssessment) -> float:
    """评估挑战质量"""
    base_score = 50
    
    # 完成情况
    if challenge_data.status == "completed":
        base_score += 30
    elif challenge_data.status == "in_progress":
        base_score += 10
    
    # 质量指标
    quality_score = (
        challenge_data.effort_level * 2 +
        challenge_data.authenticity * 2 +
        challenge_data.learning_value * 2
    ) / 3
    
    # 验证加成
    verification_bonus = 0
    if challenge_data.witness_verification:
        verification_bonus += 10
    if challenge_data.evidence_provided:
        verification_bonus += 5
    
    # 穿越记录质量
    record_quality = assess_record_quality(challenge_data)
    
    return base_score + quality_score + verification_bonus + record_quality

def assess_record_quality(challenge_data: DailyChallengeAssessment) -> float:
    """评估穿越记录质量"""
    score = 0
    
    # 恐惧描述质量
    if challenge_data.fear_before:
        fear_quality = analyze_text_quality(challenge_data.fear_before)
        score += fear_quality * 5
    
    # 行动描述质量
    if challenge_data.action_taken:
        action_quality = analyze_text_quality(challenge_data.action_taken)
        score += action_quality * 5
    
    # 现实对比质量
    if challenge_data.reality_after:
        reality_quality = analyze_text_quality(challenge_data.reality_after)
        score += reality_quality * 5
    
    # 洞见质量
    if challenge_data.insight_gained:
        insight_quality = analyze_text_quality(challenge_data.insight_gained)
        score += insight_quality * 10
    
    return score
```

### 3.2 对话深度评测

#### 对话分析维度

```python
class ConversationDepthAssessment:
    """对话深度评测"""
    id: str
    user_id: str
    conversation_id: str
    expert_id: str
    
    # 深度指标
    depth_level: int  # 1-4（表面→核心）
    depth_progression: List[int]  # 深度变化轨迹
    
    # 质量指标
    authenticity_score: float  # 真实性
    vulnerability_score: float  # 脆弱度
    insight_score: float  # 洞见度
    action_orientation: float  # 行动导向
    
    # 回避分析
    evasion_detected: int  # 检测到的回避次数
    evasion_types: Dict[str, int]  # 回避类型
    evasion_overcome: int  # 克服的回避次数
    
    # 突破点
    breakthrough_moments: List[BreakthroughMoment]

class BreakthroughMoment:
    """突破时刻"""
    timestamp: str
    message_index: int
    description: str
    depth_before: int
    depth_after: int
    insight_gained: str
```

#### 对话深度算法

```python
def assess_conversation_depth(conversation: Dict) -> ConversationDepthAssessment:
    """评估对话深度"""
    messages = conversation["messages"]
    
    # 分析每条消息的深度
    depth_levels = []
    for message in messages:
        depth = analyze_message_depth(message)
        depth_levels.append(depth)
    
    # 识别突破时刻
    breakthroughs = identify_breakthroughs(messages, depth_levels)
    
    # 分析回避
    evasion_analysis = analyze_evasion_in_conversation(messages)
    
    # 计算质量指标
    quality_metrics = calculate_conversation_quality(messages)
    
    return ConversationDepthAssessment(
        id=generate_id(),
        user_id=conversation["user_id"],
        conversation_id=conversation["id"],
        expert_id=conversation["expert_id"],
        depth_level=max(depth_levels),
        depth_progression=depth_levels,
        authenticity_score=quality_metrics["authenticity"],
        vulnerability_score=quality_metrics["vulnerability"],
        insight_score=quality_metrics["insight"],
        action_orientation=quality_metrics["action"],
        evasion_detected=evasion_analysis["total"],
        evasion_types=evasion_analysis["types"],
        evasion_overcome=evasion_analysis["overcome"],
        breakthrough_moments=breakthroughs
    )

def analyze_message_depth(message: Dict) -> int:
    """分析消息深度"""
    content = message["content"]
    
    # L1: 表面层 — 事实描述
    if is_surface_level(content):
        return 1
    
    # L2: 中间层 — 动机探索
    if is_motivation_level(content):
        return 2
    
    # L3: 深层 — 恐惧面对
    if is_fear_level(content):
        return 3
    
    # L4: 核心层 — 身份转变
    if is_identity_level(content):
        return 4
    
    return 1
```

### 3.3 回避模式评测

#### 回避类型

```python
EVASION_TYPES = {
    "否认": {
        "keywords": ["没有", "不是", "还好", "没什么", "不会"],
        "patterns": [r"我.*没有.*", r"这.*不是.*", r".*还好.*"],
        "description": "不愿承认问题存在"
    },
    "转移": {
        "keywords": ["说起来", "对了", "另外", "其实", "不过"],
        "patterns": [r"说起来.*", r"对了.*", r".*另外.*"],
        "description": "话题太痛，想跑"
    },
    "最小化": {
        "keywords": ["一点点", "稍微", "可能", "应该", "还好"],
        "patterns": [r".*一点点.*", r".*稍微.*", r".*可能.*"],
        "description": "承认问题但不想面对严重性"
    },
    "合理化": {
        "keywords": ["因为", "没办法", "大家都", "所以", "毕竟"],
        "patterns": [r".*因为.*", r".*没办法.*", r".*大家都.*"],
        "description": "给问题找借口"
    },
    "攻击": {
        "keywords": ["你凭什么", "你懂什么", "你怎么", "你才"],
        "patterns": [r"你凭什么.*", r"你懂什么.*", r"你.*怎么.*"],
        "description": "被戳中要害的防御反应"
    }
}
```

#### 回避评测结构

```python
class EvasionPatternAssessment:
    """回避模式评测"""
    id: str
    user_id: str
    period: str  # 评测周期
    
    # 回避统计
    total_evasions: int
    evasion_rate: float  # 回避率
    
    # 按类型统计
    evasion_by_type: Dict[str, int]
    
    # 按维度统计
    evasion_by_dimension: Dict[str, int]
    
    # 趋势分析
    evasion_trend: List[float]  # 回避率变化趋势
    
    # 严重度评估
    severity_level: str  # low, medium, high, critical
    severity_score: float
    
    # 改进建议
    improvement_areas: List[str]
    recommended_exercises: List[str]
```

---

## 四、结果评测系统

### 4.1 穿越验证系统

#### 验证维度

```python
class CrossingVerification:
    """穿越验证"""
    id: str
    user_id: str
    gate_id: str
    
    # 验证类型
    verification_type: str  # self, witness, evidence, expert
    
    # 验证内容
    before_state: Dict  # 之前状态
    after_state: Dict   # 之后状态
    change_evidence: List[str]  # 变化证据
    
    # 验证结果
    verified: bool
    verification_score: float
    verification_notes: str
    
    # 验证者
    verifier_id: str
    verifier_type: str  # user, witness, ai, expert
    verification_date: str
```

#### 验证方法

1. **自我验证**
   - 前后对比问卷
   - 行为日志分析
   - 情绪追踪对比

2. **见证人验证**
   - 见证人确认
   - 第三方证词
   - 社区投票

3. **证据验证**
   - 截图/照片
   - 数据记录
   - 外部链接

4. **专家验证**
   - 大师评价
   - 专家审核
   - AI分析

### 4.2 行为改变评测

#### 评测指标

```python
class BehaviorChangeAssessment:
    """行为改变评测"""
    id: str
    user_id: str
    gate_id: str
    period: str
    
    # 行为指标
    target_behavior: str  # 目标行为
    baseline_frequency: float  # 基线频率
    current_frequency: float  # 当前频率
    change_percentage: float  # 变化百分比
    
    # 一致性指标
    consistency_score: float  # 一致性得分
    streak_days: int  # 连续天数
    longest_streak: int  # 最长连续
    
    # 质量指标
    quality_score: float  # 行为质量
    effort_level: float  # 努力程度
    sustainability: float  # 可持续性
    
    # 障碍分析
    obstacles_encountered: List[str]
    obstacles_overcome: List[str]
    
    # 支持系统
    support_used: List[str]
    witness_involvement: float
```

### 4.3 身份转变评测

#### 身份维度

```python
class IdentityTransformationAssessment:
    """身份转变评测"""
    id: str
    user_id: str
    gate_id: str
    
    # 身份维度
    old_identity: Dict[str, str]  # 旧身份
    new_identity: Dict[str, str]  # 新身份
    
    # 转变指标
    belief_shift_score: float  # 信念转变
    behavior_shift_score: float  # 行为转变
    emotion_shift_score: float  # 情绪转变
    relationship_shift_score: float  # 关系转变
    
    # 整合度
    integration_score: float  # 整合度
    consistency_score: float  # 一致性
    
    # 叙事分析
    old_narrative: str  # 旧叙事
    new_narrative: str  # 新叙事
    narrative_shift: float  # 叙事转变度
```

---

## 五、可视化系统

### 5.1 个人成长仪表板

```
┌─────────────────────────────────────────┐
│           个人成长仪表板                 │
├─────────────────────────────────────────┤
│  当前层级：第3层 — 突破层               │
│  ████████████░░░░░░░░ 60% 到下一层      │
├─────────────────────────────────────────┤
│  灵魂审计得分                           │
│  认知：85 ████████░░                    │
│  情绪：70 ███████░░░                    │
│  行为：65 ██████░░░░                    │
│  关系：75 ███████░░░                    │
│  事业：80 ████████░░                    │
├─────────────────────────────────────────┤
│  本周进度                               │
│  挑战完成：5/7 ███████░░░               │
│  对话深度：L3 █████████░                │
│  回避率：15% ██░░░░░░░░                 │
├─────────────────────────────────────────┤
│  窄门进度                               │
│  🚪 拖延症穿越 ████████████░░░░ 75%     │
│  🚪 完美主义穿越 ████████░░░░░░░░ 50%   │
│  🚪 讨好模式穿越 ██████░░░░░░░░░░ 40%   │
└─────────────────────────────────────────┘
```

### 5.2 进化金字塔可视化

```python
def generate_pyramid_visualization(user_data: Dict) -> str:
    """生成进化金字塔可视化"""
    level = user_data["current_level"]
    progress = user_data["progress_to_next"]
    
    pyramid = """
          ✨  第5层：神性层 {l5_marker}
        ┌───┐
        │ 4 │  第4层：精通层 {l4_marker}
      ┌─┴───┴─┐
      │   3   │  第3层：突破层 {l3_marker}
    ┌─┴───────┴─┐
    │     2     │  第2层：觉醒层 {l2_marker}
  ┌─┴───────────┴─┐
  │       1       │  第1层：睡眠层 {l1_marker}
└───────────────────┘
    """.format(
        l5_marker="✅" if level >= 5 else " ",
        l4_marker="✅" if level >= 4 else " ",
        l3_marker="✅" if level >= 3 else " 👈 当前" if level == 3 else " ",
        l2_marker="✅" if level >= 2 else " ",
        l1_marker="✅" if level >= 1 else " "
    )
    
    return pyramid
```

### 5.3 进度追踪图表

```python
def generate_progress_chart(assessment_history: List[Dict]) -> Dict:
    """生成进度追踪图表"""
    return {
        "type": "line",
        "title": "成长轨迹",
        "x_axis": "时间",
        "y_axis": "得分",
        "series": [
            {
                "name": "综合得分",
                "data": [a["overall_score"] for a in assessment_history]
            },
            {
                "name": "认知维度",
                "data": [a["cognitive_score"] for a in assessment_history]
            },
            {
                "name": "情绪维度",
                "data": [a["emotional_score"] for a in assessment_history]
            }
        ]
    }
```

---

## 六、验证机制

### 6.1 多层次验证

```
┌─────────────────────────────────────────┐
│           穿越验证系统                   │
├─────────────────────────────────────────┤
│  Level 1: 自我验证                       │
│  ├─ 前后对比问卷                        │
│  ├─ 行为日志                            │
│  └─ 情绪追踪                            │
├─────────────────────────────────────────┤
│  Level 2: 见证人验证                     │
│  ├─ 见证人确认                          │
│  ├─ 第三方证词                          │
│  └─ 社区投票                            │
├─────────────────────────────────────────┤
│  Level 3: 证据验证                       │
│  ├─ 截图/照片                           │
│  ├─ 数据记录                            │
│  └─ 外部链接                            │
├─────────────────────────────────────────┤
│  Level 4: 专家验证                       │
│  ├─ 大师评价                            │
│  ├─ 专家审核                            │
│  └─ AI分析                              │
└─────────────────────────────────────────┘
```

### 6.2 验证分数计算

```python
def calculate_verification_score(verification: CrossingVerification) -> float:
    """计算验证分数"""
    base_score = 0
    
    # 验证类型权重
    type_weights = {
        "self": 0.3,
        "witness": 0.4,
        "evidence": 0.5,
        "expert": 0.6
    }
    
    base_score = type_weights[verification.verification_type] * 100
    
    # 证据质量加成
    evidence_quality = assess_evidence_quality(verification.change_evidence)
    base_score += evidence_quality * 20
    
    # 时间因素（近期验证权重更高）
    time_factor = calculate_time_factor(verification.verification_date)
    base_score *= time_factor
    
    return min(100, base_score)
```

### 6.3 验证徽章系统

```python
VERIFICATION_BADGES = {
    "self_verified": {
        "name": "自我觉醒",
        "description": "通过自我验证",
        "icon": "👁️",
        "requirement": "完成自我验证"
    },
    "witness_verified": {
        "name": "真实见证",
        "description": "通过见证人验证",
        "icon": "👥",
        "requirement": "获得见证人确认"
    },
    "evidence_verified": {
        "name": "铁证如山",
        "description": "提供证据验证",
        "icon": "📸",
        "requirement": "提供可验证证据"
    },
    "expert_verified": {
        "name": "大师认可",
        "description": "通过专家验证",
        "icon": "🧙",
        "requirement": "获得专家认可"
    },
    "fully_verified": {
        "name": "穿越完成",
        "description": "通过所有验证",
        "icon": "✨",
        "requirement": "通过所有验证层级"
    }
}
```

---

## 七、数据分析和洞察

### 7.1 个人洞察报告

```python
def generate_personal_insights(user_data: Dict) -> Dict:
    """生成个人洞察报告"""
    return {
        "strengths": identify_strengths(user_data),
        "blind_spots": identify_blind_spots(user_data),
        "patterns": identify_patterns(user_data),
        "growth_opportunities": identify_growth_opportunities(user_data),
        "recommendations": generate_recommendations(user_data),
        "predictions": predict_future_growth(user_data)
    }

def identify_strengths(user_data: Dict) -> List[Dict]:
    """识别优势"""
    strengths = []
    
    # 分析各维度得分
    dimension_scores = user_data.get("dimension_scores", {})
    for dimension, score in dimension_scores.items():
        if score >= 80:
            strengths.append({
                "dimension": dimension,
                "score": score,
                "description": f"在{dimension}维度表现优秀"
            })
    
    # 分析行为模式
    if user_data.get("consistency_score", 0) >= 80:
        strengths.append({
            "dimension": "行为",
            "score": user_data["consistency_score"],
            "description": "高度一致性和坚持力"
        })
    
    return strengths

def identify_blind_spots(user_data: Dict) -> List[Dict]:
    """识别盲点"""
    blind_spots = []
    
    # 分析回避模式
    evasion_patterns = user_data.get("evasion_patterns", {})
    for pattern, count in evasion_patterns.items():
        if count >= 5:
            blind_spots.append({
                "type": pattern,
                "frequency": count,
                "description": f"频繁使用{pattern}回避"
            })
    
    # 分析低分维度
    dimension_scores = user_data.get("dimension_scores", {})
    for dimension, score in dimension_scores.items():
        if score < 50:
            blind_spots.append({
                "dimension": dimension,
                "score": score,
                "description": f"{dimension}维度需要关注"
            })
    
    return blind_spots
```

### 7.2 群体比较分析

```python
def generate_peer_comparison(user_data: Dict, peer_data: List[Dict]) -> Dict:
    """生成同伴比较分析"""
    user_scores = user_data.get("dimension_scores", {})
    
    # 计算同伴平均分
    peer_averages = {}
    for dimension in user_scores.keys():
        peer_scores = [p["dimension_scores"][dimension] for p in peer_data]
        peer_averages[dimension] = sum(peer_scores) / len(peer_scores)
    
    # 计算百分位
    percentiles = {}
    for dimension in user_scores.keys():
        user_score = user_scores[dimension]
        peer_scores = [p["dimension_scores"][dimension] for p in peer_data]
        percentile = calculate_percentile(user_score, peer_scores)
        percentiles[dimension] = percentile
    
    return {
        "user_scores": user_scores,
        "peer_averages": peer_averages,
        "percentiles": percentiles,
        "summary": generate_comparison_summary(user_scores, peer_averages, percentiles)
    }
```

---

## 八、实施计划

### 8.1 第一阶段：基础评测（1-2周）

1. **完善灵魂审计评测**
   - 优化评分算法
   - 添加更多题目
   - 改进回避检测

2. **实现窄门发现评测**
   - 优先级算法
   - 窄门推荐
   - 可视化展示

3. **建立进化层级评测**
   - 层级判定算法
   - 经验值系统
   - 进度追踪

### 8.2 第二阶段：过程评测（2-3周）

1. **每日挑战评测**
   - 完成度追踪
   - 质量评估
   - 穿越记录分析

2. **对话深度评测**
   - 深度分析算法
   - 突破点识别
   - 回避检测

3. **回避模式评测**
   - 回避类型识别
   - 趋势分析
   - 改进建议

### 8.3 第三阶段：结果评测（3-4周）

1. **穿越验证系统**
   - 多层验证机制
   - 证据收集
   - 验证分数

2. **行为改变评测**
   - 行为追踪
   - 改变量化
   - 可持续性评估

3. **身份转变评测**
   - 身份维度分析
   - 叙事转变
   - 整合度评估

### 8.4 第四阶段：可视化和洞察（4-5周）

1. **个人仪表板**
   - 数据可视化
   - 进度展示
   - 实时更新

2. **洞察报告**
   - 个人分析
   - 群体比较
   - 预测建议

3. **验证徽章**
   - 徽章设计
   - 成就系统
   - 社交分享

---

*最后更新：2026-04-19*
*维护者：贾维斯 (Jarvis) for 小林医生*
*版本：v1.0*

---

> **"评测不是目的，是手段。通过评测，我们看见自己；通过验证，我们证明成长。"**
