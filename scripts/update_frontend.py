cd /root/narrowgate/src/ui
python3 << 'PYEOF'
with open("index.html", "r") as f:
    lines = f.readlines()

# Find renderMasters(); line
insert_idx = None
for i, line in enumerate(lines):
    if "renderMasters();" in line:
        insert_idx = i
        break

if insert_idx is None:
    print("ERROR: Can't find renderMasters();")
    exit(1)

# Insert witness and evolution JS after renderMasters
js_additions = '''

        // ============================================================
        // Witness Network
        // ============================================================
        async function addWitness() {
            const name = document.getElementById('witness-name').value.trim();
            if (!name) { alert('请输入见证人姓名'); return; }
            const email = document.getElementById('witness-email').value.trim();
            const rel = document.getElementById('witness-relationship').value;
            try {
                await apiCall('/api/witness/add', 'POST', { name, email, relationship: rel });
                alert(name + ' 已添加为见证人！');
                loadWitnesses();
                document.getElementById('witness-name').value = '';
            } catch(e) { alert('添加失败'); }
        }
        async function loadWitnesses() {
            try {
                const list = await apiCall('/api/witness/list', 'GET');
                const el = document.getElementById('witness-list');
                if (!list.length) { el.innerHTML = '<p class="text-gray-500 text-sm">还没有添加见证人</p>'; return; }
                el.innerHTML = list.map(w => '<div class="bg-[#12121a] border border-white/5 rounded-lg p-4 flex items-center justify-between"><div><p class="font-semibold">' + w.name + '</p><p class="text-xs text-gray-500">' + w.relationship + '</p></div><span class="text-xs ' + (w.verified ? 'text-green-400' : 'text-gray-500') + '">' + (w.verified ? '已验证' : '待验证') + '</span></div>').join('');
            } catch(e) {}
        }

        // ============================================================
        // Evolution Pyramid
        // ============================================================
        async function loadEvolution() {
            try {
                const data = await apiCall('/api/evolution/demo', 'GET');
                if (data.levels) {
                    const cur = data.levels.find(l => l.is_current) || data.levels[0];
                    const el = document.getElementById('evolution-level');
                    if (el) el.innerHTML = '<p class="text-2xl mb-2">' + cur.emoji + ' ' + cur.name + '</p><p class="text-gray-400 text-sm">' + cur.description + '</p>';
                }
            } catch(e) {}
        }

        loadWitnesses();
        loadEvolution();
'''

lines.insert(insert_idx + 1, js_additions)

# Now add HTML sections before </body>
body_idx = None
for i, line in enumerate(lines):
    if "</body>" in line:
        body_idx = i
        break

html_additions = '''
    <!-- Witness Network Section -->
    <section id="section-witness" class="py-20 px-6">
        <div class="max-w-4xl mx-auto">
            <h2 class="font-serif text-3xl font-bold mb-4 text-center">见证人网络</h2>
            <p class="text-gray-400 text-center mb-12">你的进化需要被看见。</p>
            <div class="grid md:grid-cols-2 gap-8">
                <div>
                    <h3 class="text-xl font-bold mb-4">添加见证人</h3>
                    <div class="bg-[#12121a] border border-white/5 rounded-xl p-6">
                        <input id="witness-name" type="text" placeholder="见证人姓名" class="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-4 py-3 mb-4 text-white text-sm focus:border-[#c9a84c] focus:outline-none">
                        <input id="witness-email" type="email" placeholder="邮箱（可选）" class="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-4 py-3 mb-4 text-white text-sm focus:border-[#c9a84c] focus:outline-none">
                        <select id="witness-relationship" class="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-4 py-3 mb-4 text-white text-sm focus:border-[#c9a84c] focus:outline-none">
                            <option value="朋友">朋友</option>
                            <option value="家人">家人</option>
                            <option value="同事">同事</option>
                            <option value="导师">导师</option>
                        </select>
                        <button onclick="addWitness()" class="w-full py-3 rounded-lg bg-[#c9a84c] text-black font-semibold hover:bg-[#b8973d] transition">添加见证人</button>
                    </div>
                </div>
                <div>
                    <h3 class="text-xl font-bold mb-4">我的见证人</h3>
                    <div id="witness-list" class="space-y-3"><p class="text-gray-500 text-sm">还没有添加见证人</p></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Evolution Pyramid Section -->
    <section id="section-evolution" class="py-20 px-6 bg-[#0a0a0f]">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="font-serif text-3xl font-bold mb-4">进化金字塔</h2>
            <p class="text-gray-400 mb-12">灵魂的进化不是线性的，是螺旋上升的。</p>
            <div class="inline-block bg-[#12121a] border border-white/5 rounded-xl p-6 font-mono text-sm mb-8">
                <pre class="text-[#c9a84c]">
          ✨
        ┌───┐
        │ · │
      ┌─┴───┴─┐
      │   ·   │
    ┌─┴───────┴─┐
    │     ·     │
  ┌─┴───────────┴─┐
  │      ·        │
┌─┴───────────────┴─┐
│        1          │
└───────────────────┘</pre>
            </div>
            <div id="evolution-stats" class="grid grid-cols-3 gap-4 max-w-lg mx-auto mb-8">
                <div class="bg-[#12121a] border border-white/5 rounded-lg p-4"><p class="text-2xl font-bold text-[#c9a84c]">1</p><p class="text-xs text-gray-500">当前层级</p></div>
                <div class="bg-[#12121a] border border-white/5 rounded-lg p-4"><p class="text-2xl font-bold text-gray-300">0</p><p class="text-xs text-gray-500">经验值</p></div>
                <div class="bg-[#12121a] border border-white/5 rounded-lg p-4"><p class="text-2xl font-bold text-gray-300">0</p><p class="text-xs text-gray-500">突破次数</p></div>
            </div>
            <div id="evolution-level" class="bg-[#12121a] border border-white/5 rounded-xl p-6 max-w-md mx-auto">
                <p class="text-2xl mb-2">😴 睡眠层 (Sleep)</p>
                <p class="text-gray-400 text-sm">大多数人所在的地方。你的枷锁驱动你的行为，但你不知道。</p>
            </div>
        </div>
    </section>

'''

lines.insert(body_idx, html_additions)

# Update navigation
for i, line in enumerate(lines):
    if 'section-crossing' in line and '穿越' in line and '见证' not in line:
        lines[i] = line.replace('</a>', '</a>\n                <a href="#section-witness" class="text-xs text-gray-500 hover:text-gray-300 transition">见证</a>\n                <a href="#section-evolution" class="text-xs text-gray-500 hover:text-gray-300 transition">进化</a>')
        break

with open("index.html", "w") as f:
    f.writelines(lines)

print("done: witness + evolution sections added")
PYEOF