"""
窄门 (NarrowGate) — API服务 v2.0

集成MIMO API + SQLite + 大师AI对话 + 完整前端

架构师：贾维斯 (Jarvis) for 小林医生
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from datetime import datetime

from core.soul_audit import SoulAuditEngine, AUDIT_DIMENSIONS
from core.gate_finder import GateFinder
from core.crossing import CrossingEngine
from core.masters import MasterManager
from core.database import Database
from core.mimo_client import MIMOClient, MIMOConfig
from core.witness import WitnessNetwork
from core.evolution import EvolutionPyramid
from core.auth import create_auth_routes
from expert_routes import router as expert_router
from core.course_content import get_all_days, get_day, get_week, COURSE_CONTENT
from core.payment import create_payment_routes, PaymentConfig
from core.logger import setup_logger, get_logger
from core.analytics import AnalyticsManager, create_analytics_routes
from api.middleware import RequestLoggingMiddleware, ErrorTrackingMiddleware

# ============================================================
# App
# ============================================================

# 初始化日志系统
logger = setup_logger("narrowgate")
logger.info("🚀 窄门 NarrowGate 启动中...")

app = FastAPI(
    title="窄门 NarrowGate",
    description="让人看见窄门并跨越窄门的进化平台",
    version="2.1.0",
)

# 添加中间件
app.add_middleware(ErrorTrackingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# 注册路由
app.include_router(expert_router)

# 核心引擎
audit_engine = SoulAuditEngine()
gate_finder = GateFinder()
crossing_engine = CrossingEngine()
master_manager = MasterManager()
db = Database()
mimo = MIMOClient()
witness_network = WitnessNetwork()
evolution_pyramid = EvolutionPyramid()

# 认证系统
auth_manager = create_auth_routes(app, db)

# 支付系统
payment_config = PaymentConfig.from_env()
payment_manager = create_payment_routes(app, db, payment_config)
logger.info("💳 支付系统已初始化")

# 数据分析系统
analytics_manager = AnalyticsManager(db)
analytics_routes = create_analytics_routes(app, analytics_manager)
logger.info("📊 数据分析系统已初始化")

# 内存缓存（补充数据库）
_active_audits: Dict[str, object] = {}
_conversation_histories: Dict[str, List[Dict]] = {}


# ============================================================
# Models
# ============================================================

class StartAuditRequest(BaseModel):
    user_id: str = ""
    username: str = ""

class SubmitAnswerRequest(BaseModel):
    audit_id: str
    answer: str
    master_id: str = ""

class ChooseMasterRequest(BaseModel):
    audit_id: str
    master_id: str

class StartCrossingRequest(BaseModel):
    user_id: str
    gate_name: str = ""
    gate_dimension: str = ""

class CompleteChallengeRequest(BaseModel):
    crossing_id: str
    response: str
    witness: bool = False

class AddDivinityRequest(BaseModel):
    user_id: str
    record_type: str = "crossing"
    title: str = ""
    description: str = ""
    evidence: str = ""
    dimension: str = ""


# ============================================================
# 首页
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """返回前端页面"""
    ui_path = Path(__file__).parent.parent / "ui" / "index.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>窄门 NarrowGate</h1><p>界面加载中...</p>")


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "narrowgate", "version": "2.1.0"}


# ============================================================
# 用户 API
# ============================================================

@app.post("/api/user/register")
async def register_user(req: StartAuditRequest):
    """注册用户"""
    user = db.create_user(req.username or None)
    return user

@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """获取用户信息"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    crossings = db.get_user_active_crossings(user_id)
    records = db.get_divinity_records(user_id)
    return {
        "user": user,
        "active_crossings": len(crossings),
        "divinity_records": len(records),
    }


# ============================================================
# 灵魂审计 API
# ============================================================

@app.post("/api/audit/start")
async def start_audit(req: StartAuditRequest):
    """开始灵魂审计"""
    # 创建或获取用户
    user_id = req.user_id
    if not user_id or not db.get_user(user_id):
        user = db.create_user(req.username)
        user_id = user["id"]

    # 创建审计
    audit_id = db.create_audit(user_id)

    # 加载到内存
    audit = audit_engine.create_audit(user_id)
    audit.id = audit_id
    _active_audits[audit_id] = audit
    _conversation_histories[audit_id] = []

    question = audit_engine.get_next_question(audit)

    return {
        "audit_id": audit_id,
        "user_id": user_id,
        "status": "in_progress",
        "dimension": audit.current_dimension,
        "question": question.question,
        "depth_level": question.depth_level,
        "purpose": question.purpose,
    }


