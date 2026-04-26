# NarrowGate 窄门

> **"引到永生，那门是窄的，路是小的，找着的人也少。"**

NarrowGate is an AI-powered soul evolution platform — not another meditation app or goal tracker, but a diagnostic engine that helps you see and cross your narrow gate.

**Core truth: You don't lack knowledge of what to do. You lack the willingness to do what you already know.**

---

## The Five Pillars

| Pillar | Description |
|--------|-------------|
| **Soul Audit** | Socratic questioning across 5 dimensions to identify your shackles |
| **Master Guides** | 7 AI masters with distinct personalities guide your journey |
| **Crossing Training** | 30-day daily challenges — do what you least want to do |
| **Witness Network** | Real people witness and hold you accountable for your evolution |
| **Evolution Pyramid** | Visual progression from Sleep layer to Divinity layer |

---

## Architecture

```
┌─────────────────────────────────────────┐
│        Frontend (HTML + Tailwind)        │
│   Soul Audit / Master Dialogue / Crossing│
├─────────────────────────────────────────┤
│          FastAPI Backend (Python)        │
│  Soul Audit │ Crossing │ Master Engines  │
├─────────────────────────────────────────┤
│              MIMO AI (Xiaomi)            │
│   Socrates / Jung / Awakened One / ...   │
├─────────────────────────────────────────┤
│              SQLite Database             │
│  Users │ Audits │ Crossings │ Witnesses  │
└─────────────────────────────────────────┘
```

### Core Engines

| Engine | File | Function |
|--------|------|----------|
| Soul Audit | `src/core/soul_audit.py` | 5-dimension layered questioning (Cognition / Emotion / Behavior / Relations / Mission) |
| Gate Finder | `src/core/gate_finder.py` | Generates narrow gate priorities from identified shackles |
| Crossing | `src/core/crossing.py` | 30-day daily challenge system |
| Masters | `src/core/masters.py` | 7 AI masters with distinct questioning styles |
| Witness | `src/core/witness.py` | Human witness network for accountability |
| Evolution | `src/core/evolution.py` | 5-layer evolution model with XP tracking |
| MIMO Client | `src/core/mimo_client.py` | Xiaomi MIMO API integration |
| Database | `src/core/database.py` | SQLite persistence layer |

---

## The Seven Masters

| Master | Identity | Dimension | Style |
|--------|----------|-----------|-------|
| Socrates | Questioner | Cognition | Logical contradiction exposure |
| Jung | Shadow Hunter | Emotion | Shadow integration |
| The Awakened | Executor | Behavior | Procrastination dissection |
| The Mirror | Relations Analyst | Relations | Relationship pattern recognition |
| The Architect | Systems Thinker | Career | Life architecture audit (Level 2+) |
| The Alchemist | Transformer | Cognition | Pain transmutation (Level 3+) |
| The Gatekeeper | The Gate itself | All | Crossing verification (Level 4+) |

Each master generates real-time dialogue via MIMO API — no template responses.

---

## Evolution Pyramid

```
              *   Level 5: Divinity
            ┌───┐
            │ 4 │  Level 4: Mastery
          ┌─┴───┴─┐
          │   3   │  Level 3: Breakthrough
        ┌─┴───────┴─┐
        │     2     │  Level 2: Awakening
      ┌─┴───────────┴─┐
      │       1       │  Level 1: Sleep
    ┌─┴───────────────┴─┐
    └───────────────────┘
```

**XP Rules:** Daily challenge +10 | Breakthrough +50 | Crossing complete +200

---

## Quick Start

### Prerequisites

- Python 3.12+
- MIMO API key (environment variable `MIMO_API_KEY`)

### Installation

```bash
git clone https://github.com/MoKangMedical/narrowgate.git
cd narrowgate
pip install -r requirements.txt
```

### Run

```bash
python src/api/main.py
```

Open http://localhost:8090

### Production Deployment

