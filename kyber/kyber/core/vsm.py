"""KYBER Core VSM — Beer (1972) Viable System Model for agent fleets"""
from __future__ import annotations
import asyncio, json, time, uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

class VSMLevel(Enum):
    S1=1; S2=2; S3=3; S3_STAR=35; S4=4; S5=5

class AutonomyLevel(Enum):
    HITL="hitl"; HITLFE="hitlfe"; HOTL="hotl"; HATL="hatl"; AUTO="auto"

@dataclass
class AgentIdentity:
    agent_id: str = field(default_factory=lambda: f"agent-{uuid.uuid4().hex[:8]}")
    name: str = ""
    vsm_level: VSMLevel = VSMLevel.S1
    depth: int = 1
    autonomy: AutonomyLevel = AutonomyLevel.HOTL
    capabilities: Set[str] = field(default_factory=set)
    spend_limit_usd: float = 10.0
    parent_id: Optional[str] = None
    charter_hash: Optional[str] = None
    born_at: float = field(default_factory=time.time)

@dataclass
class AgentState:
    is_alive: bool = True
    is_healthy: bool = True
    current_task: Optional[str] = None
    task_count: int = 0
    error_count: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    variety_score: float = 1.0
    entropy_budget: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def error_rate(self):
        return 0.0 if self.task_count == 0 else self.error_count / self.task_count

    @property
    def is_distressed(self):
        return self.error_rate > 0.05 or not self.is_healthy

class KyberAgent(ABC):
    MAX_DEPTH = 3

    def __init__(self, identity: AgentIdentity):
        self.identity = identity
        self.state = AgentState()
        self._algedonic_bus: Optional[AlgedonicBus] = None
        self._task_handlers: Dict[str, Callable] = {}
        self._children: Dict[str, KyberAgent] = {}
        self._register_handlers()

    @abstractmethod
    def _register_handlers(self): pass

    @abstractmethod
    async def execute(self, task: Task) -> TaskResult: pass

    def can_handle(self, task_type: str) -> bool:
        return task_type in self._task_handlers or task_type in self.identity.capabilities

    def variety(self) -> int:
        return len(self._task_handlers) + len(self.identity.capabilities)

    async def heartbeat(self):
        self.state.last_heartbeat = time.time()
        if self.state.is_distressed:
            await self._emit_pain()

    async def _emit_pain(self):
        if self._algedonic_bus:
            await self._algedonic_bus.emit(AlgedonicSignal(
                source_id=self.identity.agent_id, source_level=self.identity.vsm_level,
                signal_type="pain", severity=min(10, int(self.state.error_rate*100)),
                payload={"error_rate": self.state.error_rate},
                message=f"{self.identity.name} distress: {self.state.error_rate:.1%} error rate"))

    async def _emit_pleasure(self, achievement: str):
        if self._algedonic_bus:
            await self._algedonic_bus.emit(AlgedonicSignal(
                source_id=self.identity.agent_id, source_level=self.identity.vsm_level,
                signal_type="pleasure", severity=1,
                payload={"achievement": achievement}, message=f"{self.identity.name}: {achievement}"))

    def can_spawn(self): return self.identity.depth < self.MAX_DEPTH

    def attach_algedonic_bus(self, bus: AlgedonicBus):
        self._algedonic_bus = bus
        for child in self._children.values():
            child.attach_algedonic_bus(bus)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.identity.agent_id} level={self.identity.vsm_level.name} variety={self.variety()}>"

@dataclass
class Task:
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    task_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    requires_hitl: bool = False
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    requester_id: Optional[str] = None

    @property
    def is_urgent(self): return self.priority <= 2

    def to_compressed(self):
        return {"id": self.task_id[:8], "t": self.task_type, "p": self.priority, "payload": self.payload}

@dataclass
class TaskResult:
    task_id: str
    agent_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    tokens_used: int = 0
    duration_ms: float = 0.0
    variety_consumed: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_compressed(self):
        base = {"id": self.task_id[:8], "ok": self.success, "ms": round(self.duration_ms)}
        if self.error: base["err"] = self.error
        if self.output is not None: base["out"] = self.output
        return base

@dataclass
class AlgedonicSignal:
    signal_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    source_id: str = ""
    source_level: VSMLevel = VSMLevel.S1
    signal_type: str = "pain"
    severity: int = 5
    payload: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False

    @property
    def requires_hitl(self): return self.signal_type == "pain" and self.severity >= 7

    @property
    def emoji(self): return "⚡" if self.signal_type == "pleasure" else ("🔴" if self.severity >= 7 else "🟡")

class AlgedonicBus:
    def __init__(self):
        self._signals: List[AlgedonicSignal] = []
        self._subscribers: List[Callable] = []
        self._hitl_handlers: List[Callable] = []

    async def emit(self, signal: AlgedonicSignal):
        self._signals.append(signal)
        for sub in self._subscribers:
            result = sub(signal)
            if asyncio.iscoroutine(result): await result
        if signal.requires_hitl:
            for h in self._hitl_handlers:
                result = h(signal)
                if asyncio.iscoroutine(result): await result

    def subscribe(self, cb): self._subscribers.append(cb)
    def on_hitl(self, cb): self._hitl_handlers.append(cb)
    def unacknowledged_pain(self): return [s for s in self._signals if s.signal_type=="pain" and not s.acknowledged]
    def recent(self, n=20): return sorted(self._signals, key=lambda s: s.timestamp, reverse=True)[:n]
