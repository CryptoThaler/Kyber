"""KYBER Autopoietic Loop — Maturana & Varela (1972) self-maintenance"""
from __future__ import annotations
import asyncio, time, uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from kyber.core.vsm import AlgedonicBus, AlgedonicSignal, KyberAgent, VSMLevel

@dataclass
class HealthMetrics:
    timestamp: float = field(default_factory=time.time)
    total_agents: int = 0; alive_agents: int = 0; healthy_agents: int = 0
    avg_error_rate: float = 0.0; total_tasks: int = 0; queue_depth: int = 0
    variety_gaps: List[str] = field(default_factory=list)
    unack_pain_signals: int = 0; organization_health: float = 1.0

    @property
    def is_critical(self): return self.organization_health < 0.5
    @property
    def needs_expansion(self): return len(self.variety_gaps) > 0 or self.queue_depth > 10

class AutopoieticLoop:
    def __init__(self, bus: AlgedonicBus, agents: Dict[str, KyberAgent],
                 check_interval: float = 30.0):
        self.bus = bus; self.agents = agents; self.check_interval = check_interval
        self._history: List[HealthMetrics] = []; self._running = False
        self.bus.subscribe(self._on_signal)

    async def run(self):
        self._running = True
        while self._running:
            metrics = self._measure(); self._history.append(metrics)
            await self._adapt(metrics); await asyncio.sleep(self.check_interval)

    def stop(self): self._running = False

    def _measure(self) -> HealthMetrics:
        agents = list(self.agents.values())
        if not agents: return HealthMetrics()
        alive = [a for a in agents if a.state.is_alive]
        healthy = [a for a in agents if a.state.is_healthy]
        err_rates = [a.state.error_rate for a in alive]
        avg_err = sum(err_rates) / len(err_rates) if err_rates else 0.0
        unack = len(self.bus.unacknowledged_pain())
        alive_r = len(alive) / len(agents)
        health_r = len(healthy) / max(len(alive), 1)
        org_health = (alive_r*0.3 + health_r*0.4 + (1-min(avg_err*5,1))*0.2 + (1-min(unack*0.1,0.5))*0.1)
        return HealthMetrics(total_agents=len(agents), alive_agents=len(alive),
                             healthy_agents=len(healthy), avg_error_rate=avg_err,
                             total_tasks=sum(a.state.task_count for a in agents),
                             unack_pain_signals=unack, organization_health=org_health)

    async def _adapt(self, metrics: HealthMetrics):
        if metrics.is_critical:
            await self.bus.emit(AlgedonicSignal(source_id="autopoietic-loop",
                source_level=VSMLevel.S4, signal_type="pain", severity=8,
                message=f"Organization health critical: {metrics.organization_health:.0%}"))
        for agent in list(self.agents.values()):
            if not agent.state.is_healthy and agent.state.error_rate < 0.03:
                agent.state.is_healthy = True
                await self.bus.emit(AlgedonicSignal(source_id="autopoietic-loop",
                    source_level=VSMLevel.S4, signal_type="pleasure", severity=2,
                    message=f"Agent {agent.identity.name} recovered"))

    def _on_signal(self, signal: AlgedonicSignal):
        if signal.signal_type == "pain" and signal.severity >= 7:
            if signal.source_id in self.agents:
                self.agents[signal.source_id].state.is_healthy = False

    def health_trend(self, n: int = 10): return [m.organization_health for m in self._history[-n:]]

    def status(self) -> Dict:
        if not self._history: return {"status": "not_started"}
        latest = self._history[-1]; trend = self.health_trend()
        improving = len(trend) > 1 and trend[-1] > trend[0]
        return {"organization_health": f"{latest.organization_health:.0%}",
                "agents": f"{latest.alive_agents}/{latest.total_agents} alive",
                "avg_error_rate": f"{latest.avg_error_rate:.1%}",
                "trend": "📈 improving" if improving else "📉 declining",
                "unack_pain_signals": latest.unack_pain_signals}

@dataclass
class SpawnRequest:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    requested_by: str = ""; agent_class: str = ""; agent_type: str = ""
    vsm_level: VSMLevel = VSMLevel.S1; parent_id: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    justification: str = ""; requires_hitl: bool = False
    timestamp: float = field(default_factory=time.time)
