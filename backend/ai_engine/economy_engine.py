from dataclasses import dataclass


@dataclass(slots=True)
class WhatIfInput:
    energy_kwh_delta: float
    feed_kg_delta: float
    mortality_delta_birds: int
    revenue_delta: float


@dataclass(slots=True)
class WhatIfResult:
    delta_profit: float
    approved: bool
    reason: str


def evaluate_command(payload: WhatIfInput) -> WhatIfResult:
    delta_cost = payload.energy_kwh_delta + payload.feed_kg_delta + max(payload.mortality_delta_birds, 0)
    delta_profit = payload.revenue_delta - delta_cost
    approved = delta_profit >= 0
    reason = "APPROVED" if approved else "BLOCKED: Δprofit < 0"
    return WhatIfResult(delta_profit=round(delta_profit, 2), approved=approved, reason=reason)