@app.post("/api/audit/answer")
async def submit_answer(req: SubmitAnswerRequest):
    """提交审计回答（支持MIMO AI追问）"""
    audit = _active_audits.get(req.audit_id)
    if not audit:
        # 从数据库恢复
        audit_data = db.get_audit(req.audit_id)
        if not audit_data:
            raise HTTPException(404, "审计不存在")
        audit = audit_engine.create_audit(audit_data["user_id"])
        audit.id = req.audit_id
        _active_audits[req.audit_id] = audit
        _conversation_histories[req.audit_id] = []

    history = _conversation_histories.get(req.audit_id, [])

    # 处理回答
    response = audit_engine.process_response(audit, req.answer)

    # 保存到数据库
    db.save_audit_response(req.audit_id, {
        "question": response.question,
        "answer": req.answer,
        "dimension": audit.current_dimension,
        "depth_level": audit.current_depth,
        "evasion_detected": response.evasion_detected,
        "evasion_type": response.evasion_type,
        "ai_analysis": response.ai_analysis,
        "master_id": req.master_id,
    })

    # 更新审计记录
    db.update_audit(req.audit_id,
        current_dimension=audit.current_dimension,
        current_depth=audit.current_depth,
        shackle_map={sid: {"name": s.name, "dimension": s.dimension, "priority": s.gate_priority}
                     for sid, s in audit.shackle_map.items()},
        gate_candidates=audit.gate_candidates,
    )

    # 用MIMO生成AI追问
    history.append({"role": "user", "content": req.answer})

    if req.master_id:
        master = master_manager.get_master(req.master_id)
        if master:
            ai_reply = await mimo.master_converse(
                master_name=master.name,
                master_persona=master.personality,
                master_style=master.questioning_style,
                user_message=req.answer,
                conversation_history=history[-6:],
                evasion_detected=response.evasion_detected,
                evasion_type=response.evasion_type,
            )
            history.append({"role": "assistant", "content": ai_reply})

            return {
                "evasion_detected": response.evasion_detected,
                "evasion_type": response.evasion_type,
                "ai_reply": ai_reply,
                "shackles_found": len(audit.shackle_map),
                "dimension": audit.current_dimension,
                "depth": audit.current_depth,
                "conversation_count": len(history),
            }

    # 无大师时用审计引擎默认追问
    next_q = audit_engine.get_next_question(audit)

    # 尝试用MIMO增强追问
    try:
        ai_reply = await mimo.soul_audit_question(
            dimension=audit.current_dimension,
            depth=audit.current_depth,
            user_answer=req.answer,
            evasion_detected=response.evasion_detected,
            evasion_type=response.evasion_type,
        )
    except Exception:
        ai_reply = next_q.question

    history.append({"role": "assistant", "content": ai_reply})

    return {
        "evasion_detected": response.evasion_detected,
        "evasion_type": response.evasion_type,
        "ai_analysis": response.ai_analysis,
        "ai_reply": ai_reply,
        "shackles_found": len(audit.shackle_map),
        "dimension": audit.current_dimension,
        "depth": audit.current_depth,
        "conversation_count": len(history),
    }


@app.post("/api/audit/complete")
async def complete_audit(req: StartAuditRequest):
    """完成灵魂审计"""
    # 查找用户的进行中审计
    audit = None
    audit_id = None
    for aid, a in _active_audits.items():
        if a.user_id == req.user_id and a.status == "in_progress":
            audit = a
            audit_id = aid
            break

    if not audit:
        raise HTTPException(404, "没有进行中的审计")

    # 完成审计
    report = audit_engine.complete_audit(audit)

    # 保存到数据库
    shackle_map = {sid: {"name": s.name, "dimension": s.dimension, "priority": s.gate_priority}
                   for sid, s in audit.shackle_map.items()}
    db.complete_audit(audit_id, shackle_map, audit.gate_candidates)

    return report


@app.get("/api/audit/{audit_id}/recommend")
async def get_course_recommendation(audit_id: str):
    """获取审计完成后的课程推荐"""
    audit = _active_audits.get(audit_id)
    if not audit:
        raise HTTPException(404, "审计不存在")
    return audit_engine.generate_course_recommendation(audit)


@app.get("/api/audit/{audit_id}")
async def get_audit(audit_id: str):
    """获取审计详情"""
    audit_data = db.get_audit(audit_id)
    if not audit_data:
        raise HTTPException(404, "审计不存在")
    responses = db.get_audit_responses(audit_id)
    return {**audit_data, "responses": responses}


@app.get("/api/audit/{audit_id}/gates")
async def get_gates(audit_id: str):
    """获取窄门候选"""
    audit = _active_audits.get(audit_id)
    if not audit:
        raise HTTPException(404, "请先完成灵魂审计")

    gates = gate_finder.find_gates(audit)
    report = gate_finder.generate_gate_report(gates)
    return report


