"""KYBER - Cybernetic Agent Operating System"""
from kyber.core.vsm import (AlgedonicBus, AlgedonicSignal, AgentIdentity, AgentState,
    AutonomyLevel, KyberAgent, Task, TaskResult, VSMLevel)
from kyber.core.router import S2Coordinator
from kyber.core.autopoiesis import AutopoieticLoop, HealthMetrics, SpawnRequest
from kyber.comms.shannon import ShannonOptimizer, to_toon, from_toon
from kyber.governance.policy import PolicyEngine, Charter, S3StarAuditor, default_charter
from kyber.tools.claude_agent import ClaudeKyberAgent, AgentFactory

import asyncio, time
from typing import Dict, List, Optional, Any

class Kyber:
    def __init__(self, api_key: Optional[str] = None, charter: Optional[Charter] = None,
                 audit_sample_rate: float = 0.15):
        self.policy = PolicyEngine(charter or default_charter())
        self.bus = AlgedonicBus()
        self.auditor = S3StarAuditor(self.policy, self.bus, audit_sample_rate)
        self.coordinator = S2Coordinator(self.bus)
        self.autopoiesis = AutopoieticLoop(self.bus, self.coordinator._agents)
        self.factory = AgentFactory(default_api_key=api_key)
        self.bus.on_hitl(self._handle_hitl)
        self._hitl_log: List[AlgedonicSignal] = []
        self._start_time = time.time()

    def spawn(self, name: str, capabilities: set, vsm_level: VSMLevel = VSMLevel.S1,
              depth: int = 1, autonomy: AutonomyLevel = AutonomyLevel.HOTL,
              model: str = "claude-sonnet-4-6", extra_instructions: str = "") -> ClaudeKyberAgent:
        agent = self.factory.create(name=name, capabilities=capabilities, vsm_level=vsm_level,
                                    depth=depth, autonomy=autonomy, model=model,
                                    extra_instructions=extra_instructions)
        agent.attach_algedonic_bus(self.bus)
        self.coordinator.register_agent(agent)
        self.policy.register_agent(agent)
        return agent

    async def run(self, task_type: str, payload: Dict = None, priority: int = 5) -> Optional[TaskResult]:
        task = Task(task_type=task_type, payload=payload or {}, priority=priority)
        await self.coordinator.submit(task)
        result = await self.coordinator.route_one()
        if result: await self.auditor.audit_result(result, task)
        return result

    async def run_batch(self, tasks: List[Dict]) -> List[TaskResult]:
        task_objects = [Task(task_type=t["type"], payload=t.get("payload",{}), priority=t.get("priority",5)) for t in tasks]
        for t in task_objects: await self.coordinator.submit(t)
        results = []
        for t in task_objects:
            result = await self.coordinator.route_one()
            if result: await self.auditor.audit_result(result, t); results.append(result)
        return results

    async def start_background(self):
        asyncio.create_task(self.autopoiesis.run())
        asyncio.create_task(self.coordinator.run_loop())

    def status(self) -> Dict:
        return {"kyber_version":"1.0.0","uptime_s":round(time.time()-self._start_time),
                "charter":self.policy.charter.name,"charter_hash":self.policy.charter.hash,
                "coordinator":self.coordinator.status(),"autopoiesis":self.autopoiesis.status(),
                "audit":self.auditor.drift_report(),
                "algedonic":{"unacknowledged_pain":len(self.bus.unacknowledged_pain()),
                             "hitl_requests":len(self._hitl_log),
                             "recent":[{"type":s.signal_type,"sev":s.severity,"msg":s.message[:60]}
                                       for s in self.bus.recent(5)]}}

    def _handle_hitl(self, signal: AlgedonicSignal):
        self._hitl_log.append(signal)
        print(f"\n{'='*60}\n🔴 HITL REQUIRED\nSource: {signal.source_id}\nSeverity: {signal.severity}/10\nMessage: {signal.message}\n{'='*60}\n")

__version__ = "1.0.0"
__all__ = ["Kyber","KyberAgent","ClaudeKyberAgent","AgentFactory","VSMLevel","AutonomyLevel",
           "AgentIdentity","AgentState","Task","TaskResult","AlgedonicBus","AlgedonicSignal",
           "S2Coordinator","PolicyEngine","Charter","S3StarAuditor","AutopoieticLoop",
           "ShannonOptimizer","to_toon","from_toon","default_charter"]
