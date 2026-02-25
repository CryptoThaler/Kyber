"""KYBER Policy Engine — S5 (invariant charter) + S3* (sporadic audit)"""
from __future__ import annotations
import hashlib, json, random, time, uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from kyber.core.vsm import AlgedonicBus, AlgedonicSignal, AutonomyLevel, KyberAgent, Task, TaskResult, VSMLevel

@dataclass
class Charter:
    name: str; mission: str; values: List[str]
    spend_limits: Dict[str, float]; hitl_thresholds: Dict[str, Any]; prohibited: List[str]
    version: str = "1.0.0"; created_at: float = field(default_factory=time.time)
    amended_at: Optional[float] = None; amender_id: Optional[str] = None

    @property
    def hash(self) -> str:
        content = json.dumps({"name":self.name,"mission":self.mission,"values":sorted(self.values),
            "spend_limits":self.spend_limits,"hitl_thresholds":self.hitl_thresholds,
            "prohibited":sorted(self.prohibited),"version":self.version}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def requires_hitl(self, action: str, amount_usd: float = 0.0) -> Tuple[bool, str]:
        if action in self.prohibited: return True, f"Action '{action}' is prohibited"
        if amount_usd > self.spend_limits.get("auto", 0): return True, f"Amount ${amount_usd} exceeds auto limit"
        if action in self.hitl_thresholds: return True, f"Action '{action}' always requires human approval"
        return False, ""

def default_charter() -> Charter:
    return Charter(
        name="Kyber Default Organization",
        mission="Accomplish assigned tasks autonomously within charter constraints",
        values=["safety_first","minimal_footprint","human_oversight_respected","truthful_reporting","reversible_actions_preferred"],
        spend_limits={"auto":100.0,"hotl":1000.0,"hitl":10000.0},
        hitl_thresholds={"deploy_new_agent_class":True,"external_legal_commitment":True,
                         "charter_amendment":True,"mass_communication":True,"irreversible_deletion":True},
        prohibited=["modify_own_charter","disable_algedonic_bus","suppress_human_alerts",
                    "forge_agent_identity","exceed_recursion_depth"])

class PolicyEngine:
    def __init__(self, charter: Optional[Charter] = None):
        self.charter = charter or default_charter()
        self._decision_log: List[Dict] = []
        self._registered_agents: Dict[str, str] = {}
        self._human_approvals: Dict[str, bool] = {}

    def check_action(self, agent_id: str, action: str, amount_usd: float = 0.0,
                     context: Optional[Dict] = None) -> Tuple[bool, str, AutonomyLevel]:
        requires, reason = self.charter.requires_hitl(action, amount_usd)
        if requires:
            self._log(agent_id, action, "HITL_REQUIRED", reason)
            return False, reason, AutonomyLevel.HITL
        if amount_usd > self.charter.spend_limits.get("auto", 0):
            reason = f"Amount ${amount_usd} requires HOTL notification"
            self._log(agent_id, action, "HOTL_REQUIRED", reason)
            return True, reason, AutonomyLevel.HOTL
        self._log(agent_id, action, "APPROVED_AUTO", "Within charter")
        return True, "Within charter limits", AutonomyLevel.AUTO

    def register_agent(self, agent: KyberAgent) -> bool:
        self._registered_agents[agent.identity.agent_id] = agent.identity.charter_hash or "unset"
        return True

    def _log(self, agent_id, action, outcome, reason):
        self._decision_log.append({"timestamp":time.time(),"agent_id":agent_id,
                                   "action":action,"outcome":outcome,"reason":reason})

    def audit_log(self, n: int = 50) -> List[Dict]:
        return self._decision_log[-n:]

class S3StarAuditor:
    """Beer's S3* — sporadic compliance sampling, bypasses normal hierarchy"""
    def __init__(self, policy: PolicyEngine, bus: AlgedonicBus, sample_rate: float = 0.15):
        self.policy = policy; self.bus = bus; self.sample_rate = sample_rate
        self._audit_results: List[Dict] = []; self._drift_patterns: Dict[str, int] = {}

    async def audit_result(self, result: TaskResult, task: Task) -> Optional[Dict]:
        if random.random() > self.sample_rate: return None
        finding = await self._check_compliance(result, task)
        if finding:
            self._audit_results.append(finding)
            pattern = finding.get("pattern", "unknown")
            self._drift_patterns[pattern] = self._drift_patterns.get(pattern, 0) + 1
            await self.bus.emit(AlgedonicSignal(
                source_id="s3-star-auditor", source_level=VSMLevel.S3_STAR,
                signal_type="pain", severity=6 if finding["severity"]=="high" else 4,
                payload=finding, message=f"S3* audit: {finding['description']}"))
        return finding

    async def _check_compliance(self, result: TaskResult, task: Task) -> Optional[Dict]:
        if result.output and isinstance(result.output, str):
            for p in self.policy.charter.prohibited:
                if p.replace("_"," ") in result.output.lower():
                    return {"timestamp":time.time(),"task_id":task.task_id,"agent_id":result.agent_id,
                            "severity":"high","pattern":"prohibited_content",
                            "description":f"Output contains prohibited reference: {p}"}
        if result.tokens_used > 4000:
            return {"timestamp":time.time(),"task_id":task.task_id,"agent_id":result.agent_id,
                    "severity":"medium","pattern":"token_anomaly",
                    "description":f"Token spike: {result.tokens_used} for '{task.task_type}'"}
        return None

    def drift_report(self) -> Dict:
        return {"audits_performed":len(self._audit_results),
                "drift_patterns":sorted(self._drift_patterns.items(),key=lambda x:-x[1])[:10],
                "recent_findings":self._audit_results[-5:]}
