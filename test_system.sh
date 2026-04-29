#!/bin/bash
# 窄门系统功能测试脚本

echo "🚪 窄门 NarrowGate 系统功能测试"
echo "================================"

BASE_URL="http://localhost:8090"
PASS=0
FAIL=0

test_api() {
    local name=$1
    local endpoint=$2
    local method=$3
    local data=$4
    
    echo -n "测试 $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" -o /tmp/response.json "$BASE_URL$endpoint")
    fi
    
    if [ "$response" = "200" ]; then
        echo "✅ 通过"
        PASS=$((PASS + 1))
    else
        echo "❌ 失败 (HTTP $response)"
        FAIL=$((FAIL + 1))
    fi
}

# 1. 健康检查
test_api "健康检查" "/health" "GET"

# 2. 灵魂审计系统
test_api "开始灵魂审计" "/api/audit/start" "POST" '{"user_id": "test_user"}'

# 3. 大师系统
test_api "获取大师列表" "/api/masters" "GET"

# 4. 课程系统
test_api "获取第1天课程" "/api/course/day/1" "GET"
test_api "获取课程概览" "/api/course/overview" "GET"

# 5. 见证人系统
test_api "添加见证人" "/api/witness/add" "POST" '{"name": "测试见证人", "email": "test@example.com", "relationship": "朋友"}'
test_api "获取见证人列表" "/api/witness/list" "GET"

# 6. 进化系统
test_api "获取进化状态" "/api/evolution/test_user" "GET"

# 7. 穿越系统
test_api "获取穿越计划" "/api/training/plan" "GET"

# 8. 统计信息
test_api "获取统计信息" "/api/stats" "GET"

echo ""
echo "================================"
echo "测试结果："
echo "✅ 通过: $PASS"
echo "❌ 失败: $FAIL"
echo "总计: $((PASS + FAIL))"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo "🎉 所有测试通过！系统功能完整。"
    exit 0
else
    echo ""
    echo "⚠️ 有 $FAIL 个测试失败，请检查。"
    exit 1
fi