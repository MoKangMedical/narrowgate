"""
窄门专家Agent API路由
处理专家agent管理和SecondMe集成
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import sys
from pathlib import Path

# 添加core模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.expert_agents import ExpertAgentSystem
from core.expert_profiles import EXPERT_PROFILES, DIMENSION_EXPERTS, get_all_experts

router = APIRouter(prefix="/api/experts", tags=["experts"])

# 初始化专家agent系统
expert_system = ExpertAgentSystem()

# ============================================================
# 请求模型
# ============================================================

class CreateAgentRequest(BaseModel):
    expert_id: str
    user_id: Optional[str] = None
    deploy_to_secondme: bool = False

class AgentActionRequest(BaseModel):
    agent_id: str

class ConversationRequest(BaseModel):
    agent_id: str
    user_message: str
    context: Optional[Dict] = None

class SecondMeSyncRequest(BaseModel):
    expert_id: str
    api_key: Optional[str] = None

# ============================================================
# 专家信息端点
# ============================================================

@router.get("/")
async def list_experts():
    """列出所有可用的专家"""
    experts = get_all_experts()
    
    return {
        "success": True,
        "experts": {
            "evolution_levels": [
                {
                    "level": i,
                    "expert_id": f"{['sleep', 'awakening', 'breakthrough', 'mastery', 'divinity'][i-1]}_expert",
                    "name": EXPERT_PROFILES.get(f"{['sleep', 'awakening', 'breakthrough', 'mastery', 'divinity'][i-1]}_expert", {}).get("name"),
                    "title": EXPERT_PROFILES.get(f"{['sleep', 'awakening', 'breakthrough', 'mastery', 'divinity'][i-1]}_expert", {}).get("title"),
                    "avatar": EXPERT_PROFILES.get(f"{['sleep', 'awakening', 'breakthrough', 'mastery', 'divinity'][i-1]}_expert", {}).get("avatar")
                }
                for i in range(1, 6)
            ],
            "dimensions": [
                {
                    "dimension": dim,
                    "expert_id": expert["id"],
                    "name": expert["name"],
                    "title": expert["title"],
                    "avatar": expert["avatar"]
                }
                for dim, expert in DIMENSION_EXPERTS.items()
            ]
        }
    }

@router.get("/{expert_id}")
async def get_expert(expert_id: str):
    """获取专家详细信息"""
    experts = get_all_experts()
    
    if expert_id not in experts:
        raise HTTPException(status_code=404, detail=f"专家 {expert_id} 不存在")
    
    expert = experts[expert_id]
    
    return {
        "success": True,
        "expert": {
            "id": expert["id"],
            "name": expert["name"],
            "title": expert["title"],
            "avatar": expert["avatar"],
            "philosophy": expert["philosophy"],
            "specialties": expert["specialties"],
            "signature_phrases": expert["signature_phrases"],
            "greeting": expert["greeting"],
            "dimension": expert.get("dimension"),
            "level": expert.get("level")
        }
    }

# ============================================================
# Agent管理端点
# ============================================================

@router.post("/agents/create")
async def create_agent(request: CreateAgentRequest):
    """创建专家agent实例"""
    try:
        result = expert_system.setup_expert(
            expert_id=request.expert_id,
            user_id=request.user_id,
            deploy_to_secondme=request.deploy_to_secondme
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建agent失败: {str(e)}")

@router.get("/agents/list")
async def list_agents(user_id: Optional[str] = None):
    """列出所有agents"""
    agents = expert_system.agent_manager.agents
    
    agent_list = []
    for agent_id, agent in agents.items():
        if user_id is None or agent.metadata.get("user_id") == user_id:
            agent_list.append(agent.to_dict())
    
    return {
        "success": True,
        "agents": agent_list,
        "total": len(agent_list)
    }

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取agent详情"""
    agent = expert_system.agent_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} 不存在")
    
    return {
        "success": True,
        "agent": agent.to_dict()
    }

@router.post("/agents/activate")
async def activate_agent(request: AgentActionRequest):
    """激活agent"""
    success = expert_system.agent_manager.activate_agent(request.agent_id)
    
    if success:
        return {"success": True, "message": f"Agent {request.agent_id} 已激活"}
    else:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} 不存在")

@router.post("/agents/deactivate")
async def deactivate_agent(request: AgentActionRequest):
    """停用agent"""
    success = expert_system.agent_manager.deactivate_agent(request.agent_id)
    
    if success:
        return {"success": True, "message": f"Agent {request.agent_id} 已停用"}
    else:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} 不存在")

# ============================================================
# 对话端点
# ============================================================

@router.post("/agents/chat")
async def chat_with_agent(request: ConversationRequest):
    """与专家agent对话"""
    agent = expert_system.agent_manager.get_agent(request.agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} 不存在")
    
    if agent.status != "active":
        raise HTTPException(status_code=400, detail=f"Agent {request.agent_id} 未激活")
    
    # 获取专家配置
    experts = get_all_experts()
    expert = experts.get(agent.expert_id)
    
    if not expert:
        raise HTTPException(status_code=400, detail=f"专家配置 {agent.expert_id} 不存在")
    
    # 记录对话
    expert_system.record_conversation(request.agent_id)
    
    # 如果有SecondMe agent ID，转发到SecondMe
    if agent.secondme_agent_id:
        # TODO: 实现SecondMe对话转发
        pass
    
    # 返回专家响应（实际应该调用AI模型）
    response = {
        "success": True,
        "agent_id": request.agent_id,
        "expert_name": expert["name"],
        "expert_avatar": expert["avatar"],
        "response": f"[{expert['name']}]: 这是一个示例响应。在完整实现中，这里会调用AI模型生成回复。",
        "signature_phrases": expert["signature_phrases"],
        "conversation_count": agent.conversation_count
    }
    
    return response

# ============================================================
# SecondMe集成端点
# ============================================================

@router.post("/secondme/sync")
async def sync_to_secondme(request: SecondMeSyncRequest):
    """同步专家到SecondMe"""
    if request.api_key:
        expert_system.secondme.api_key = request.api_key
        expert_system.secondme.headers["Authorization"] = f"Bearer {request.api_key}"
    
    result = expert_system.secondme.sync_expert(request.expert_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result)

@router.post("/secondme/deploy/{agent_id}")
async def deploy_to_secondme(agent_id: str):
    """部署agent到SecondMe"""
    agent = expert_system.agent_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} 不存在")
    
    result = expert_system.secondme.deploy_agent(agent)
    
    if result["success"]:
        agent.secondme_agent_id = result.get("secondme_agent_id")
        expert_system.agent_manager._save_agents()
        return result
    else:
        raise HTTPException(status_code=400, detail=result)

@router.post("/secondme/bridge")
async def create_secondme_bridge(agent_id: str, user_id: str):
    """创建SecondMe对话桥接"""
    result = expert_system.secondme.create_conversation_bridge(agent_id, user_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result)

# ============================================================
# 系统状态端点
# ============================================================

@router.get("/system/status")
async def get_system_status():
    """获取专家系统状态"""
    status = expert_system.get_system_status()
    return {
        "success": True,
        "status": status
    }

@router.get("/system/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "experts_available": len(get_all_experts()),
        "agents_active": len(expert_system.agent_manager.get_active_agents())
    }