# ============================================================
# 大师 API
# ============================================================

@app.get("/api/masters")
async def list_masters(user_level: int = 1):
    """获取可用大师列表"""
    return {
        "masters": master_manager.get_all_master_cards(user_level),
        "total": len(master_manager.get_available_masters(user_level)),
    }


@app.get("/api/masters/{master_id}")
async def get_master_detail(master_id: str):
    """获取大师详情"""
    master = master_manager.get_master(master_id)
    if not master:
        raise HTTPException(404, "大师不存在")
    return {
        "id": master.id,
        "name": master.name,
        "title": master.title,
        "avatar": master.avatar,
        "philosophy": master.philosophy,
        "dimension": master.dimension,
        "personality": master.personality,
        "greeting": master.greeting,
        "questioning_style": master.questioning_style,
        "specialties": master.specialties,
        "signature_phrases": master.signature_phrases,
        "color": master.color,
    }


@app.post("/api/masters/choose")
async def choose_master(req: ChooseMasterRequest):
    """选择大师开始引导对话"""
    audit = _active_audits.get(req.audit_id)
    if not audit:
        raise HTTPException(404, "请先开始灵魂审计")

    master = master_manager.get_master(req.master_id)
    if not master:
        raise HTTPException(404, "大师不存在")

    return {
        "master": master_manager.get_master_card(master),
        "greeting": master.greeting,
        "style": master.questioning_style,
    }


class MasterChatRequest(BaseModel):
    master_id: str
    message: str
    user_id: str = "anonymous"


@app.post("/api/masters/chat")
async def chat_with_master(req: MasterChatRequest):
    """与大师对话（MIMO AI驱动）"""
    master = master_manager.get_master(req.master_id)
    if not master:
        raise HTTPException(404, "大师不存在")

    try:
        from core.mimo_client import MIMOClient, MIMOConfig

        # Build system prompt from master's personality
        system_prompt = f"""你是{master.name}，{master.title}。
性格：{master.personality}
哲学：{master.philosophy}
提问风格：{master.questioning_style}
专长维度：{master.dimension}

你的职责是引导用户深度反思，发现内在真相。你从不给直接答案，而是用苏格拉底式追问让用户自己发现。

语言风格：简洁、深刻、有时带点幽默和刺痛感。每次回复控制在1-2句话。
"""

        config = MIMOConfig()
        mimo = MIMOClient(config)
        messages = [{"role": "user", "content": req.message}]
        reply = await mimo.chat(messages, system_prompt=system_prompt, temperature=0.8)

        return {
            "success": True,
            "master_id": master.id,
            "master_name": master.name,
            "master_avatar": master.avatar,
            "reply": reply,
            "signature_phrases": master.signature_phrases,
        }
    except Exception as e:
        # Fallback to signature phrase
        import random
        phrase = random.choice(master.signature_phrases)
        return {
            "success": True,
            "master_id": master.id,
            "master_name": master.name,
            "master_avatar": master.avatar,
            "reply": phrase,
            "fallback": True,
        }


# ============================================================
# 穿越训练 API
# ============================================================

@app.post("/api/crossing/start")
async def start_crossing(req: StartCrossingRequest):
    """开始穿越窄门"""
    # 创建穿越记录
    crossing_id = db.create_crossing(
        req.user_id,
        gate_id=f"gate_{req.gate_dimension}_{req.gate_name}",
        gate_name=req.gate_name or f"{req.gate_dimension}窄门",
    )

    # 生成第一天挑战
    from core.gate_finder import NarrowGate
    gate = NarrowGate(
        id=f"gate_{req.gate_dimension}",
        name=req.gate_name or f"{req.gate_dimension}窄门",
        description="穿越训练",
        dimension=req.gate_dimension or "行为",
        priority_score=80,
        why_this_gate="你的窄门已识别",
        wide_gate_path="选择容易的路",
        narrow_gate_path="做你最不想做的事",
    )
    challenge = crossing_engine.generate_daily_challenge(gate, 0)

    # 保存每日记录
    db.save_daily_record(crossing_id, {
        "day": 1,
        "challenge": challenge.challenge,
        "difficulty": challenge.difficulty,
        "status": "pending",
    })

    return {
        "crossing_id": crossing_id,
        "gate_name": req.gate_name,
        "today_challenge": {
            "challenge": challenge.challenge,
            "difficulty": challenge.difficulty,
            "day": 1,
        },
    }


