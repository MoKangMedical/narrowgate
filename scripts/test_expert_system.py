#!/usr/bin/env python3
"""
窄门专家系统测试脚本
"""

import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from expert_profiles import get_all_experts, get_expert_by_level, get_expert_by_dimension
from expert_agents import ExpertAgentSystem

def test_expert_profiles():
    """测试专家配置"""
    print("=" * 60)
    print("测试1: 专家配置")
    print("=" * 60)
    
    experts = get_all_experts()
    print(f"\n✓ 总专家数: {len(experts)}")
    
    print("\n【五层进化专家】")
    for level in range(1, 6):
        expert = get_expert_by_level(level)
        if expert:
            print(f"  L{level}: {expert['avatar']} {expert['name']} - {expert['title']}")
    
    print("\n【维度专家】")
    dimensions = ["cognitive", "emotional", "behavioral", "relational", "career"]
    for dim in dimensions:
        expert = get_expert_by_dimension(dim)
        if expert:
            print(f"  {dim}: {expert['avatar']} {expert['name']} - {expert['title']}")
    
    return True

def test_agent_creation():
    """测试Agent创建"""
    print("\n" + "=" * 60)
    print("测试2: Agent创建")
    print("=" * 60)
    
    system = ExpertAgentSystem()
    
    # 创建几个测试Agent
    test_cases = [
        ("sleep_expert", "test_user_001"),
        ("cognitive_expert", "test_user_001"),
        ("breakthrough_expert", None)
    ]
    
    for expert_id, user_id in test_cases:
        try:
            agent = system.agent_manager.create_agent(expert_id, user_id)
            print(f"\n✓ 创建Agent: {agent.agent_id}")
            print(f"  专家: {expert_id}")
            print(f"  用户: {user_id or '无'}")
            print(f"  状态: {agent.status}")
        except Exception as e:
            print(f"\n✗ 创建Agent失败: {expert_id}")
            print(f"  错误: {e}")
    
    return True

def test_system_status():
    """测试系统状态"""
    print("\n" + "=" * 60)
    print("测试3: 系统状态")
    print("=" * 60)
    
    system = ExpertAgentSystem()
    status = system.get_system_status()
    
    print(f"\n✓ Agent总数: {status['total_agents']}")
    print(f"✓ 活跃Agent: {status['active_agents']}")
    print(f"✓ SecondMe连接: {'已配置' if status['secondme_connected'] else '未配置'}")
    
    if status['agents']:
        print("\n活跃Agent列表:")
        for agent in status['agents']:
            print(f"  - {agent['agent_id']}")
            print(f"    专家: {agent['expert_id']}")
            print(f"    对话次数: {agent['conversation_count']}")
    
    return True

def test_expert_greetings():
    """测试专家问候语"""
    print("\n" + "=" * 60)
    print("测试4: 专家问候语")
    print("=" * 60)
    
    experts = get_all_experts()
    
    for expert_id, expert in list(experts.items())[:3]:  # 只显示前3个
        print(f"\n【{expert['avatar']} {expert['name']}】")
        print(f"哲学: {expert['philosophy']}")
        print(f"专长: {', '.join(expert['specialties'])}")
        print(f"问候语:")
        print(f"  {expert['greeting'][:100]}...")
    
    return True

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("窄门专家系统测试")
    print("=" * 60)
    
    tests = [
        test_expert_profiles,
        test_agent_creation,
        test_system_status,
        test_expert_greetings
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ 测试失败: {test.__name__}")
            print(f"  错误: {e}")
            results.append((test.__name__, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)