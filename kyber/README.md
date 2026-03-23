# KYBER — Cybernetic Agent Operating System

> **What Kubernetes is to containers, Kyber is to agents.**

Most AI agents today implement VSM S1 only — they execute tasks when called, then die.
They have no self-maintenance, no organizational memory, no variety management, no algedonic signaling.

**KYBER** is the missing runtime: a full Viable System Model (Beer, 1972) implemented as a Python framework for multi-agent Claude deployments. It turns isolated agents into a *viable organization* — one that maintains its identity through structural change, routes tasks by requisite variety, compresses inter-agent communications, and self-heals when components fail.

## Theoretical Foundation

| Theorist | Year | Concept Applied |
|---|---|---|
| Beer | 1972 | Viable System Model → 5-level agent hierarchy (S1-S5) |
| Ashby | 1956 | Law of Requisite Variety → task routing algorithm |
| Shannon | 1948 | Information Theory → TOON format (72% token reduction) |
| Maturana & Varela | 1972 | Autopoiesis → self-maintaining agent organizations |
| Conant & Ashby | 1970 | Good Regulator Theorem → agent = causal model of domain |
| Wiener | 1948 | Cybernetics → feedback control loops (HOTL/HITL) |
| von Foerster | 1974 | Second-Order Cybernetics → observer-included governance |

## Quick Start

```bash
git clone https://github.com/CryptoThaler/Kyber && cd Kyber/kyber
pip install -e .
python examples/demo_basic.py
```

```python
from kyber import Kyber

# Spin up a complete viable agent organization in 5 lines
kyber = Kyber(api_key="sk-ant-...")
kyber.spawn("Researcher", capabilities={"research", "summarize", "fact_check"})
kyber.spawn("Writer",     capabilities={"write", "edit", "format"})
kyber.spawn("Analyst",    capabilities={"analyze", "calculate", "report"})

# Route a task — Ashby variety matching finds the right agent automatically
result = await kyber.run("research", payload={"query": "autopoiesis in AI systems"})
print(result.output)
```

### Default Model

All `ClaudeKyberAgent` instances default to `claude-sonnet-4-6`. You can override per agent:

```python
kyber.spawn("Deep Thinker", capabilities={"research"}, model="claude-opus-4-6")
```

When no `api_key` is provided, agents run in mock mode — they return simulated responses so you can test routing, policy, and signals without an API key.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S5  POLICY ENGINE        charter, ethics, HITL gates       │
├─────────────────────────────────────────────────────────────┤
│  S4  AUTOPOIETIC LOOP     health monitoring, adaptation     │
├────────────────────────┬────────────────────────────────────┤
│  S3  COHESION           │  S3*  AUDIT (bypasses hierarchy)  │
│  resource bargaining    │       sporadic compliance sampling │
├─────────────────────────────────────────────────────────────┤
│  S2  COORDINATOR          variety matching, anti-oscillation│
├──────────────┬──────────────┬──────────────┬───────────────┤
│  S1 Agent A  │  S1 Agent B  │  S1 Agent C  │  S1 Agent D  │
│  (each is    │  (a complete │  VSM at      │  lower        │
│  itself a    │  higher      │  resolution) │  resolution)  │
│  complete    │              │              │               │
│  VSM)        │              │              │               │
└──────────────┴──────────────┴──────────────┴───────────────┘
         ←─────────── ALGEDONIC BUS ──────────────→
         (pain/pleasure signals bypass hierarchy)
