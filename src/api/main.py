"""
窄门 (NarrowGate) — API服务

FastAPI后端，提供灵魂审计、窄门识别、穿越训练的完整接口。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.soul_audit import SoulAuditEngine, SoulAudit
from core.gate_finder import GateFinder
from core.crossing import CrossingEngine

# ============================================================
# App初始化
# ============================================================

app = FastAPI(
    title="窄门 NarrowGate",
    description="让人看见窄门并跨越窄门的进化平台",
    version="0.1.0",
)

# 核心引擎
audit_engine = SoulAuditEngine()
gate_finder = GateFinder()
crossing_engine = CrossingEngine()

# 内存存储（MVP阶段，后续换PostgreSQL）
audits_store: dict = {}
crossings_store: dict = {}


# ============================================================
# Pydantic Models
# ============================================================

class StartAuditRequest(BaseModel):
    user_id: str = "anonymous"


class SubmitAnswerRequest(BaseModel):
    audit_id: str
    answer: str


class StartCrossingRequest(BaseModel):
    audit_id: str
    gate_index: int = 0  # 默认选第一个窄门


class CompleteChallengeRequest(BaseModel):
    gate_id: str
    response: str
    witness: bool = False


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


# ============================================================
# 灵魂审计 API
# ============================================================

@app.post("/api/audit/start")
async def start_audit(req: StartAuditRequest):
    """开始灵魂审计"""
    audit = audit_engine.create_audit(req.user_id)
    audits_store[audit.id] = audit

    # 获取第一个问题
    question = audit_engine.get_next_question(audit)

    return {
        "audit_id": audit.id,
        "status": "in_progress",
        "dimension": audit.current_dimension,
        "question": question.question,
        "depth_level": question.depth_level,
        "purpose": question.purpose,
    }


@app.post("/api/audit/answer")
async def submit_answer(req: SubmitAnswerRequest):
    """提交审计回答"""
    audit = audits_store.get(req.audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="审计不存在")

    # 处理回答
    response = audit_engine.process_response(audit, req.answer)

    # 获取下一个问题
    next_question = audit_engine.get_next_question(audit)

    result = {
        "evasion_detected": response.evasion_detected,
        "evasion_type": response.evasion_type,
        "ai_analysis": response.ai_analysis,
        "shackles_found": len(audit.shackle_map),
        "next_question": next_question.question,
        "next_depth": next_question.depth_level,
        "dimension": audit.current_dimension,
        "conversation_count": len(audit.conversation),
    }

    return result


@app.post("/api/audit/complete")
async def complete_audit(req: StartAuditRequest):
    """完成灵魂审计（用audit_id作为user_id来找）"""
    # 查找进行中的审计
    audit = None
    for a in audits_store.values():
        if a.user_id == req.user_id and a.status == "in_progress":
            audit = a
            break

    if not audit:
        raise HTTPException(status_code=404, detail="没有进行中的审计")

    report = audit_engine.complete_audit(audit)
    return report


@app.get("/api/audit/{audit_id}")
async def get_audit(audit_id: str):
    """获取审计详情"""
    audit = audits_store.get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="审计不存在")
    return audit.to_dict()


@app.get("/api/audit/{audit_id}/gates")
async def get_gates(audit_id: str):
    """获取窄门候选"""
    audit = audits_store.get(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="审计不存在")

    gates = gate_finder.find_gates(audit)
    report = gate_finder.generate_gate_report(gates)
    return report


# ============================================================
# 穿越训练 API
# ============================================================

@app.post("/api/crossing/start")
async def start_crossing(req: StartCrossingRequest):
    """开始穿越窄门"""
    audit = audits_store.get(req.audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="审计不存在")

    gates = gate_finder.find_gates(audit)
    if not gates:
        raise HTTPException(status_code=404, detail="没有找到窄门")

    if req.gate_index >= len(gates):
        raise HTTPException(status_code=400, detail="窄门索引超出范围")

    gate = gates[req.gate_index]
    progress = crossing_engine.start_crossing(gate)
    crossings_store[gate.id] = {"progress": progress, "gate": gate}

    # 生成第一天的挑战
    challenge = crossing_engine.generate_daily_challenge(gate, 0)

    return {
        "gate": {
            "id": gate.id,
            "name": gate.name,
            "description": gate.description,
            "narrow_gate_path": gate.narrow_gate_path,
        },
        "today_challenge": {
            "id": challenge.id,
            "challenge": challenge.challenge,
            "difficulty": challenge.difficulty,
        },
        "progress": crossing_engine.get_progress_report(progress),
    }


@app.post("/api/crossing/complete")
async def complete_challenge(req: CompleteChallengeRequest):
    """完成今日挑战"""
    crossing = crossings_store.get(req.gate_id)
    if not crossing:
        raise HTTPException(status_code=404, detail="穿越记录不存在")

    gate = crossing["gate"]
    progress = crossing["progress"]

    # 生成今天的挑战（用于记录）
    challenge = crossing_engine.generate_daily_challenge(gate, progress.current_day)

    # 记录完成
    record = crossing_engine.record_challenge_completion(
        progress, challenge, req.response, req.witness
    )

    # 生成明天的挑战
    next_challenge = crossing_engine.generate_daily_challenge(
        gate, progress.current_day
    )

    return {
        "completed": True,
        "today_record": {
            "action": record.action,
            "reality_after": record.reality_after,
        },
        "tomorrow_challenge": {
            "challenge": next_challenge.challenge,
            "difficulty": next_challenge.difficulty,
        },
        "progress": crossing_engine.get_progress_report(progress),
    }


@app.get("/api/crossing/{gate_id}/progress")
async def get_crossing_progress(gate_id: str):
    """获取穿越进度"""
    crossing = crossings_store.get(gate_id)
    if not crossing:
        raise HTTPException(status_code=404, detail="穿越记录不存在")

    return crossing_engine.get_progress_report(crossing["progress"])


# ============================================================
# 系统 API
# ============================================================

@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "running",
        "service": "窄门 NarrowGate",
        "version": "0.1.0",
        "active_audits": len([a for a in audits_store.values() if a.status == "in_progress"]),
        "active_crossings": len(crossings_store),
    }


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("🚪 窄门 NarrowGate 启动中...")
    print("📍 http://localhost:8090")
    uvicorn.run(app, host="0.0.0.0", port=8090)