```bash
sudo tee /etc/systemd/system/narrowgate.service << 'EOF'
[Unit]
Description=NarrowGate
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/narrowgate/src/api
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 127.0.0.1 --port 8090
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable narrowgate
sudo systemctl start narrowgate
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/audit/start` | Start a soul audit session |
| POST | `/api/audit/answer` | Submit audit answer (triggers AI follow-up) |
| POST | `/api/audit/complete` | Complete the audit |
| GET | `/api/audit/{id}/gates` | Get narrow gate candidates |
| GET | `/api/masters` | List all available masters |
| POST | `/api/masters/choose` | Select a master guide |
| POST | `/api/crossing/start` | Start a crossing challenge |
| POST | `/api/crossing/complete` | Complete a daily challenge |
| POST | `/api/witness/add` | Add a witness |
| GET | `/api/witness/list` | List witnesses |
| GET | `/api/evolution/{user_id}` | Get evolution status |
| POST | `/api/evolution/breakthrough` | Record a breakthrough |

### Example

```bash
# Start soul audit
curl -X POST http://localhost:8090/api/audit/start \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user"}'

# Submit answer (AI-powered follow-up)
curl -X POST http://localhost:8090/api/audit/answer \
  -H "Content-Type: application/json" \
  -d '{
    "audit_id": "audit_xxx",
    "answer": "My greatest achievement is completing medical school",
    "master_id": "socrates"
  }'
```

---

## Soul Audit — How It Works

### Five Dimensions

| Dimension | Explores | Core Question |
|-----------|----------|---------------|
| Cognition | Beliefs, thought patterns | What do you believe is true? |
| Emotion | Feelings, repression, fear | What are you feeling? |
| Behavior | Habits, execution, procrastination | What are you doing? |
| Relations | Interpersonal, boundaries, people-pleasing | Who are you in relationships? |
| Mission | Meaning, direction, values | Why do you exist? |

### Evasion Detection

The system detects four real-time evasion patterns:

- **Denial** — "No", "It's not like that", "It's fine"
- **Deflection** — "Speaking of which", "Oh right", "Also..."
- **Minimization** — "A little bit", "Slightly", "Maybe somewhat"
- **Rationalization** — "Because", "No choice", "Everyone does it"

---

## Project Structure

```
narrowgate/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── middleware.py         # Request middleware
│   │   └── expert_routes.py     # Expert system API routes
│   ├── core/
│   │   ├── soul_audit.py        # Soul audit engine
│   │   ├── gate_finder.py       # Gate identification
│   │   ├── crossing.py          # 30-day crossing challenges
│   │   ├── masters.py           # 7 master guide system
│   │   ├── witness.py           # Witness network
│   │   ├── evolution.py         # Evolution pyramid & XP
│   │   ├── mimo_client.py       # MIMO AI client
│   │   ├── database.py          # SQLite persistence
│   │   ├── expert_agents.py     # Expert agent system
│   │   ├── payment.py           # Payment integration
│   │   └── analytics.py         # Analytics tracking
│   └── ui/
│       ├── index.html            # Main frontend
│       ├── tailwind.css          # Styles
│       └── manifest.json         # PWA manifest
├── b2b/                          # B2B student portal
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── requirements.txt
└── CHANGELOG.md
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| Pydantic | Data validation |
| httpx | HTTP client (MIMO API calls) |
| aiofiles | Async file operations |
| Jinja2 | Template rendering |
| SQLite3 | Database (built-in) |

---

## Documentation

- [Theory System](docs/THEORY.md) — Complete methodology (9 chapters)
- [Knowledge Base](docs/KNOWLEDGE_BASE.md) — 22 theoretical frameworks + reading list
- [CHANGELOG](CHANGELOG.md) — Version history

---

## License

Proprietary project by Dr. MoKang (MoKangMedical).

## Acknowledgments

- Xiaomi MIMO team — AI dialogue capabilities
- Socrates — "The unexamined life is not worth living"

---

*"Not that you don't know — you don't want to. The gate is waiting."*
