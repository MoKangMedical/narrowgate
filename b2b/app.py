"""窄门 NarrowGate — B2B2C 机构付费模式"""
from flask import Flask, render_template_string, render_template, jsonify, request
import json, os, hashlib, time
from datetime import datetime

app = Flask(__name__, template_folder="templates")
DB_FILE = os.path.join(os.path.dirname(__file__), "institution_billing.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f: return json.load(f)
    return {"institutions": {}, "students": [], "revenue": 0}

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, ensure_ascii=False, indent=2)

@app.before_request
def ensure_db():
    if not hasattr(app, '_db'):
        app._db = load_db()

def get_db(): return app._db
def commit(): save_db(app._db)

PLANS = {
    "small": {"name": "小班版", "max_students": 30, "price_per_student": 100, "price_monthly": 500},
    "standard": {"name": "标准版", "max_students": 100, "price_per_student": 80, "price_monthly": 3000},
    "enterprise": {"name": "机构版", "max_students": -1, "price_per_student": 50, "price_monthly": 15000},
}

TARGET_CUSTOMERS = [
    {"type": "心理咨询机构", "need": "来访者自助成长工具", "budget": "5-20万/年"},
    {"type": "灵性培训机构", "need": "课程辅助AI引导师", "budget": "3-15万/年"},
    {"type": "企业EAP服务商", "need": "员工心理健康工具", "budget": "10-50万/年"},
    {"type": "高校心理中心", "need": "学生心理健康平台", "budget": "5-30万/年"},
    {"type": "在线教育平台", "need": "灵性成长课程AI助教", "budget": "5-25万/年"},
]

