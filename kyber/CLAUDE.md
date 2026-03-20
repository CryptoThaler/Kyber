# KYBER — Claude Code Integration Guide

This file is read by Claude Code automatically. It tells Claude how to work with the Kyber codebase.

## What This Repo Is

Kyber is a **Cybernetic Agent Operating System** — a Python framework for building multi-agent Claude deployments grounded in Beer's Viable System Model. Every `KyberAgent` is a complete VSM (S1-S5) operating within a recursive organizational hierarchy.

## Core Concepts Claude Must Understand

### The VSM Hierarchy
```
S5  PolicyEngine     → Charter (invariant). Never change without human approval.
S4  AutopoieticLoop  → Health monitoring. Runs in background.
S3* S3StarAuditor    → Bypasses hierarchy. Samples 15% of results.
S3  AgentFactory     → Resource allocation via budget tracking.
S2  S2Coordinator    → Routes tasks by Ashby variety matching.
S1  ClaudeKyberAgent → Executes tasks. Each IS a causal model of its domain.
```

### Invariant Rule (Maturana)
**Organization is invariant. Structure is variable.**
- `AgentIdentity` = organization (don't mutate after creation)
- `AgentState` = structure (update freely)
- `Charter` = S5 policy (only humans can amend via `policy.amend_charter()`)

### Communication Format (Shannon)
**ALL agent-to-agent messages use TOON format. NOT JSON. NOT prose.**
```python
from kyber.comms.shannon import to_toon, from_toon

# Correct: internal message
msg = to_toon({"id": "abc", "ok": True, "ms": 142})
# → "id=abc|ok=T|ms=142"

# Correct: human-facing output
output = json.dumps(data, indent=2)  # prose is fine for humans
```

### Variety Rule (Ashby)
**Never assign tasks to agents outside their variety.**
```python
if not agent.can_handle(task.task_type):
    # Escalate to S2 coordinator or emit algedonic signal
    await coordinator.submit(task)  # let the router find the right agent
```

### Algedonic Signals (Beer)
**Pain (sev ≥ 7) → immediate HITL. Pleasure → amplify to S5.**
```python
# From within any agent:
await self._emit_pain()         # auto-fires when error_rate > 5%
await self._emit_pleasure("milestone: 1000 tasks complete")

# From external code:
await bus.emit(AlgedonicSignal(
    source_id="my-monitor",
    source_level=VSMLevel.S3_STAR,
    signal_type="pain",
    severity=8,
    message="Critical: charter violation detected"
))
```

### Recursion Guard
**MAX_DEPTH = 3. Never bypass this.**
```python
if not agent.can_spawn():
    raise RuntimeError("Leaf agent at max depth cannot spawn children")
```

## File Structure
```
kyber/
  __init__.py          # Kyber runtime class — start here
  core/
    vsm.py             # KyberAgent, Task, TaskResult, AlgedonicBus
    router.py          # S2Coordinator + VarietyMatcher (Ashby)
    autopoiesis.py     # AutopoieticLoop (Maturana)
  comms/
    shannon.py         # TOON format, ShannonOptimizer, entropy analysis
  governance/
    policy.py          # PolicyEngine (S5), Charter, S3StarAuditor
  tools/
    claude_agent.py    # ClaudeKyberAgent, AgentFactory
  channels/
    telegram.py        # TelegramChannel, TelegramConfig — Telegram bot bridge
examples/
  demo_basic.py        # Runnable demo — all 5 subsystems
  telegram_bot.py      # Telegram bot example
.env.example           # Environment variable template
CLAUDE.md              # This file
README.md              # Full documentation
```

## How To Add a New Agent Type

```python
# 1. Subclass KyberAgent (or use ClaudeKyberAgent directly)
from kyber import KyberAgent, AgentIdentity, Task, TaskResult, VSMLevel

class MySpecialistAgent(KyberAgent):
    def _register_handlers(self):
        self._task_handlers = {
            "my_task_type": self._handle_my_task,
        }

    async def execute(self, task: Task) -> TaskResult:
        handler = self._task_handlers.get(task.task_type)
        if handler:
            return await handler(task)
        return TaskResult(task_id=task.task_id, agent_id=self.identity.agent_id,
                          success=False, error="Not in variety")

    async def _handle_my_task(self, task: Task) -> TaskResult:
        # Your logic here
        return TaskResult(task_id=task.task_id, agent_id=self.identity.agent_id,
                          success=True, output="result")

# 2. Register with Kyber
kyber = Kyber()
identity = AgentIdentity(name="MySpecialist", capabilities={"my_task_type"})
agent = MySpecialistAgent(identity)
kyber.coordinator.register_agent(agent)
```

## How To Handle HITL Events

```python
kyber = Kyber()

# Override the default HITL handler
def my_hitl_handler(signal):
    # Send to Slack, PagerDuty, email, etc.
    send_slack_alert(
        channel="#agent-ops",
        message=f"🔴 HITL: {signal.message}",
        payload=signal.payload
    )

kyber.bus.on_hitl(my_hitl_handler)
```

## How To Amend the Charter

```python
# Charter amendments require human authorization
kyber.policy.amend_charter(
    amendments={"spend_limits": {"auto": 500.0, "hotl": 5000.0}},
    human_id="alice@company.com"   # Log who authorized it
)
```

## How To Connect Telegram

```python
from kyber import Kyber
from kyber.channels.telegram import TelegramChannel, TelegramConfig

kyber = Kyber()
kyber.spawn("assistant", capabilities={"prompt", "think"})

config = TelegramConfig(
    bot_token="your-token-from-botfather",
    allowed_chat_ids={123456789},  # restrict to specific chats
    alerts_chat_id=-100123456,     # forward algedonic signals here
)
channel = TelegramChannel(kyber, config)
channel.run()  # starts polling
```

Or configure via environment variables (see `.env.example`):
```bash
pip install kyber-agent[telegram]
export KYBER_TELEGRAM_BOT_TOKEN=your-token
python examples/telegram_bot.py
```

## Running Tests

```bash
cd kyber
python examples/demo_basic.py    # Full system demo
python -m pytest tests/          # Unit tests (coming)
```

## Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Using JSON for agent messages | Use `to_toon(data)` |
| Calling `agent.execute()` directly | Submit to `coordinator.submit(task)` |
| Modifying `charter` without human_id | Call `policy.amend_charter(amendments, human_id)` |
| Spawning agents at depth > 3 | Check `agent.can_spawn()` first |
| Ignoring pain signals | Wire `bus.on_hitl()` before starting |
| Suppressing algedonic bus | Prohibited in charter — will trigger S3* audit |

## Cybernetic Principles (For Context)

When extending Kyber, stay true to the founding theory:

- **Ashby**: The controller must have AT LEAST as much variety as the system it controls. If your agent keeps failing tasks, it needs more variety (capabilities), not more retries.
- **Beer**: The algedonic bus exists because hierarchies are too slow. Pain signals are not just logs — they bypass normal reporting and demand immediate attention.
- **Maturana**: The organization (charter, identity) must persist through all structural changes. Agents can be replaced; the organization cannot.
- **Shannon**: Every bit of entropy in an agent-to-agent message is a token that costs money. Compress relentlessly.
- **Conant-Ashby**: If your agent can't model its domain accurately, it can't regulate it. The system prompt IS the causal model. Write it carefully.