```

## Project Structure

```
kyber/
├── pyproject.toml            # Build config & dependencies (hatchling)
├── .env.example              # Environment variable template
├── CLAUDE.md                 # Claude Code integration guide
├── README.md                 # This file
├── kyber/                    # Core Python package
│   ├── __init__.py           # Kyber runtime class — main entry point
│   ├── __main__.py           # CLI: `kyber demo`
│   ├── core/
│   │   ├── vsm.py            # KyberAgent (ABC), Task, TaskResult, AlgedonicBus,
│   │   │                     # AlgedonicSignal, AgentIdentity, AgentState,
│   │   │                     # VSMLevel, AutonomyLevel
│   │   ├── router.py         # S2Coordinator, VarietyMatcher, TaskQueue
│   │   └── autopoiesis.py    # AutopoieticLoop, HealthMetrics, SpawnRequest
│   ├── comms/
│   │   └── shannon.py        # TOON codec (to_toon/from_toon), ShannonOptimizer,
│   │                         # entropy analysis, KYBER_AGENT_HEADER prompt
│   ├── governance/
│   │   └── policy.py         # PolicyEngine (S5), Charter, S3StarAuditor,
│   │                         # default_charter()
│   ├── tools/
│   │   └── claude_agent.py   # ClaudeKyberAgent, AgentFactory
│   ├── channels/
│   │   └── telegram.py       # TelegramChannel, TelegramConfig
│   └── signals/
│       └── __init__.py       # (placeholder for future signal types)
└── examples/
    ├── demo_basic.py         # 5 runnable demos — no API key required
    └── telegram_bot.py       # Telegram bot example
```

## VSM Mapping

| Beer's VSM | Kyber Class | Module | Function |
|---|---|---|---|
| S5 Policy | `PolicyEngine` | `governance/policy.py` | Charter enforcement, HITL gates, spend limits |
| S4 Intelligence | `AutopoieticLoop` | `core/autopoiesis.py` | Health monitoring, agent recovery, structural adaptation |
| S3 Cohesion | `AgentFactory` + budget tracking | `tools/claude_agent.py` | Resource allocation, agent spawning |
| S3* Audit | `S3StarAuditor` | `governance/policy.py` | Sporadic compliance sampling (15% default), drift detection |
| S2 Coordination | `S2Coordinator` + `VarietyMatcher` | `core/router.py` | Ashby variety matching, priority queue, anti-oscillation |
| S1 Operations | `ClaudeKyberAgent` | `tools/claude_agent.py` | Claude-backed task execution via Anthropic API |

## Key Features

### 1. TOON: Token-Oriented Object Notation

All agent-to-agent messages use TOON — a purpose-built wire format achieving ~72% token reduction vs JSON.

```
# JSON (147 chars, ~36 tokens):
{"task_id":"abc123","success":true,"duration_ms":142,"error":null}

# TOON (52 chars, ~13 tokens):
task_id=abc123|ok=T|ms=142|err=-
```

```python
from kyber.comms.shannon import to_toon, from_toon

msg = to_toon({"id": "abc", "ok": True, "ms": 142})
# → "id=abc|ok=T|ms=142"

data = from_toon(msg)
# → {"id": "abc", "ok": True, "ms": 142}
```

Supports: booleans (`T`/`F`), null (`-`), arrays (`[a,b,c]`), nested keys (`parent.child=val`), integers, floats, and strings.

### 2. Ashby Variety Routing

Tasks are routed to agents whose capability set covers the task type — not round-robin, not random. The `VarietyMatcher` selects the best agent by variety score, error rate, and idle status.

```python
# Variety matching in action:
"research"  → Researcher (variety=5, covers: research, summarize, fact_check, prompt, think)
"write"     → Writer     (variety=5, covers: write, edit, format, prompt, think)
"unknown"   → ⚠️ Variety gap detected → pain signal emitted → S4 proposes new agent class
```

When no agent can handle a task type, the coordinator emits a severity-4 pain signal and records a variety gap. The `AutopoieticLoop` (S4) monitors these gaps for structural adaptation.

### 3. Algedonic Signal Bus

Beer's "channel that bypasses the hierarchy" — urgent signals go directly to human oversight without waiting for scheduled reports.

```python
# Pain signal (severity 7+) → immediate HITL escalation
🟡 [S1] "Research agent: 6% error rate approaching threshold" (sev=4)
🔴 [S3*] "Prohibited content detected in output — HITL required" (sev=8)
⚡ [S1] "Writer completed 100th article milestone" (sev=1, pleasure)
```

The bus supports subscribers (any callback), HITL handlers (triggered at severity >= 7), and unacknowledged pain tracking. Agents automatically emit pain signals when their `error_rate` exceeds 5%.

### 4. S3* Sporadic Audit Channel

15% of task results are randomly sampled against the charter by `S3StarAuditor`. It checks for:

- **Prohibited content** — output containing references to prohibited actions defined in the charter
- **Token anomalies** — usage spikes above 4000 tokens that may indicate prompt injection or model drift

Drift patterns accumulate in a frequency map. The audit report is available via `kyber.status()`.

### 5. Autopoietic Self-Maintenance

The organization produces and reproduces its own components. `AutopoieticLoop` runs every 30 seconds (configurable) and:

- Measures organization health as a weighted composite: alive ratio (30%), healthy ratio (40%), error rate (20%), unacknowledged pain (10%)
- Recovers agents whose error rate drops below 3% after being marked unhealthy
- Emits a severity-8 pain signal when organization health drops below 50%
- Tracks health trends over time (`health_trend()`)

### 6. Charter Governance

The `Charter` is the S5 policy — an immutable set of rules with a SHA-256 hash for integrity.

```python
from kyber.governance.policy import Charter

