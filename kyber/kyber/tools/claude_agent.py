"""KYBER Claude Agent — ClaudeKyberAgent backed by claude-sonnet-4-6"""
from __future__ import annotations
import asyncio, hashlib, json, time
from typing import Any, Dict, List, Optional, Tuple
from kyber.core.vsm import AgentIdentity, AutonomyLevel, KyberAgent, Task, TaskResult, VSMLevel
from kyber.comms.shannon import ShannonOptimizer, KYBER_AGENT_HEADER, TOON_GUIDE

class ClaudeKyberAgent(KyberAgent):
    def __init__(self, identity: AgentIdentity, api_key: Optional[str] = None,
                 model: str = "claude-sonnet-4-6", extra_instructions: str = "",
                 tools: Optional[List[Dict]] = None):
        self.api_key = api_key; self.model = model
        self.extra_instructions = extra_instructions; self.tools = tools or []
        self.optimizer = ShannonOptimizer()
        self._client = None; self._session_tokens = 0; self._session_cost_usd = 0.0
        super().__init__(identity)
        prompt = self._build_system_prompt()
        self.identity.charter_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

    def _register_handlers(self):
        self._task_handlers = {t: self._execute_with_claude for t in self.identity.capabilities}
        self._task_handlers["prompt"] = self._execute_with_claude
        self._task_handlers["think"]  = self._execute_with_claude

    def _build_system_prompt(self) -> str:
        header = self.optimizer.format_prompt_header(self.identity.name, {
            "vsm_level": self.identity.vsm_level.name, "depth": self.identity.depth,
            "autonomy": self.identity.autonomy.value,
            "capabilities": list(self.identity.capabilities),
            "spend_limit_usd": self.identity.spend_limit_usd})
        caps = "\n".join(f"  - {c}" for c in sorted(self.identity.capabilities)) or "  - general"
        return f"""{KYBER_AGENT_HEADER}\n{header}\n## YOUR ROLE\nYou are **{self.identity.name}**, Kyber agent {self.identity.vsm_level.name}, depth {self.identity.depth}/{self.MAX_DEPTH}.\n## CAPABILITIES\n{caps}\n## COMMUNICATION\n{TOON_GUIDE}\n{self.extra_instructions}"""

    async def execute(self, task: Task) -> TaskResult:
        t0 = time.time()
        if not self.can_handle(task.task_type):
            return TaskResult(task_id=task.task_id, agent_id=self.identity.agent_id,
                              success=False, error=f"Task '{task.task_type}' outside variety",
                              duration_ms=(time.time()-t0)*1000)
        try:
            compressed, report = self.optimizer.compress(task.to_compressed(), target="agent")
            user_message = f"TASK: {compressed}"
            if task.payload.get("details"): user_message += f"\n\nDETAILS:\n{task.payload['details']}"
            output, tokens = await self._call_claude(user_message)
            self._session_tokens += tokens; self._session_cost_usd += tokens * 0.000003
            return TaskResult(task_id=task.task_id, agent_id=self.identity.agent_id,
                              success=True, output=output, tokens_used=tokens,
                              duration_ms=(time.time()-t0)*1000,
                              metadata={"model": self.model, "format": report.format})
        except Exception as e:
            return TaskResult(task_id=task.task_id, agent_id=self.identity.agent_id,
                              success=False, error=str(e), duration_ms=(time.time()-t0)*1000)

    async def _execute_with_claude(self, task: Task) -> TaskResult:
        return await self.execute(task)

    async def _call_claude(self, user_message: str) -> Tuple[str, int]:
        try:
            import anthropic
            if self._client is None:
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            response = await self._client.messages.create(
                model=self.model, max_tokens=1024,
                system=self._build_system_prompt(),
                messages=[{"role":"user","content":user_message}])
            text = response.content[0].text if response.content else ""
            tokens = response.usage.input_tokens + response.usage.output_tokens
            return text, tokens
        except ImportError:
            return f"[MOCK] Processed: {user_message[:80]}", 50
        except Exception as e:
            return f"[ERROR] {str(e)}", 0

    def session_stats(self) -> Dict:
        s = self.optimizer.session_stats()
        s.update({"total_tokens": self._session_tokens,
                  "total_cost_usd": round(self._session_cost_usd, 4),
                  "task_count": self.state.task_count,
                  "error_rate": f"{self.state.error_rate:.1%}"})
        return s

class AgentFactory:
    def __init__(self, default_api_key: Optional[str] = None):
        self.default_api_key = default_api_key
        self._registry: Dict[str, ClaudeKyberAgent] = {}

    def create(self, name: str, capabilities: set, vsm_level: VSMLevel = VSMLevel.S1,
               depth: int = 1, autonomy: AutonomyLevel = AutonomyLevel.HOTL,
               parent_id: Optional[str] = None, extra_instructions: str = "",
               api_key: Optional[str] = None, model: str = "claude-sonnet-4-6") -> ClaudeKyberAgent:
        if depth > KyberAgent.MAX_DEPTH:
            raise RuntimeError(f"Cannot spawn at depth {depth}: exceeds MAX_DEPTH {KyberAgent.MAX_DEPTH}")
        identity = AgentIdentity(name=name, vsm_level=vsm_level, depth=depth, autonomy=autonomy,
                                 capabilities=set(capabilities), parent_id=parent_id)
        agent = ClaudeKyberAgent(identity=identity, api_key=api_key or self.default_api_key,
                                 model=model, extra_instructions=extra_instructions)
        self._registry[agent.identity.agent_id] = agent
        return agent

    def get(self, agent_id: str): return self._registry.get(agent_id)
    def all_agents(self): return list(self._registry.values())

    def retire(self, agent_id: str):
        agent = self._registry.pop(agent_id, None)
        if agent: agent.state.is_alive = False