@app.post("/api/crossing/complete")
async def complete_challenge(req: CompleteChallengeRequest):
    """完成今日挑战"""
    crossing = db.get_crossing(req.crossing_id)
    if not crossing:
        raise HTTPException(404, "穿越记录不存在")

    new_day = crossing["current_day"] + 1
    new_completed = crossing["completed"] + 1
    new_streak = crossing["streak"] + 1
    new_max = max(crossing["max_streak"], new_streak)

    db.update_crossing(req.crossing_id,
        current_day=new_day,
        completed=new_completed,
        streak=new_streak,
        max_streak=new_max,
    )

    # 添加神性记录
    db.add_divinity_record(crossing["user_id"], {
        "type": "challenge_completed",
        "title": f"穿越挑战 Day {new_day}",
        "description": req.response,
        "dimension": "行为",
        "verified": req.witness,
    })

    # 生成明天的挑战
    from core.gate_finder import NarrowGate
    gate = NarrowGate(
        id=crossing["gate_id"],
        name=crossing["gate_name"],
        description="穿越训练",
        dimension="行为",
        priority_score=80,
        why_this_gate="穿越中",
        wide_gate_path="容易的路",
        narrow_gate_path="难但对的路",
    )
    next_challenge = crossing_engine.generate_daily_challenge(gate, new_day)

    # 检查是否穿越
    is_crossed = new_day >= 30 and (new_completed / max(new_day, 1)) >= 0.8

    result = {
        "completed": True,
        "day": new_day,
        "streak": new_streak,
        "completion_rate": f"{new_completed / max(new_day, 1) * 100:.0f}%",
        "tomorrow_challenge": next_challenge.challenge,
        "is_crossed": is_crossed,
    }

    if is_crossed:
        db.update_crossing(req.crossing_id, status="completed", completed_at=datetime.now().isoformat())
        result["message"] = "🚪 你穿越了窄门。欢迎来到下一个层级。"

    return result


@app.get("/api/crossing/{crossing_id}")
async def get_crossing_detail(crossing_id: str):
    """获取穿越详情"""
    crossing = db.get_crossing(crossing_id)
    if not crossing:
        raise HTTPException(404, "穿越记录不存在")
    records = db.get_daily_records(crossing_id)
    return {**crossing, "daily_records": records}


# ============================================================
# 神性档案 API
# ============================================================

@app.get("/api/divinity/{user_id}")
async def get_divinity(user_id: str):
    """获取神性档案"""
    records = db.get_divinity_records(user_id)
    return {
        "user_id": user_id,
        "total_records": len(records),
        "records": records,
    }


@app.post("/api/divinity/add")
async def add_divinity(req: AddDivinityRequest):
    """添加神性记录"""
    record_id = db.add_divinity_record(req.user_id, {
        "type": req.record_type,
        "title": req.title,
        "description": req.description,
        "evidence": req.evidence,
        "dimension": req.dimension,
    })
    return {"id": record_id, "status": "added"}


# ============================================================
# 平台统计
# ============================================================

@app.get("/api/stats")
async def get_platform_stats():
    """获取平台统计"""
    return db.get_stats()



# ============================================================
# 见证人 API
# ============================================================



# ============================================================
# 30天训练计划 API
# ============================================================

@app.get("/api/training/plan")
async def get_training_plan():
    """获取30天四周训练计划"""
    from core.crossing import TRAINING_WEEKS
    return {"weeks": TRAINING_WEEKS, "total_days": 30}

@app.get("/api/training/week/{day}")
async def get_training_week(day: int):
    """根据天数获取当前周计划"""
    from core.crossing import get_week_for_day
    return get_week_for_day(day)

@app.get("/api/training/challenge/{gate_id}/day/{day}")
async def get_daily_challenge_detail(gate_id: str, day: int):
    """获取某天的详细挑战（含四周上下文）"""
    from core.crossing import get_week_for_day
    week = get_week_for_day(day)
    crossing = crossing_engine.active_crossings.get(gate_id)
    if not crossing:
        raise HTTPException(404, "未找到穿越记录")

    gate = gate_finder.get_gate(gate_id) if hasattr(gate_finder, 'get_gate') else None
    challenge = crossing_engine.generate_daily_challenge(
        gate or type('obj', (object,), {'id': gate_id, 'dimension': '认知', 'name': '通用窄门', 'estimated_crossing_days': 30})(),
        day
    )

    return {
        "challenge": {
            "id": challenge.id,
            "day": day,
            "text": challenge.challenge,
            "difficulty": challenge.difficulty,
            "status": challenge.status,
        },
        "week": week,
        "progress": crossing_engine.get_progress_report(crossing),
        "record_template": {
            "fear_before": "做之前，写下你害怕发生什么",
            "action": "具体描述你怎么做的",
            "insight": "做完后发现了什么？恐惧 vs 现实的差距",
        },
    }

