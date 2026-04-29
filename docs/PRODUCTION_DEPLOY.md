# NarrowGate 生产环境部署指南
# 最后更新: 2026-04-19

## 📋 部署清单

### ✅ 已完成 (GitHub)

- [x] 代码推送到 main 分支
- [x] 前端部署到 gh-pages 分支
- [x] 首页改进（社会证明、用户旅程、用户见证）
- [x] 课程体系页面
- [x] 课程理论映射API

### 🔄 待完成 (生产服务器)

- [ ] 登录生产服务器
- [ ] 拉取最新代码
- [ ] 重启后端服务
- [ ] 验证部署结果

---

## 🚀 快速部署（3步完成）

### 方式1: 一键部署脚本

```bash
# 1. SSH到服务器
ssh root@narrowgatemind.top

# 2. 下载并执行部署脚本
cd /root/narrowgate
git pull origin main
chmod +x deploy_production.sh
./deploy_production.sh
```

### 方式2: 手动部署

```bash
# 1. SSH到服务器
ssh root@narrowgatemind.top

# 2. 进入项目目录
cd /root/narrowgate

# 3. 拉取最新代码
git fetch origin
git reset --hard origin/main

# 4. 重启服务
sudo systemctl restart narrowgate

# 5. 验证
curl http://127.0.0.1:8090/health
```

---

## 📍 功能访问地址

部署完成后，以下功能将在正式网址上可用：

### 前端页面

| 页面 | 地址 | 说明 |
|------|------|------|
| 首页 | https://narrowgatemind.top | 主页，包含社会证明、用户旅程 |
| 课程体系 | https://narrowgatemind.top/course-system.html | 30天课程可视化 |

### API端点

| 端点 | 地址 | 说明 |
|------|------|------|
| 健康检查 | https://narrowgatemind.top/health | 服务状态检查 |
| 课程概览 | https://narrowgatemind.top/api/course/overview | 30天课程概览 |
| 课程详情 | https://narrowgatemind.top/api/course/day/1 | 单日课程+理论映射 |
| 灵魂审计 | https://narrowgatemind.top/api/audit/start | 开始灵魂审计 |
| 大师列表 | https://narrowgatemind.top/api/masters | 获取大师列表 |

---

## 🎯 新增功能详情

### 1. 首页改进

**社会证明横幅**:
- ✓ 1,234人已完成灵魂审计
- ⚡ 567人正在穿越窄门
- ⭐ 98%用户表示"看见了真实的自己"

**用户旅程可视化**:
```
1. 灵魂审计 → 2. 发现窄门 → 3. 30天穿越
```

**用户见证**:
- 3位典型用户见证（程序员、心理咨询师、创业者）
- 数据展示：98%推荐率、4.9评分、85%完成率、3x行动力提升

### 2. 课程体系页面

**五维度模型**:
- 🔮 认知 - 苏格拉底
- 🌑 情绪 - 荣格
- ⚡ 行为 - 清醒者
- 🪞 关系 - 镜像者
- 🏗️ 事业 - 架构师

**进化金字塔**:
- L1 睡眠层 → L2 觉醒层 → L3 突破层 → L4 精通层 → L5 神性层

**30天课程详情**:
- 第1周：面对恐惧 (D1-D7)
- 第2周：建立节奏 (D8-D14)
- 第3周：突破瓶颈 (D15-D21)
- 第4周：成为穿越者 (D22-D30)

### 3. 课程理论映射API

**GET /api/course/day/{day}** 返回:
```json
{
    "day": 1,
    "content": {...},
    "theory_mapping": {
        "dimension": "认知",
        "evolution_target": "L1→L2",
        "evasion_detection": "否认模式",
        "theory_reference": "灵魂审计L1：看见问题"
    }
}
```

---

## 🔧 验证部署

### 1. 前端验证

```bash
# 检查首页
curl -I https://narrowgatemind.top

# 检查课程体系页面
curl -I https://narrowgatemind.top/course-system.html
```

### 2. 后端验证

```bash
# 健康检查
curl https://narrowgatemind.top/health

# 预期响应:
# {"status":"ok","service":"narrowgate","version":"2.1.0"}

# 测试课程API
curl https://narrowgatemind.top/api/course/day/1

# 预期响应包含 theory_mapping 字段
```

### 3. 功能验证清单

- [ ] 首页加载正常
- [ ] 社会证明数字动画显示
- [ ] 用户旅程3步卡片显示
- [ ] 用户见证板块显示
- [ ] 课程体系页面加载正常
- [ ] API健康检查返回200
- [ ] 课程API返回理论映射信息

---

## 🛠️ 故障排除

### 问题1: 服务无法启动

```bash
# 查看日志
sudo journalctl -u narrowgate -n 100

# 检查端口占用
sudo lsof -i :8090

# 手动启动测试
cd /root/narrowgate/src/api
python3 main.py
```

### 问题2: 前端页面空白

```bash
# 检查Nginx配置
sudo nginx -t
sudo systemctl status nginx

# 检查文件权限
ls -la /var/www/narrowgate/
sudo chown -R www-data:www-data /var/www/narrowgate/
```

### 问题3: API返回404

```bash
# 确认后端服务运行中
sudo systemctl status narrowgate

# 测试本地访问
curl http://127.0.0.1:8090/health

# 检查Nginx代理配置
sudo nano /etc/nginx/sites-enabled/narrowgate
```

---

## 📝 Nginx配置参考

如果需要配置Nginx反向代理：

```nginx
server {
    listen 80;
    server_name narrowgatemind.top;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name narrowgatemind.top;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 前端静态文件
    location / {
        root /var/www/narrowgate;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8090/health;
    }
}
```

---

## 🔄 回滚方案

如需回滚到之前版本：

```bash
# 1. 进入项目目录
cd /root/narrowgate

# 2. 查看最近提交
git log --oneline -10

# 3. 回滚到指定版本
git checkout <commit-hash>

# 4. 重启服务
sudo systemctl restart narrowgate

# 5. 验证
curl http://127.0.0.1:8090/health
```

---

## 📞 技术支持

如遇问题，请检查：

1. **服务状态**: `sudo systemctl status narrowgate`
2. **服务日志**: `sudo journalctl -u narrowgate -f`
3. **Nginx日志**: `sudo tail -f /var/log/nginx/error.log`
4. **系统资源**: `htop` 或 `free -h`

---

*"不是不知道，是不想做。窄门在等你。"* 🚪