charter = Charter(
    name="My Organization",
    mission="...",
    values=["safety_first", "minimal_footprint"],
    spend_limits={"auto": 100.0, "hotl": 1000.0, "hitl": 10000.0},
    hitl_thresholds={
        "deploy_new_agent_class": True,   # Always needs human
        "external_legal_commitment": True,
        "charter_amendment": True,
    },
    prohibited=[
        "modify_own_charter",
        "disable_algedonic_bus",
    ]
)

kyber = Kyber(charter=charter)
```

**Default charter** includes five values (`safety_first`, `minimal_footprint`, `human_oversight_respected`, `truthful_reporting`, `reversible_actions_preferred`), five prohibited actions, and five HITL-required actions.

The `PolicyEngine` evaluates actions against the charter and returns one of three autonomy levels:
- **AUTO** — within limits, proceed autonomously
- **HOTL** — human-on-the-loop notification required
- **HITL** — human-in-the-loop approval required (blocks execution)

### 7. Autonomy Levels

Every agent has an `AutonomyLevel` that governs its decision authority:

| Level | Meaning |
|---|---|
| `HITL` | Human-in-the-loop — requires approval for every action |
| `HITLFE` | HITL for exceptions — approval only when things go wrong |
| `HOTL` | Human-on-the-loop — human is notified, can intervene |
| `HATL` | Human-above-the-loop — human sets policy, doesn't monitor |
| `AUTO` | Fully autonomous within charter constraints |

### 8. Recursion Guard

Kyber enforces a maximum VSM depth of 3. Leaf agents at depth 3 cannot spawn children. The `AgentFactory` raises `RuntimeError` if you attempt to exceed this.

```
Depth 1: Kyber Organization (S5→S4→S3→S2→S1 departments)
Depth 2: HR Department     (S5→S4→S3→S2→S1 workers)
Depth 3: Recruiter Team    (leaf nodes — no spawning)
```

## Telegram Integration

Kyber includes a built-in Telegram channel that bridges chat messages to Kyber tasks and forwards algedonic signals to an alerts chat.

### Setup

```bash
pip install -e ".[telegram]"
cp .env.example .env
# Edit .env with your bot token from @BotFather
python examples/telegram_bot.py
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `KYBER_TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `KYBER_TELEGRAM_ALLOWED_CHATS` | No | Comma-separated chat IDs (empty = allow all) |
| `KYBER_TELEGRAM_ALERTS_CHAT` | No | Chat ID for algedonic signal forwarding |
| `KYBER_TELEGRAM_DEFAULT_TASK` | No | Task type for free-text messages (default: `prompt`) |
| `KYBER_TELEGRAM_ALERT_MIN_SEVERITY` | No | Min severity to forward signals (default: `5`) |

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Greeting message |
| `/help` | List available commands |
| `/task <type> <message>` | Submit a typed task (e.g., `/task research quantum computing`) |
| `/status` | Show full Kyber system status as JSON |
| `/agents` | List registered agents with health status |
| (any text) | Submitted as the default task type |

### Programmatic Usage

```python
from kyber import Kyber
from kyber.channels.telegram import TelegramChannel, TelegramConfig

kyber = Kyber()
kyber.spawn("assistant", capabilities={"prompt", "think", "summarize"})
kyber.spawn("coder", capabilities={"code_review", "code_gen", "debug"})

config = TelegramConfig(
    bot_token="your-token-from-botfather",
    allowed_chat_ids={123456789},       # restrict access
    alerts_chat_id=-100123456,          # forward pain/pleasure signals
)
channel = TelegramChannel(kyber, config)