class WitnessRequest(BaseModel):
    name: str
    email: str = ""
    relationship: str = "朋友"

class VerifyRequest(BaseModel):
    witness_id: str
    crossing_id: str
    day: int
    challenge: str
    approved: bool = True
    message: str = ""

@app.post("/api/witness/add")
async def add_witness(req: WitnessRequest):
    """添加见证人"""
    witness = witness_network.add_witness(req.name, req.email, req.relationship)
    return witness.to_dict()

@app.get("/api/witness/list")
async def list_witnesses():
    """获取所有见证人"""
    return [w.to_dict() for w in witness_network.get_all_witnesses()]

@app.post("/api/witness/verify")
async def verify_witness(req: VerifyRequest):
    """发送见证验证"""
    verification = witness_network.send_verification_request(
        req.witness_id, req.crossing_id, req.day, req.challenge
    )
    return verification.to_dict()

@app.get("/api/witness/report/{crossing_id}")
async def get_witness_report(crossing_id: str):
    """获取见证报告"""
    return witness_network.get_witness_report(crossing_id)


# ============================================================
# 进化金字塔 API
# ============================================================

class EvolutionRequest(BaseModel):
    user_id: str
    gate_name: str = ""
    description: str = ""

@app.get("/api/evolution/{user_id}")
async def get_evolution(user_id: str):
    """获取用户进化状态"""
    return evolution_pyramid.get_pyramid_data(user_id)

@app.get("/api/evolution/{user_id}/pyramid")
async def get_evolution_visual(user_id: str):
    """获取进化金字塔可视化"""
    return {"pyramid": evolution_pyramid.get_visual_pyramid(user_id)}

@app.post("/api/evolution/breakthrough")
async def record_breakthrough(req: EvolutionRequest):
    """记录突破"""
    return evolution_pyramid.record_breakthrough(req.user_id, req.gate_name, req.description)

@app.post("/api/evolution/crossing-complete")
async def record_evolution_crossing(req: EvolutionRequest):
    """记录穿越完成（进化版）"""
    return evolution_pyramid.record_crossing_completion(req.user_id, req.gate_name)


# ============================================================
# 课程内容 API
# ============================================================

@app.get("/api/course/overview")
async def get_course_overview():
    """获取全部30天课程概览"""
    return {
        "total_days": 30,
        "days": get_all_days(),
        "weeks": [
            {"week": 1, "name": "面对恐惧", "days": "D1-D7"},
            {"week": 2, "name": "建立节奏", "days": "D8-D14"},
            {"week": 3, "name": "突破瓶颈", "days": "D15-D21"},
            {"week": 4, "name": "巩固穿越", "days": "D22-D30"},
        ],
    }


@app.get("/api/course/day/{day}")
async def get_course_day(day: int):
    """获取单天课程详情"""
    if day < 1 or day > 30:
        raise HTTPException(400, "无效的天数，请输入1-30")

    day_content = get_day(day)
    if not day_content:
        raise HTTPException(404, "课程内容未找到")

    week_info = get_week(day_content["week"])

    # 添加理论映射信息
    theory_mapping = {
        "dimension": day_content.get("dimension", ""),
        "evolution_target": day_content.get("evolution_target", ""),
        "evasion_detection": day_content.get("evasion_detection", ""),
        "theory_reference": day_content.get("theory_reference", "")
    }

    return {
        "day": day,
        "content": day_content,
        "theory_mapping": theory_mapping,
        "week": {
            "week": day_content["week"],
            "days_in_week": week_info,
        },
        "progress": {
            "current_day": day,
            "total_days": 30,
            "percentage": round(day / 30 * 100, 1),
        },
    }


