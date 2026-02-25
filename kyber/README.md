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
pip install kyber-agent    # coming: pypi
# or:
git clone https://github.com/kyber-os/kyber && cd kyber
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

## Key Innovations

### 1. TOON: Token-Oriented Object Notation
All agent-to-agent messages use TOON — a purpose-built wire format achieving ~72% token reduction vs JSON.

```
# JSON (147 chars, ~36 tokens):
{"task_id":"abc123","success":true,"duration_ms":142,"error":null}

# TOON (52 chars, ~13 tokens):
task_id=abc123|ok=T|ms=142|err=-
```

At 1M agent calls/day: the difference between $3,000/day and $840/day.

### 2. Ashby Variety Routing
Tasks are routed to agents whose capability set covers the task type — not round-robin, not random.

```python
# Variety matching in action:
"research"  → Researcher (variety=8, covers: research, summarize, fact_check...)
"write"     → Writer     (variety=8, covers: write, edit, format...)
"unknown"   → ⚠️ Variety gap detected → S4 proposes new agent class
```

### 3. Algedonic Signal Bus
Beer's "channel that bypasses the hierarchy" — urgent signals go directly to human oversight without waiting for scheduled reports.

```python
# Pain signal (severity 7+) → immediate HITL escalation
🟡 [S1] "Research agent: 6% error rate approaching threshold" (sev=4)
🔴 [S3*] "Prohibited content detected in output — HITL required" (sev=8)
⚡ [S1] "Writer completed 100th article milestone" (sev=1, pleasure)
```

### 4. S3* Sporadic Audit Channel
15% of task results are randomly sampled against the charter. Drift patterns accumulate invisibly until S3* catches them.

```python
# S3* detects what S3 monitoring misses:
- Prohibited content patterns in agent outputs
- Token usage anomalies (possible prompt injection)
- Repeated error sequences indicating model drift
```

### 5. Autopoietic Self-Maintenance
The organization produces and reproduces its own components. When an agent's error rate recovers, it's automatically restored to healthy status. When organization health drops below 50%, HITL escalation fires.

```python
Iter 1: [████████████████████] 98% | err_rate=2.5% | tasks=30
Iter 4: [██████████████████░░] 92% | err_rate=8.0% | tasks=102
Iter 5: [███████████████████░] 95% | err_rate=4.1% | tasks=124  # recovered
```

## VSM Mapping

| Beer's VSM | Kyber Class | Function |
|---|---|---|
| S5 Policy | `PolicyEngine` | Charter enforcement, HITL gates |
| S4 Intelligence | `AutopoieticLoop` | Health monitoring, structural adaptation |
| S3 Cohesion | `AgentFactory` budget tracking | Resource allocation |
| S3* Audit | `S3StarAuditor` | Sporadic compliance sampling |
| S2 Coordination | `S2Coordinator` | Variety matching, anti-oscillation |
| S1 Operations | `ClaudeKyberAgent` | Claude-backed task execution |

## Charter Governance

```python
from kyber import Kyber
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

## Recursion Guard

Kyber enforces a maximum VSM depth of 3. Leaf agents at depth 3 cannot spawn children.

```
Depth 1: Kyber Organization (S5→S4→S3→S2→S1 departments)
Depth 2: HR Department     (S5→S4→S3→S2→S1 workers)
Depth 3: Recruiter Team    (leaf nodes — no spawning)
```

```python
# This raises RuntimeError:
agent_depth3.create_child()
# RuntimeError: Cannot spawn at depth 4: exceeds MAX_DEPTH 3
```

## Roadmap

- **MVP (now)**: Python package, Claude agent, VSM hierarchy, Shannon optimizer, algedonic bus
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
