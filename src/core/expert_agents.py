"""
窄门专家Agent管理器
管理专家agent的生命周期和SecondMe集成
"""

import json
import os
import sys
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# 添加core模块到路径
sys.path.insert(0, str(os.path.dirname(__file__)))

# 导入专家配置
from expert_profiles import EXPERT_PROFILES, DIMENSION_EXPERTS, SECONDFME_CONFIG, prepare_secondme_payload

@dataclass
class AgentInstance:
    """Agent实例"""
    agent_id: str
    expert_id: str
    status: str  # active, inactive, deploying, error
    created_at: str
    last_active: Optional[str] = None
    conversation_count: int = 0
    secondme_agent_id: Optional[str] = None
    metadata: Dict = None
    
    def to_dict(self):
        return asdict(self)

class ExpertAgentManager:
    """专家Agent管理器"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/Desktop/narrowgate/data/agents")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.agents_file = os.path.join(self.data_dir, "agents.json")
        self.agents: Dict[str, AgentInstance] = {}
        
        self._load_agents()
    
    def _load_agents(self):
        """加载已存在的agents"""
        if os.path.exists(self.agents_file):
            try:
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_id, agent_data in data.items():
                        self.agents[agent_id] = AgentInstance(**agent_data)
            except Exception as e:
                print(f"加载agents失败: {e}")
    
    def _save_agents(self):
        """保存agents"""
        data = {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()}
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_agent(self, expert_id: str, user_id: str = None) -> AgentInstance:
        """创建新的agent实例"""
        # 检查专家是否存在
        all_experts = {**EXPERT_PROFILES, **DIMENSION_EXPERTS}
        if expert_id not in all_experts:
            raise ValueError(f"专家 {expert_id} 不存在")
        
        # 生成agent_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        agent_id = f"{expert_id}_{timestamp}"
        
        if user_id:
            agent_id = f"{user_id}_{agent_id}"
        
        # 创建agent实例
        agent = AgentInstance(
            agent_id=agent_id,
            expert_id=expert_id,
            status="inactive",
            created_at=datetime.now().isoformat(),
            metadata={"user_id": user_id} if user_id else {}
        )
        
        self.agents[agent_id] = agent
        self._save_agents()
        
        print(f"✓ 创建Agent: {agent_id}")
        return agent
    
    def activate_agent(self, agent_id: str) -> bool:
        """激活agent"""
        if agent_id not in self.agents:
            print(f"✗ Agent {agent_id} 不存在")
            return False
        
        agent = self.agents[agent_id]
        agent.status = "active"
        agent.last_active = datetime.now().isoformat()
        
        self._save_agents()
        print(f"✓ 激活Agent: {agent_id}")
        return True
    
    def deactivate_agent(self, agent_id: str) -> bool:
        """停用agent"""
        if agent_id not in self.agents:
            print(f"✗ Agent {agent_id} 不存在")
            return False
        
        agent = self.agents[agent_id]
        agent.status = "inactive"
        
        self._save_agents()
        print(f"✓ 停用Agent: {agent_id}")
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """获取agent"""
        return self.agents.get(agent_id)
    
    def get_agents_by_expert(self, expert_id: str) -> List[AgentInstance]:
        """获取某专家的所有agents"""
        return [agent for agent in self.agents.values() if agent.agent_id.startswith(expert_id)]
    
    def get_active_agents(self) -> List[AgentInstance]:
        """获取所有活跃的agents"""
        return [agent for agent in self.agents.values() if agent.status == "active"]
    
    def increment_conversation(self, agent_id: str):
        """增加对话计数"""
        if agent_id in self.agents:
            self.agents[agent_id].conversation_count += 1
            self.agents[agent_id].last_active = datetime.now().isoformat()
            self._save_agents()

class SecondMeConnector:
    """SecondMe平台连接器"""
    
    def __init__(self, api_key: str = None):
        self.api_endpoint = SECONDFME_CONFIG["api_endpoint"]
        self.api_key = api_key or os.environ.get("SECONDFME_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {"Content-Type": "application/json"}
    
    def sync_expert(self, expert_id: str) -> Dict:
        """同步专家到SecondMe"""
        payload = prepare_secondme_payload(expert_id)
        
        if not payload:
            return {"success": False, "error": f"专家 {expert_id} 不存在"}
        
        try:
            endpoint = f"{self.api_endpoint}/experts/sync"
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"同步失败: {response.status_code}", "details": response.text}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"连接失败: {str(e)}"}
    
    def deploy_agent(self, agent: AgentInstance) -> Dict:
        """部署agent到SecondMe"""
        payload = {
            "agent_id": agent.agent_id,
            "expert_id": agent.expert_id,
            "config": SECONDFME_CONFIG["agent_deployment_config"],
            "metadata": agent.metadata or {}
        }
        
        try:
            endpoint = f"{self.api_endpoint}/agents/deploy"
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "secondme_agent_id": result.get("agent_id")}
            else:
                return {"success": False, "error": f"部署失败: {response.status_code}", "details": response.text}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"连接失败: {str(e)}"}
    
    def create_conversation_bridge(self, agent_id: str, user_id: str) -> Dict:
        """创建对话桥接"""
        payload = {
            "agent_id": agent_id,
            "user_id": user_id,
            "platform": "narrowgate",
            "bridge_type": "full"
        }
        
        try:
            endpoint = f"{self.api_endpoint}/conversations/bridge"
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "bridge_data": response.json()}
            else:
                return {"success": False, "error": f"桥接失败: {response.status_code}", "details": response.text}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"连接失败: {str(e)}"}
    
    def get_conversation_history(self, agent_id: str, limit: int = 50) -> Dict:
        """获取对话历史"""
        try:
            endpoint = f"{self.api_endpoint}/agents/{agent_id}/conversations"
            params = {"limit": limit}
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "conversations": response.json()}
            else:
                return {"success": False, "error": f"获取失败: {response.status_code}"}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"连接失败: {str(e)}"}

class ExpertAgentSystem:
    """完整的专家Agent系统"""
    
    def __init__(self, data_dir: str = None, secondme_api_key: str = None):
        self.agent_manager = ExpertAgentManager(data_dir)
        self.secondme = SecondMeConnector(secondme_api_key)
    
    def setup_expert(self, expert_id: str, user_id: str = None, deploy_to_secondme: bool = False) -> Dict:
        """完整设置专家agent"""
        results = {
            "expert_id": expert_id,
            "steps": []
        }
        
        # 1. 创建本地agent
        try:
            agent = self.agent_manager.create_agent(expert_id, user_id)
            results["agent_id"] = agent.agent_id
            results["steps"].append({"step": "create_agent", "success": True})
        except Exception as e:
            results["steps"].append({"step": "create_agent", "success": False, "error": str(e)})
            return results
        
        # 2. 激活agent
        if self.agent_manager.activate_agent(agent.agent_id):
            results["steps"].append({"step": "activate_agent", "success": True})
        else:
            results["steps"].append({"step": "activate_agent", "success": False})
        
        # 3. 同步到SecondMe（可选）
        if deploy_to_secondme:
            sync_result = self.secondme.sync_expert(expert_id)
            results["steps"].append({"step": "sync_expert", **sync_result})
            
            if sync_result.get("success"):
                deploy_result = self.secondme.deploy_agent(agent)
                results["steps"].append({"step": "deploy_agent", **deploy_result})
                
                if deploy_result.get("success"):
                    agent.secondme_agent_id = deploy_result.get("secondme_agent_id")
                    self.agent_manager._save_agents()
        
        results["success"] = all(step.get("success", False) for step in results["steps"])
        return results
    
    def get_expert_agent(self, expert_id: str, user_id: str = None) -> Optional[AgentInstance]:
        """获取或创建专家agent"""
        # 先查找现有的活跃agent
        agents = self.agent_manager.get_agents_by_expert(expert_id)
        
        for agent in agents:
            if agent.status == "active":
                if user_id is None or agent.metadata.get("user_id") == user_id:
                    return agent
        
        # 如果没有找到，创建新的
        return self.agent_manager.create_agent(expert_id, user_id)
    
    def record_conversation(self, agent_id: str):
        """记录对话"""
        self.agent_manager.increment_conversation(agent_id)
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        active_agents = self.agent_manager.get_active_agents()
        
        return {
            "total_agents": len(self.agent_manager.agents),
            "active_agents": len(active_agents),
            "agents": [agent.to_dict() for agent in active_agents],
            "secondme_connected": self.secondme.api_key is not None
        }

# CLI接口
def main():
    """命令行接口"""
    import sys
    
    system = ExpertAgentSystem()
    
    if len(sys.argv) < 2:
        print("用法: python expert_agents.py <command> [args]")
        print("\n命令:")
        print("  list                    - 列出所有专家")
        print("  create <expert_id>      - 创建专家agent")
        print("  status                  - 查看系统状态")
        print("  activate <agent_id>     - 激活agent")
        print("  deactivate <agent_id>   - 停用agent")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print("=== 窄门理论顶级专家 ===\n")
        print("【五层进化专家】")
        for level in range(1, 6):
            expert_id = f"{['sleep', 'awakening', 'breakthrough', 'mastery', 'divinity'][level-1]}_expert"
            from expert_profiles import get_expert_by_level
            expert = get_expert_by_level(level)
            if expert:
                print(f"  L{level}: {expert['id']} - {expert['avatar']} {expert['name']}")
        
        print("\n【维度专家】")
        from expert_profiles import DIMENSION_EXPERTS
        for dim, expert in DIMENSION_EXPERTS.items():
            print(f"  {dim}: {expert['id']} - {expert['avatar']} {expert['name']}")
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("用法: python expert_agents.py create <expert_id>")
            return
        
        expert_id = sys.argv[2]
        user_id = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = system.setup_expert(expert_id, user_id, deploy_to_secondme=False)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "status":
        status = system.get_system_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("用法: python expert_agents.py activate <agent_id>")
            return
        
        agent_id = sys.argv[2]
        system.agent_manager.activate_agent(agent_id)
    
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("用法: python expert_agents.py deactivate <agent_id>")
            return
        
        agent_id = sys.argv[2]
        system.agent_manager.deactivate_agent(agent_id)
    
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()