@app.route("/")
def index():
    return render_template_string("""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>窄门 NarrowGate — 机构合作</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,sans-serif;background:#f5f7fa;color:#333;max-width:800px;margin:0 auto;padding:20px}
.hdr{background:linear-gradient(135deg,#ff6f00,#e65100);color:#fff;padding:24px;border-radius:14px;text-align:center;margin-bottom:20px}
.hdr h1{font-size:22px}.hdr p{font-size:13px;opacity:.8;margin-top:6px}
.hdr nav{margin-top:10px;display:flex;gap:8px;justify-content:center}
.hdr nav a{color:rgba(255,255,255,.85);font-size:12px;padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.15);text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
.card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.05);text-align:center}
.card.popular{border:2px solid #ff6f00;position:relative}
.card.popular::before{content:'推荐';position:absolute;top:-10px;right:16px;background:#ff6f00;color:#fff;font-size:11px;padding:2px 10px;border-radius:8px}
.card h3{font-size:16px;margin-bottom:8px}
.card .price{font-size:28px;font-weight:800;color:#e65100}
.card .unit{font-size:12px;color:#888}
.card .features{text-align:left;font-size:13px;line-height:2;margin:12px 0}
.card .btn{display:block;width:100%;padding:10px;background:#ff6f00;color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer}
.section{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.05);margin-bottom:20px}
.section h2{font-size:15px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #eee}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px;font-size:13px;border-bottom:1px solid #f0f0f0}
th{background:#fafafa}
.tag{display:inline-block;padding:3px 10px;border-radius:10px;font-size:11px;background:#fff3e0;color:#e65100}
.roi{background:#fff8e1;border-radius:10px;padding:14px;margin-top:10px}
.roi .big{font-size:28px;font-weight:800;color:#ff6f00}
input{width:100%;padding:8px;border:1px solid #ddd;border-radius:8px;margin:4px 0 8px}
.btn-main{padding:10px 20px;background:#ff6f00;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px}
</style></head><body>
<div class="hdr">
  <h1>🚪 窄门 NarrowGate</h1>
  <p>"引到永生，那门是窄的" — AI灵性引导平台 · 机构合作方案</p>
<nav><a href="/">🏢 机构合作</a><a href="/student">🚪 学员体验</a></nav>
</div>

<div class="section">
  <h2>🎯 越狱思维：用户用，机构付</h2>
  <p style="font-size:13px;color:#555;line-height:1.8">
    Parakeet Chat：囚犯用 → 家属付$15/月<br>
    NarrowGate：学员用 → 培训机构付¥80-100/人/月<br><br>
    学员免费获得AI灵性引导（苏格拉底对话/灵魂拷问/30天穿越训练），<br>
    培训机构通过AI工具提升课程价值，按学员数付费。
  </p>
</div>

<div class="grid">
{% for k,v in plans.items() %}
<div class="card {{ 'popular' if k=='standard' else '' }}">
  <h3>{{ v.name }}</h3>
  <div><span class="price">¥{% if v.max_students > 0 %}{{ v.price_per_student }}{% else %}{{ v.price_monthly }}{% endif %}</span><span class="unit">{% if v.max_students > 0 %}/人/月{% else %}/月{% endif %}</span></div>
  <div class="features">
    {% if v.max_students > 0 %}最多{{ v.max_students }}名学员{% else %}不限学员数{% endif %}<br>
    苏格拉底AI对话<br>
    灵魂拷问系统<br>
    30天穿越训练<br>
    学员进度追踪<br>
    机构管理后台<br>
    {% if k=='enterprise' %}专属客户经理<br>定制化开发{% endif %}
  </div>
  <button class="btn" onclick="apply('{{ k }}')">申请合作</button>
</div>
{% endfor %}
</div>

<div class="section">
  <h2>🏢 目标客户</h2>
  <table>
    <tr><th>类型</th><th>需求</th><th>预算</th></tr>
    {% for c in customers %}
    <tr><td>{{ c.type }}</td><td>{{ c.need }}</td><td><span class="tag">{{ c.budget }}</span></td></tr>
    {% endfor %}
  </table>
</div>

<div class="section">
  <h2>💰 ROI计算器（100人培训机构）</h2>
  <div class="roi">
    <div style="font-size:13px;color:#555;line-height:2">
      机构年费：100人 × ¥80/人/月 × 12 = <strong>¥96,000</strong><br>
      学员续费率提升：+20%（AI工具提升课程价值）<br>
      新增学员：+30人/年（AI引流+口碑）<br>
      额外收入：30人 × ¥5,000/人（课程费）= <strong>¥150,000</strong>
    </div>
    <div style="text-align:center;margin-top:10px">
      <div style="font-size:12px;color:#888">年净收益</div>
      <div class="big">¥54,000</div>
      <div style="font-size:12px;color:#888">ROI 1.6x（首年），第二年起 ROI 3x+</div>
    </div>
  </div>
</div>

<div class="section">
  <h2>📋 申请合作</h2>
  <label>机构名称</label>
  <input id="instName" placeholder="输入机构名称">
  <label>机构类型</label>
  <select id="instType">
    <option>心理咨询机构</option><option>灵性培训机构</option><option>企业EAP服务商</option>
    <option>高校心理中心</option><option>在线教育平台</option>
  </select>
  <label>预计学员数</label>
  <input id="instCount" type="number" value="50" min="10">
  <button class="btn-main" onclick="applyInst()">提交申请</button>
  <div id="result" style="display:none;margin-top:12px;padding:12px;background:#e8f5e9;border-radius:8px;font-size:13px"></div>
</div>

<script>
function apply(plan){alert('已选择 '+plan+' 方案，请填写下方申请表单')}
async function applyInst(){
  const name=document.getElementById('instName').value;
  const type=document.getElementById('instType').value;
  const count=parseInt(document.getElementById('instCount').value);
  if(!name){alert('请输入机构名称');return;}
  const res=await fetch('/api/apply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,type,count})});
  const data=await res.json();
  document.getElementById('result').style.display='block';
  document.getElementById('result').innerHTML=`✅ 申请已提交！<br>机构：${data.name}<br>方案：${data.plan}<br>月费：¥${data.monthly_fee.toLocaleString()}<br>我们的合作顾问将在24小时内联系您。`;
}
</script>
</body></html>""", plans=PLANS, customers=TARGET_CUSTOMERS)

@app.route("/api/apply", methods=["POST"])
def api_apply():
    data = request.json
    name = data.get("name", "")
    count = data.get("count", 50)
    plan_key = "small" if count <= 30 else ("standard" if count <= 100 else "enterprise")
    plan = PLANS[plan_key]
    monthly = count * plan["price_per_student"] if plan_key != "enterprise" else plan["price_monthly"]
    
    db = get_db()
    inst_id = f"NG{int(time.time())}"
    db["institutions"][inst_id] = {"name": name, "plan": plan_key, "students": count, "monthly_fee": monthly, "created": datetime.now().isoformat()}
    commit()
    return jsonify({"id": inst_id, "name": name, "plan": plan["name"], "monthly_fee": monthly, "annual_fee": monthly * 12})

@app.route("/api/plans")
def api_plans():
    return jsonify(PLANS)

@app.route("/api/stats")
def api_stats():
    db = get_db()
    return jsonify({"institutions": len(db["institutions"]), "total_revenue": db.get("revenue", 0)})

@app.route("/student")
def student():
    return render_template("student_portal.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
