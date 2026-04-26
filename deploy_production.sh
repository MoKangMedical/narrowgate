#!/bin/bash
# NarrowGate 生产环境部署脚本
# 使用方法: 在服务器上执行此脚本

set -e

echo "=========================================="
echo "🚀 NarrowGate 生产环境部署"
echo "=========================================="
echo ""

# 配置
SERVER_IP="narrowgatemind.top"
PROJECT_DIR="/root/narrowgate"
SERVICE_NAME="narrowgate"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 步骤1: 进入项目目录
print_info "步骤1: 进入项目目录"
cd $PROJECT_DIR || { print_error "项目目录不存在: $PROJECT_DIR"; exit 1; }
print_success "已进入项目目录"

# 步骤2: 拉取最新代码
print_info "步骤2: 拉取最新代码"
git fetch origin
git reset --hard origin/main
print_success "代码已更新到最新版本"

# 步骤3: 安装/更新依赖
print_info "步骤3: 检查依赖"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_success "依赖已安装"
else
    print_info "未找到requirements.txt，跳过依赖安装"
fi

# 步骤4: 复制前端文件到web目录
print_info "步骤4: 部署前端文件"
WEB_DIR="/var/www/narrowgate"
if [ -d "$WEB_DIR" ]; then
    cp index.html $WEB_DIR/
    cp course-system.html $WEB_DIR/ 2>/dev/null || true
    print_success "前端文件已部署到 $WEB_DIR"
else
    print_info "Web目录不存在，使用项目根目录的index.html"
fi

# 步骤5: 重启后端服务
print_info "步骤5: 重启后端服务"
if systemctl is-active --quiet $SERVICE_NAME; then
    sudo systemctl restart $SERVICE_NAME
    print_success "服务已重启"
else
    print_info "服务未运行，尝试启动..."
    sudo systemctl start $SERVICE_NAME
    print_success "服务已启动"
fi

# 步骤6: 等待服务启动
print_info "步骤6: 等待服务启动"
sleep 3

# 步骤7: 健康检查
print_info "步骤7: 执行健康检查"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8090/health || echo "000")
if [ "$HEALTH_CHECK" = "200" ]; then
    print_success "健康检查通过 ✓"
    curl -s http://127.0.0.1:8090/health | python3 -m json.tool
else
    print_error "健康检查失败 (HTTP $HEALTH_CHECK)"
    echo "请检查服务日志: sudo journalctl -u $SERVICE_NAME -n 50"
fi

# 步骤8: 检查服务状态
print_info "步骤8: 检查服务状态"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "=========================================="
echo "✨ 部署完成！"
echo "=========================================="
echo ""
echo "🌐 访问地址:"
echo "   首页: https://$SERVER_IP"
echo "   课程体系: https://$SERVER_IP/course-system.html"
echo ""
echo "📊 API端点:"
echo "   健康检查: https://$SERVER_IP/health"
echo "   课程概览: https://$SERVER_IP/api/course/overview"
echo "   课程详情: https://$SERVER_IP/api/course/day/1"
echo ""
echo "📝 常用命令:"
echo "   查看日志: sudo journalctl -u $SERVICE_NAME -f"
echo "   重启服务: sudo systemctl restart $SERVICE_NAME"
echo "   查看状态: sudo systemctl status $SERVICE_NAME"
echo ""