# Register custom commands
async def ping(kyber_instance, chat_id, args):
    return f"Pong! Agents: {len(kyber_instance.coordinator._agents)}"
channel.register_command("ping", ping)

channel.run()  # blocking — starts polling
```

For non-blocking use within an existing event loop:

```python
await channel.start_async()
# ... do other work ...
await channel.stop_async()
```

## API Reference

### `Kyber` (main runtime)

```python
kyber = Kyber(
    api_key=None,              # Anthropic API key (None = mock mode)
    charter=None,              # Charter instance (None = default charter)
    audit_sample_rate=0.15,    # S3* audit sampling rate
)

agent = kyber.spawn(
    name="Name",
    capabilities={"cap1", "cap2"},
    vsm_level=VSMLevel.S1,
    depth=1,
    autonomy=AutonomyLevel.HOTL,
    model="claude-sonnet-4-6",
    extra_instructions="",
)

result = await kyber.run("task_type", payload={"key": "value"}, priority=5)
results = await kyber.run_batch([{"type": "research", "payload": {...}, "priority": 3}])
await kyber.start_background()   # starts autopoiesis + coordinator loops
status = kyber.status()          # full system status dict
```

### Core Data Classes

| Class | Key Fields |
|---|---|
| `AgentIdentity` | `agent_id`, `name`, `vsm_level`, `depth`, `autonomy`, `capabilities`, `spend_limit_usd`, `parent_id`, `charter_hash` |
| `AgentState` | `is_alive`, `is_healthy`, `current_task`, `task_count`, `error_count`, `error_rate` (property), `is_distressed` (property) |
| `Task` | `task_id`, `task_type`, `payload`, `priority`, `requires_hitl`, `deadline`, `is_urgent` (property) |
| `TaskResult` | `task_id`, `agent_id`, `success`, `output`, `error`, `tokens_used`, `duration_ms` |
| `AlgedonicSignal` | `signal_id`, `source_id`, `source_level`, `signal_type`, `severity`, `message`, `requires_hitl` (property) |
| `Charter` | `name`, `mission`, `values`, `spend_limits`, `hitl_thresholds`, `prohibited`, `hash` (property) |

## Running the Demos

```bash
python examples/demo_basic.py
```

Five demos run in sequence, no API key needed:

1. **Shannon Entropy Optimization** — compares JSON vs TOON encoding with entropy analysis
2. **Algedonic Signal Bus** — emits pain/pleasure signals from different VSM levels, shows HITL escalation
3. **Ashby Variety Matching** — routes tasks to agents by capability coverage, demonstrates variety gaps
4. **Policy Engine (S5)** — evaluates actions against the charter with different spend amounts
5. **Autopoietic Health Loop** — simulates agent activity and shows organization health trending

## Dependencies

**Core** (always installed):
- `anthropic>=0.40.0` — Claude API client (async)

**Telegram** (`pip install -e ".[telegram]"`):
- `python-telegram-bot>=21.0`
- `python-dotenv>=1.0`

**Dev** (`pip install -e ".[dev]"`):
- `pytest>=8.0`, `pytest-asyncio>=0.23`, `black`, `mypy`

**Full** (`pip install -e ".[full]"`):
- All of the above plus `prometheus-client`, `redis`, `pinecone-client`

## Roadmap

- **v1.0 (current)**: Python package, Claude agent fleet, VSM hierarchy, Shannon optimizer, algedonic bus, charter governance, Telegram integration
- **v1.1**: Dashboard UI, Prometheus metrics, LangSmith tracing
- **v1.2**: ERC-4337 agent wallets, x402 micropayments, AgentMail integration
- **v2.0**: Multi-org agent marketplace, Wyoming DAO LLC integration, cross-org contracts

## Citation

If you use Kyber in research, please cite:

```
Beer, S. (1972). Brain of the Firm. Penguin.
Ashby, W.R. (1956). Introduction to Cybernetics. Methuen.
Shannon, C. (1948). A Mathematical Theory of Communication. Bell System Technical Journal.
Maturana, H. & Varela, F. (1972). Autopoiesis and Cognition. Reidel.
Conant, R. & Ashby, W.R. (1970). Every good regulator of a system must be a model of that system.
```

## License

MIT — build on it.