@app.get("/api/course/progress/{user_id}")
async def get_course_progress(user_id: str):
    """获取用户课程进度"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(404, "用户未找到")

    # 查询用户的穿越记录
    with db._connect() as conn:
        crossings = conn.execute(
            "SELECT * FROM crossings WHERE user_id = ? ORDER BY started_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()

        if not crossings:
            return {
                "user_id": user_id,
                "has_started": False,
                "current_day": 0,
                "completed_days": [],
                "total_days": 30,
                "started_at": None,
                "last_activity": None,
            }

        crossing_id = crossings["id"]

        # 获取已完成的天数
        completed = conn.execute(
            "SELECT day, completed_at FROM daily_records WHERE crossing_id = ? AND status = 'completed' ORDER BY day",
            (crossing_id,),
        ).fetchall()

        completed_days = [row["day"] for row in completed]
        current_day = max(completed_days) + 1 if completed_days else 1

        return {
            "user_id": user_id,
            "has_started": True,
            "crossing_id": crossing_id,
            "current_day": min(current_day, 30),
            "completed_days": completed_days,
            "total_days": 30,
            "started_at": crossings["started_at"],
            "last_activity": completed[-1]["completed_at"] if completed else None,
            "streak": crossings["streak"],
            "max_streak": crossings["max_streak"],
        }


class CourseCompleteRequest(BaseModel):
    user_id: str
    day: int
    reflection: str = ""
    completed_challenge: bool = True

@app.post("/api/course/complete")
async def complete_course_day(req: CourseCompleteRequest):
    """标记某天课程完成"""
    if req.day < 1 or req.day > 30:
        raise HTTPException(400, "无效的天数，请输入1-30")

    day_content = get_day(req.day)
    if not day_content:
        raise HTTPException(404, "课程内容未找到")

    user = db.get_user(req.user_id)
    if not user:
        raise HTTPException(404, "用户未找到")

    now = datetime.now().isoformat()

    with db._connect() as conn:
        # 查找或创建穿越记录
        crossing = conn.execute(
            "SELECT id FROM crossings WHERE user_id = ? AND status = 'active' ORDER BY started_at DESC LIMIT 1",
            (req.user_id,),
        ).fetchone()

        if not crossing:
            crossing_id = f"crossing_{req.user_id}_{req.day}"
            conn.execute(
                "INSERT INTO crossings (id, user_id, gate_id, gate_name, status, current_day, total_days, started_at) VALUES (?, ?, ?, ?, 'active', ?, 30, ?)",
                (crossing_id, req.user_id, "course", "30天穿越训练", req.day, now),
            )
        else:
            crossing_id = crossing["id"]
            conn.execute(
                "UPDATE crossings SET current_day = ? WHERE id = ?",
                (max(req.day, conn.execute("SELECT current_day FROM crossings WHERE id = ?", (crossing_id,)).fetchone()["current_day"]), crossing_id),
            )

        # 记录每日完成
        record_id = f"record_{crossing_id}_day{req.day}"
        conn.execute(
            "INSERT OR REPLACE INTO daily_records (id, crossing_id, day, challenge, difficulty, status, response, created_at, completed_at) VALUES (?, ?, ?, ?, ?, 'completed', ?, ?, ?)",
            (record_id, crossing_id, req.day, day_content["challenge"], day_content["difficulty"], req.reflection, now, now),
        )

        # 更新连续天数
        crossing_data = conn.execute("SELECT streak, max_streak FROM crossings WHERE id = ?", (crossing_id,)).fetchone()
        new_streak = crossing_data["streak"] + 1
        new_max = max(new_streak, crossing_data["max_streak"])
        conn.execute(
            "UPDATE crossings SET streak = ?, max_streak = ? WHERE id = ?",
            (new_streak, new_max, crossing_id),
        )

    # 奖励经验值
    xp_earned = day_content["xp"]
    evolution_pyramid.add_experience(req.user_id, xp_earned)

    return {
        "success": True,
        "message": f"第{req.day}天「{day_content['title']}」已完成",
        "xp_earned": xp_earned,
        "streak": new_streak,
        "next_day": req.day + 1 if req.day < 30 else None,
        "next_title": get_day(req.day + 1)["title"] if req.day < 30 else "🎉 全部完成！",
    }


# ============================================================
# 学习日记 API
# ============================================================

class JournalSaveRequest(BaseModel):
    user_id: str
    day: int
    content: str
    mood: Optional[str] = None
    tags: Optional[List[str]] = []
    is_private: bool = True

class JournalDeleteRequest(BaseModel):
    user_id: str
    day: int

@app.post("/api/journal/save")
async def save_journal(req: JournalSaveRequest):
    """保存学习日记"""
    try:
        journal_id = db.save_journal(
            user_id=req.user_id,
            day=req.day,
            content=req.content,
            mood=req.mood,
            tags=req.tags or [],
            is_private=req.is_private
        )
        
        # 奖励经验值（每篇日记+5 XP）
        evolution_pyramid.add_experience(req.user_id, 5)
        
        return {
            "success": True,
            "journal_id": journal_id,
            "message": f"第{req.day}天日记保存成功",
            "xp_earned": 5
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

@app.get("/api/journal/{user_id}/{day}")
async def get_journal(user_id: str, day: int):
    """获取指定天的学习日记"""
    journal = db.get_journal(user_id, day)
    if not journal:
        raise HTTPException(status_code=404, detail="日记不存在")
    return journal

@app.get("/api/journals/{user_id}")
async def get_user_journals(user_id: str, limit: int = 30):
    """获取用户的所有学习日记"""
    journals = db.get_user_journals(user_id, limit)
    return {
        "user_id": user_id,
        "journals": journals,
        "total": len(journals)
    }

@app.delete("/api/journal/{user_id}/{day}")
async def delete_journal(user_id: str, day: int):
    """删除指定天的学习日记"""
    success = db.delete_journal(user_id, day)
    if not success:
        raise HTTPException(status_code=404, detail="日记不存在")
    return {
        "success": True,
        "message": f"第{day}天日记已删除"
    }

@app.get("/api/journal/stats/{user_id}")
async def get_journal_stats(user_id: str):
    """获取用户日记统计"""
    stats = db.get_journal_stats(user_id)
    return {
        "user_id": user_id,
        "stats": stats
    }


# ============================================================
# 奖励系统 API
# ============================================================

class RewardClaimRequest(BaseModel):
    user_id: str
    day: int
    completed_at: str

@app.post("/api/reward/claim")
async def claim_reward(req: RewardClaimRequest):
    """领取每日奖励"""
    try:
        # 获取课程内容
        day_content = get_day(req.day)
        if not day_content:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        # 计算基础经验值
        base_xp = day_content["xp"]
        
        # 获取用户进度
        user_progress = db.get_user_progress(req.user_id)
        streak = user_progress.get("streak", 0) + 1 if user_progress else 1
        
        # 计算连续奖励
        streak_bonus = streak * 2  # 连续天数 × 2 XP
        
        # 计算周奖励
        week_bonus = 0
        if req.day % 7 == 0:  # 每周结束
            week = req.day // 7
            week_bonus = week * 50  # 每周50 XP
        
        # 计算特殊奖励
        special_bonus = 0
        if req.day == 7:
            special_bonus = 20  # 第一周复盘
        elif req.day == 14:
            special_bonus = 20  # 第二周复盘
        elif req.day == 21:
            special_bonus = 25  # 第三周复盘
        elif req.day == 27:
            special_bonus = 50  # 穿越日
        elif req.day == 30:
            special_bonus = 50  # 封神仪式
        
        # 计算总经验值
        total_xp = base_xp + streak_bonus + week_bonus + special_bonus
        
        # 记录奖励
        reward_id = db.save_reward(
            user_id=req.user_id,
            reward_type="daily",
            reward_name=f"第{req.day}天完成奖励",
            xp_amount=total_xp,
            description=f"基础:{base_xp} + 连续:{streak_bonus} + 周奖励:{week_bonus} + 特殊:{special_bonus}"
        )
        
        # 更新用户经验值
        db.add_user_xp(req.user_id, total_xp)
        
        # 检查徽章
        badges = []
        
        # 检查连续徽章
        if streak >= 7 and not db.has_badge(req.user_id, "persistent_7"):
            db.award_badge(req.user_id, "persistent_7")
            badges.append({"id": "persistent_7", "name": "坚持不懈", "icon": "🔥"})
        
        if streak >= 14 and not db.has_badge(req.user_id, "persistent_14"):
            db.award_badge(req.user_id, "persistent_14")
            badges.append({"id": "persistent_14", "name": "意志坚定", "icon": "💪"})
        
        if streak >= 21 and not db.has_badge(req.user_id, "persistent_21"):
            db.award_badge(req.user_id, "persistent_21")
            badges.append({"id": "persistent_21", "name": "钢铁意志", "icon": "⚔️"})
        
        # 检查周徽章
        if req.day >= 7 and not db.has_badge(req.user_id, "week_1"):
            db.award_badge(req.user_id, "week_1")
            badges.append({"id": "week_1", "name": "初级穿越者", "icon": "🚶"})
        
        if req.day >= 14 and not db.has_badge(req.user_id, "week_2"):
            db.award_badge(req.user_id, "week_2")
            badges.append({"id": "week_2", "name": "中级穿越者", "icon": "🏃"})
        
        if req.day >= 21 and not db.has_badge(req.user_id, "week_3"):
            db.award_badge(req.user_id, "week_3")
            badges.append({"id": "week_3", "name": "高级穿越者", "icon": "🦸"})
        
        if req.day >= 30 and not db.has_badge(req.user_id, "complete"):
            db.award_badge(req.user_id, "complete")
            badges.append({"id": "complete", "name": "封神者", "icon": "👑"})
        
        return {
            "success": True,
            "reward_id": reward_id,
            "xp_breakdown": {
                "base": base_xp,
                "streak_bonus": streak_bonus,
                "week_bonus": week_bonus,
                "special_bonus": special_bonus,
                "total": total_xp
            },
            "badges": badges,
            "message": f"恭喜获得 {total_xp} XP！"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"领取奖励失败: {str(e)}")

@app.get("/api/rewards/{user_id}")
async def get_user_rewards(user_id: str, limit: int = 50):
    """获取用户奖励记录"""
    rewards = db.get_user_rewards(user_id, limit)
    return {
        "user_id": user_id,
        "rewards": rewards,
        "total": len(rewards)
    }

@app.get("/api/badges/{user_id}")
async def get_user_badges(user_id: str):
    """获取用户徽章"""
    badges = db.get_user_badges(user_id)
    return {
        "user_id": user_id,
        "badges": badges,
        "total": len(badges)
    }

@app.get("/api/level/{user_id}")
async def get_user_level(user_id: str):
    """获取用户等级信息"""
    level_info = db.get_user_level(user_id)
    return {
        "user_id": user_id,
        "level_info": level_info
    }

@app.get("/api/badges/all")
async def get_all_badges():
    """获取所有可用徽章"""
    with db._connect() as conn:
        rows = conn.execute("SELECT * FROM badges ORDER BY id").fetchall()
        badges = [dict(row) for row in rows]
    return {
        "badges": badges,
        "total": len(badges)
    }


# ============================================================
# 专家Agent API (已移到 expert_routes.py)
# ============================================================
# 注意：专家API路由已移到 src/api/expert_routes.py
# 包括SecondMe集成、Agent管理等功能
# 路由前缀：/api/experts/


# ============================================================
# 系统 API
# ============================================================

@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "running",
        "service": "窄门 NarrowGate",
        "version": "2.1.0",
        "mimo_connected": True,
        "database": "sqlite",
        "stats": db.get_stats(),
    }


# ============================================================
# 启动
# ============================================================


# ============================================================
# Hermes改进：用户进度追踪（连续天数+里程碑）
# ============================================================

USER_STREAKS = {}

MILESTONES = [
    {"days": 1, "title": "第一次穿越", "emoji": "🚪", "message": "你迈出了第一步。大多数人永远不会开始。"},
    {"days": 3, "title": "三天觉醒", "emoji": "⚡", "message": "三天连续穿越，你的灵魂开始苏醒。"},
    {"days": 7, "title": "一周封印", "emoji": "🔥", "message": "一周不间断。你已经不是一周前的自己了。"},
    {"days": 14, "title": "双周突破", "emoji": "💎", "message": "两周穿越。习惯正在重塑你。"},
    {"days": 21, "title": "习惯固化", "emoji": "🌟", "message": "21天。新的神经通路已经建立。"},
    {"days": 30, "title": "月度封神", "emoji": "👑", "message": "30天完成。你已经穿越了这道窄门。"},
]

@app.get("/api/streak/{user_id}")
async def get_user_streak(user_id: str):
    """获取用户连续训练天数"""
    streak = USER_STREAKS.get(user_id, {"current": 0, "best": 0, "last_date": ""})
    achieved = [m for m in MILESTONES if streak["current"] >= m["days"]]
    next_milestone = next((m for m in MILESTONES if streak["current"] < m["days"]), None)
    return {
        "user_id": user_id,
        "current_streak": streak["current"],
        "best_streak": streak["best"],
        "achieved_milestones": achieved,
        "next_milestone": next_milestone,
        "message": achieved[-1]["message"] if achieved else "开始你的第一次穿越吧。"
    }

@app.post("/api/streak/{user_id}/complete")
async def complete_daily_training(user_id: str):
    """标记今日训练完成，更新连续天数"""
    from datetime import date
    today = date.today().isoformat()
    streak = USER_STREAKS.get(user_id, {"current": 0, "best": 0, "last_date": ""})
    if streak["last_date"] == today:
        return {"message": "今天已经完成了！", "streak": streak}
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    if streak["last_date"] == yesterday:
        streak["current"] += 1
    elif streak["last_date"] != today:
        streak["current"] = 1
    streak["best"] = max(streak["best"], streak["current"])
    streak["last_date"] = today
    USER_STREAKS[user_id] = streak
    milestone = next((m for m in MILESTONES if m["days"] == streak["current"]), None)
    return {
        "streak": streak,
        "milestone": milestone,
        "message": milestone["message"] if milestone else f"连续{streak["current"]}天，继续穿越！"
    }


if __name__ == "__main__":
    import uvicorn
    print("🚪 窄门 NarrowGate v2.0 启动中...")
    print("📍 http://localhost:8090")
    print("🤖 MIMO API: 已集成")
    print("💾 SQLite: 已集成")
    uvicorn.run(app, host="0.0.0.0", port=8090)
