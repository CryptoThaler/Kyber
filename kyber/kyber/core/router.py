"""KYBER S2 Coordinator — Ashby variety matching + task routing"""
from __future__ import annotations
import asyncio, heapq, time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from kyber.core.vsm import AlgedonicBus, AlgedonicSignal, KyberAgent, Task, TaskResult, VSMLevel

class TaskQueue:
    def __init__(self): self._q: List[Tuple[int,int,Task]] = []; self._c = 0
    def push(self, task: Task): heapq.heappush(self._q, (task.priority, self._c, task)); self._c += 1
    def pop(self) -> Optional[Task]:
        if self._q: _, _, t = heapq.heappop(self._q); return t
        return None
    def __len__(self): return len(self._q)

class VarietyMatcher:
    def __init__(self): self._gaps: Dict[str,int] = defaultdict(int)
    def find_best_agent(self, task: Task, agents: List[KyberAgent], exclude_ids: List[str] = None) -> Optional[KyberAgent]:
        exclude_ids = exclude_ids or []
        candidates = [a for a in agents if a.can_handle(task.task_type) and
                      a.identity.agent_id not in exclude_ids and a.state.is_alive and a.state.is_healthy]
        if not candidates: self._gaps[task.task_type] += 1; return None
        return min(candidates, key=lambda a: (-a.state.variety_score, a.state.error_rate, 1 if a.state.current_task else 0))
    def variety_gaps(self): return dict(self._gaps)
    def top_gaps(self, n=5): return sorted(self._gaps.items(), key=lambda x: -x[1])[:n]

class S2Coordinator:
    def __init__(self, algedonic_bus: Optional[AlgedonicBus] = None):
        self._agents: Dict[str, KyberAgent] = {}
        self._queue = TaskQueue(); self._matcher = VarietyMatcher()
        self._bus = algedonic_bus; self._task_history: Dict[str, TaskResult] = {}
        self._running = False; self._processed = 0
        self._routed_by_type: Dict[str,int] = defaultdict(int)

    def register_agent(self, agent: KyberAgent):
        self._agents[agent.identity.agent_id] = agent
        if self._bus: agent.attach_algedonic_bus(self._bus)

    def deregister_agent(self, agent_id: str): self._agents.pop(agent_id, None)

    async def submit(self, task: Task) -> str:
        self._queue.push(task); return task.task_id

    async def route_one(self) -> Optional[TaskResult]:
        task = self._queue.pop()
        if not task: return None
        agent = self._matcher.find_best_agent(task, list(self._agents.values()))
        if not agent:
            await self._signal_variety_gap(task)
            return TaskResult(task_id=task.task_id, agent_id="none", success=False,
                              error=f"No agent with variety for '{task.task_type}'")
        agent.state.current_task = task.task_id; t0 = time.time()
        try:
            result = await agent.execute(task)
            result.duration_ms = (time.time() - t0) * 1000
            agent.state.task_count += 1
            if not result.success: agent.state.error_count += 1
            self._routed_by_type[task.task_type] += 1; self._processed += 1
        except Exception as e:
            agent.state.error_count += 1; agent.state.task_count += 1
            result = TaskResult(task_id=task.task_id, agent_id=agent.identity.agent_id,
                                success=False, error=str(e), duration_ms=(time.time()-t0)*1000)
        finally: agent.state.current_task = None
        self._task_history[task.task_id] = result
        await agent.heartbeat(); return result

    async def run_loop(self, poll_interval: float = 0.1):
        self._running = True
        while self._running:
            if len(self._queue) > 0: await self.route_one()
            else: await asyncio.sleep(poll_interval)

    def stop(self): self._running = False

    async def _signal_variety_gap(self, task: Task):
        if self._bus:
            await self._bus.emit(AlgedonicSignal(source_id="s2-coordinator",
                source_level=VSMLevel.S2, signal_type="pain", severity=4,
                payload={"task_type": task.task_type},
                message=f"Variety gap: no agent handles '{task.task_type}'"))

    @property
    def _matcher_ref(self): return self._matcher

    def status(self) -> Dict:
        alive = sum(1 for a in self._agents.values() if a.state.is_alive)
        healthy = sum(1 for a in self._agents.values() if a.state.is_healthy)
        return {"agents_total": len(self._agents), "agents_alive": alive,
                "agents_healthy": healthy, "queue_depth": len(self._queue),
                "tasks_processed": self._processed,
                "variety_gaps": self._matcher.top_gaps(5),
                "top_task_types": sorted(self._routed_by_type.items(), key=lambda x:-x[1])[:5]}
