#!/bin/bash
# 窄门项目部署脚本
# 用于将首页更新推送到GitHub Pages

#!/bin/bash
# 窄门项目部署脚本
# 用于将首页更新推送到GitHub Pages

echo "🚪 窄门 NarrowGate 部署脚本"
echo "================================"

# 确保在main分支
current_branch=$(git branch --show-current)
echo "📍 当前分支: $current_branch"
if [ "$current_branch" != "main" ]; then
    echo "❌ 请在main分支运行此脚本"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 发现未提交的更改，正在提交..."
    git add .
    git commit -m "deploy: 更新首页 $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送main分支
echo "📤 推送main分支..."
git push origin main

# 切换到gh-pages分支
echo "🔄 切换到gh-pages分支..."
git checkout gh-pages

# 从main分支复制index.html
echo "📋 复制首页文件..."
git checkout main -- index.html

# 提交更改
echo "💾 提交gh-pages更改..."
git add index.html
git commit -m "deploy: 更新首页 $(date '+%Y-%m-%d %H:%M:%S')"

# 推送gh-pages分支
echo "📤 推送gh-pages分支..."
git push origin gh-pages

# 切换回main分支
echo "🔄 切换回main分支..."
git checkout main

echo "✅ 部署完成！"
echo "📍 主页: https://narrowgatemind.top"
echo "📍 后端: http://127.0.0.1:8090"

# 重启后端服务（可选）
read -p "🔄 是否重启后端服务？(y/N): " restart_backend
if [ "$restart_backend" = "y" ] || [ "$restart_backend" = "Y" ]; then
    echo "🔄 重启后端服务..."
    pkill -f "python3 src/api/main.py" 2>/dev/null || true
    sleep 2
    python3 src/api/main.py &
    echo "✅ 后端服务已重启"
fi