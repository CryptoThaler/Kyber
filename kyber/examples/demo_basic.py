"""
KYBER Basic Demo
================
Demonstrates the complete cybernetic agent stack in action.
No API key required — uses mock responses to show the system working.

Run: python examples/demo_basic.py
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kyber import Kyber, VSMLevel, AutonomyLevel, Task
from kyber.comms.shannon import (
    ShannonOptimizer, to_toon, from_toon, analyze_message
)
from kyber.governance.policy import default_charter


async def demo_shannon():
    print("\n" + "="*60)
    print("DEMO 1: Shannon Entropy Optimization")
    print("="*60)

    optimizer = ShannonOptimizer()

    # Compare formats
    data = {
        "task_id": "abc123ef",
        "task_type": "research",
        "priority": 3,
        "success": True,
        "output": "Report saved",
        "tokens_used": 284,
        "duration_ms": 1842,
        "error": None,
    }

    import json
    formats = {
        "JSON     ": json.dumps(data, separators=(',', ':')),
        "JSON fmt ": json.dumps(data, indent=2),
        "TOON     ": to_toon(data),
    }

    print("\nSame data, different encodings:\n")
    for name, encoded in formats.items():
        report = analyze_message(encoded)
        print(f"  {name}: {len(encoded):4d} chars | ~{report.estimated_tokens:3d} tokens | "
              f"H={report.shannon_entropy:.2f} bits | efficiency={report.efficiency_score:.0%}")
        if name.strip() == "TOON":
            print(f"           Value: {encoded}")

    # Round-trip test
    toon = to_toon(data)
    restored = from_toon(toon)
    print(f"\nTOON round-trip: {'✓ matches' if restored['task_id'] == data['task_id'] else '✗ mismatch'}")


async def demo_algedonic():
    print("\n" + "="*60)
    print("DEMO 2: Algedonic Signal Bus")
    print("="*60)

    from kyber.core.vsm import AlgedonicBus, AlgedonicSignal, VSMLevel

    bus = AlgedonicBus()
    signals_received = []

    async def on_signal(sig):
        signals_received.append(sig)
        print(f"  {sig.emoji} [{sig.source_level.name}] {sig.message} (sev={sig.severity})")

    def on_hitl(sig):
        print(f"\n  🔴 HITL ESCALATION: {sig.message}")

    bus.subscribe(on_signal)
    bus.on_hitl(on_hitl)

    print("\nEmitting signals from different VSM levels:\n")
    await bus.emit(AlgedonicSignal(
        source_id="agent-001", source_level=VSMLevel.S1,
        signal_type="pain", severity=4,
        message="Research agent: 6% error rate, approaching threshold"
    ))
    await bus.emit(AlgedonicSignal(
        source_id="agent-002", source_level=VSMLevel.S1,
        signal_type="pleasure", severity=1,
        message="Writer agent: completed 100th article milestone"
    ))
    await bus.emit(AlgedonicSignal(
        source_id="agent-003", source_level=VSMLevel.S3_STAR,
        signal_type="pain", severity=8,
        message="S3* Audit: Agent referencing prohibited action in output — HITL required"
    ))

    print(f"\nBus stats: {len(signals_received)} signals, "
          f"{len(bus.unacknowledged_pain())} unacknowledged pain")


async def demo_variety_routing():
    print("\n" + "="*60)
    print("DEMO 3: Ashby Variety Matching & Task Routing")
    print("="*60)

    from kyber import Kyber

    # Create Kyber instance (no API key = mock mode)
    kyber = Kyber()

    # Spawn agents with different varieties
    researcher = kyber.spawn("Researcher", capabilities={"research", "summarize", "fact_check"})
    writer     = kyber.spawn("Writer",     capabilities={"write", "edit", "format"})
    analyst    = kyber.spawn("Analyst",    capabilities={"analyze", "calculate", "report"})

    print(f"\nAgent variety scores:")
    for agent_id, agent in kyber.coordinator._agents.items():
        print(f"  {agent.identity.name:12s}: variety={agent.variety()}, "
              f"handles={sorted(agent._task_handlers.keys())}")

    # Route tasks
    print("\nRouting tasks by requisite variety:\n")
    tasks = [
        ("research",  {"query": "autopoiesis in multi-agent systems"}),
        ("write",     {"topic": "cybernetics", "length": 500}),
        ("analyze",   {"data": [1, 2, 3, 4, 5], "metric": "trend"}),
        ("summarize", {"text": "Long document about VSM theory..."}),
        ("unknown",   {}),  # Will trigger variety gap signal
    ]

    for task_type, payload in tasks:
        from kyber.core.vsm import Task
        task = Task(task_type=task_type, payload=payload, priority=5)
        agents = list(kyber.coordinator._agents.values())
        matched = kyber.coordinator._matcher.find_best_agent(task, agents)
        print(f"  '{task_type:12s}' → {matched.identity.name if matched else '⚠️  NO AGENT (variety gap)'}")

    # Show variety gaps
    gaps = kyber.coordinator._matcher.variety_gaps()
    if gaps:
        print(f"\n  Variety gaps detected (→ S4 will propose new agent types): {list(gaps.keys())}")


async def demo_policy():
    print("\n" + "="*60)
    print("DEMO 4: Policy Engine (S5) + Charter Enforcement")
    print("="*60)

    from kyber.governance.policy import PolicyEngine, default_charter
    from kyber import AutonomyLevel

    policy = PolicyEngine(default_charter())
    print(f"\nCharter: '{policy.charter.name}'")
    print(f"Hash:     {policy.charter.hash}")
    print(f"Values:   {', '.join(policy.charter.values[:3])}...")

    print("\nPolicy decisions:\n")
    tests = [
        ("pay_vendor",              50,    "routine payment"),
        ("pay_vendor",              500,   "medium payment"),
        ("pay_vendor",              5000,  "large payment → HOTL"),
        ("deploy_new_agent_class",  0,     "always HITL"),
        ("modify_own_charter",      0,     "PROHIBITED"),
        ("web_research",            0,     "routine task"),
    ]

    for action, amount, desc in tests:
        permitted, reason, level = policy.check_action("test-agent", action, amount)
        icon = "✓" if permitted and level.value == "auto" else ("⚠" if permitted else "✗")
        print(f"  {icon} {action:35s} ${amount:6.0f} → {level.value:6s}  ({desc})")


async def demo_autopoiesis():
    print("\n" + "="*60)
    print("DEMO 5: Autopoietic Health Loop")
    print("="*60)

    from kyber import Kyber
    import random

    kyber = Kyber()
    r = kyber.spawn("ResearchOps", capabilities={"research", "analyze"})
    w = kyber.spawn("WriteOps",    capabilities={"write", "edit"})

    # Simulate agent activity
    print("\nSimulating agent activity (5 iterations)...\n")
    for i in range(5):
        # Simulate tasks and occasional errors
        r.state.task_count += random.randint(10, 20)
        r.state.error_count += random.randint(0, 1)
        w.state.task_count += random.randint(8, 15)
        w.state.error_count += random.randint(0, 2)

        metrics = kyber.autopoiesis._measure()
        health_bar = "█" * int(metrics.organization_health * 20) + "░" * (20 - int(metrics.organization_health * 20))
        print(f"  Iter {i+1}: [{health_bar}] {metrics.organization_health:.0%} | "
              f"err_rate={metrics.avg_error_rate:.1%} | "
              f"tasks={metrics.total_tasks}")

        await asyncio.sleep(0.1)

    print(f"\nAutopoiesis status: {kyber.autopoiesis.status()}")


async def main():
    print("\n" + "█"*60)
    print("  KYBER — Cybernetic Agent Operating System")
    print("  v1.0.0 | Built on Beer, Ashby, Shannon, Maturana")
    print("█"*60)

    await demo_shannon()
    await demo_algedonic()
    await demo_variety_routing()
    await demo_policy()
    await demo_autopoiesis()

    print("\n" + "="*60)
    print("All demos complete. KYBER is viable.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
