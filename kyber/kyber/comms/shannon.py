"""KYBER Shannon Optimizer — Token entropy minimization for agent comms"""
import json, math, re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# ─── TOON: Token-Oriented Object Notation (~72% fewer tokens than JSON) ───────
def to_toon(data: Dict[str, Any], prefix: str = "") -> str:
    parts = []
    for k, v in data.items():
        fk = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict): parts.append(to_toon(v, fk))
        elif isinstance(v, bool): parts.append(f"{fk}={'T' if v else 'F'}")
        elif v is None: parts.append(f"{fk}=-")
        elif isinstance(v, list): parts.append(f"{fk}=[{','.join(str(i) for i in v)}]")
        else: parts.append(f"{fk}={v}")
    return "|".join(parts)

def from_toon(s: str) -> Dict[str, Any]:
    result = {}
    for part in s.split("|"):
        if "=" not in part: continue
        k, v = part.split("=", 1)
        keys = k.split(".")
        target = result
        for key in keys[:-1]: target = target.setdefault(key, {})
        lk = keys[-1]
        if v == "T": target[lk] = True
        elif v == "F": target[lk] = False
        elif v == "-": target[lk] = None
        elif v.startswith("[") and v.endswith("]"): target[lk] = v[1:-1].split(",") if len(v) > 2 else []
        elif re.match(r'^-?\d+$', v): target[lk] = int(v)
        elif re.match(r'^-?\d+\.\d+$', v): target[lk] = float(v)
        else: target[lk] = v
    return result

# ─── Entropy Analysis ─────────────────────────────────────────────────────────
def calculate_entropy(text: str) -> float:
    if not text: return 0.0
    from collections import Counter
    counts = Counter(text); n = len(text)
    return -sum((c/n)*math.log2(c/n) for c in counts.values())

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def detect_format(text: str) -> str:
    s = text.strip()
    if "|" in s and "=" in s and not s.startswith("{"): return "toon"
    if s.startswith("{") or s.startswith("["): return "json"
    if s.startswith("---") or re.search(r'^\w+:\s', s, re.M): return "yaml"
    if s.startswith("<"): return "xml"
    if re.search(r'^\w+,', s): return "csv"
    return "prose"

FORMAT_EFFICIENCY = {"toon": 0.95, "csv": 0.90, "yaml": 0.72, "json": 0.65, "xml": 0.40, "prose": 0.20}

@dataclass
class EntropyReport:
    raw_text: str; char_count: int; estimated_tokens: int
    shannon_entropy: float; redundancy: float; format: str
    efficiency_score: float; suggestion: Optional[str] = None

def analyze_message(text: str) -> EntropyReport:
    H = calculate_entropy(text)
    H_max = math.log2(max(len(set(text)), 2))
    redundancy = 1 - (H / H_max) if H_max > 0 else 0
    fmt = detect_format(text)
    efficiency = FORMAT_EFFICIENCY.get(fmt, 0.5)
    tokens = estimate_tokens(text)
    suggestion = None
    if fmt == "prose" and tokens > 50: suggestion = "Convert to TOON for ~72% token reduction"
    elif fmt == "json" and tokens > 20: suggestion = "Convert to TOON for ~35% token reduction"
    elif fmt == "xml": suggestion = "Convert to JSON or TOON immediately"
    return EntropyReport(raw_text=text, char_count=len(text), estimated_tokens=tokens,
                         shannon_entropy=H, redundancy=redundancy, format=fmt,
                         efficiency_score=efficiency, suggestion=suggestion)

# ─── Optimizer ────────────────────────────────────────────────────────────────
class ShannonOptimizer:
    def __init__(self):
        self._session_tokens_saved = 0; self._session_messages = 0

    def compress(self, data: Any, target: str = "agent") -> Tuple[str, EntropyReport]:
        if target == "human":
            text = json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
        elif target == "log":
            text = json.dumps(data, separators=(',',':')) if isinstance(data, dict) else str(data)
        else:
            text = to_toon(data) if isinstance(data, dict) else json.dumps(data, separators=(',',':'))
        report = analyze_message(text)
        json_tokens = estimate_tokens(json.dumps(data, separators=(',',':')) if isinstance(data, dict) else str(data))
        self._session_tokens_saved += max(0, json_tokens - report.estimated_tokens)
        self._session_messages += 1
        return text, report

    def decompress(self, text: str) -> Any:
        fmt = detect_format(text)
        if fmt == "toon": return from_toon(text)
        if fmt == "json": return json.loads(text)
        return text

    def session_stats(self) -> Dict:
        return {"messages_processed": self._session_messages,
                "tokens_saved": self._session_tokens_saved,
                "estimated_cost_saved_usd": round(self._session_tokens_saved * 0.000003, 4)}

    def format_prompt_header(self, agent_name: str, context: Dict) -> str:
        caps = context.get("capabilities", [])
        return "\n".join(["---", f"agent: {agent_name}",
            f"vsm: {context.get('vsm_level','S1')}", f"depth: {context.get('depth',1)}",
            f"autonomy: {context.get('autonomy','hotl')}",
            f"capabilities: [{', '.join(caps)}]",
            f"spend_limit: ${context.get('spend_limit_usd',10):.0f}",
            "comms_format: toon", "---"])

# ─── Prompt constants ─────────────────────────────────────────────────────────
KYBER_AGENT_HEADER = """---
# KYBER AGENT CONSTITUTION v1.0
comms:
  internal: toon          # agent→agent: use TOON format (72% fewer tokens)
  external: prose         # agent→human: natural language
  max_tokens_per_msg: 512
vsm:
  law: "Conant-Ashby — you ARE a model of your domain"
  ashby: "Only accept tasks within your variety. Escalate what exceeds it."
  beer:  "Emit algedonic signals: pain on failure, pleasure on achievement."
  maturana: "Conserve your organization. Adapt your structure."
governance:
  hitl_threshold: 0.07
  spend_gate: 1000
  recursion_max: 3
---"""

TOON_GUIDE = """
TOON FORMAT for agent-to-agent comms (72% fewer tokens than JSON):
  KEY=VALUE|KEY2=VALUE2   (pipe-separated pairs)
  bool: T or F | null: - | array: [a,b,c] | nested: parent.child=val
  Example: id=abc123|ok=T|ms=142|err=-
"""
