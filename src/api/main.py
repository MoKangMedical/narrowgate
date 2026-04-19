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

# ============================================================
# App
# ============================================================

app = FastAPI(
    title="窄门 NarrowGate",
    description="让人看见窄门并跨越窄门的进化平台",
    version="2.1.0",
)

# 核心引擎
audit_engine = SoulAuditEngine()
gate_finder = GateFinder()
crossing_engine = CrossingEngine()
master_manager = MasterManager()
db = Database()
mimo = MIMOClient()
witness_network = WitnessNetwork()
evolution_pyramid = EvolutionPyramid()

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
# 专家Agent API
# ============================================================

from core.expert_agents import ExpertManager

expert_manager = ExpertManager()


class ExpertChatRequest(BaseModel):
    expert_id: str
    message: str
    conversation_id: str = ""


@app.get("/api/experts")
async def get_experts():
    """获取所有专家列表"""
    return {"experts": expert_manager.get_all_experts()}


@app.get("/api/experts/{expert_id}")
async def get_expert_detail(expert_id: str):
    """获取专家详情"""
    expert = expert_manager.get_expert_detail(expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="专家不存在")
    return expert


@app.post("/api/experts/chat")
async def chat_with_expert(req: ExpertChatRequest):
    """与专家对话"""
    return expert_manager.chat(req.expert_id, req.message, req.conversation_id)


@app.get("/api/experts/{expert_id}/cases")
async def get_expert_cases(expert_id: str):
    """获取专家的案例列表"""
    cases = expert_manager.get_expert_cases(expert_id)
    if not cases:
        raise HTTPException(status_code=404, detail="专家不存在")
    return {"expert_id": expert_id, "cases": cases}


@app.get("/api/experts/domain/{domain}")
async def get_domain_experts(domain: str):
    """获取特定领域的专家"""
    return {"domain": domain, "experts": expert_manager.get_domain_experts(domain)}


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

if __name__ == "__main__":
    import uvicorn
    print("🚪 窄门 NarrowGate v2.0 启动中...")
    print("📍 http://localhost:8090")
    print("🤖 MIMO API: 已集成")
    print("💾 SQLite: 已集成")
    uvicorn.run(app, host="0.0.0.0", port=8090)
