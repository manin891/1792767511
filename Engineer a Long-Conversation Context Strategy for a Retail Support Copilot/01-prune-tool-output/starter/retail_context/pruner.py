"""Deterministic tool-output pruning for the verbose `lookup_order` response.

The "Tool Context Pruning" pattern: application-side filtering
of a verbose tool result so only the fields needed for the immediate decision survive
into context. For return/refund reasoning, exactly five fields matter — order identity,
when it was placed, what it cost, whether it shipped, and the return-window deadline.

# Why each kept field is the only one that matters for return/refund reasoning:
#   - order_id: identifies the exact order record the decision applies to.
#   - order_date: anchors return-window calculation from the purchase date.
#   - order_total_usd: bounds potential refund amount and approval thresholds.
#   - fulfillment_status: distinguishes cancellation paths from post-shipment returns.
#   - return_eligible_until: provides the hard deadline for return eligibility.

Implementation: deterministic field selection (no LLM call). The pruner has no
`anthropic` import — enforced by an AST audit.
"""
from __future__ import annotations

# These are the only fields the pruner returns; everything else in the raw
# response is dropped. The output dict preserves this declaration order.
#
# The 5 fields: order_id, order_date, order_total_usd, fulfillment_status,
# return_eligible_until — chosen because they are the *only* fields needed for
# the agent's return/refund decision.
KEPT_FIELDS: tuple[str, ...] = (
    "order_id",
    "order_date",
    "order_total_usd",
    "fulfillment_status",
    "return_eligible_until",
)


class PrunerMissingFieldError(KeyError):
    """Raised when the raw tool response is missing one of the required kept fields."""


def prune_lookup_order(raw: dict) -> dict:
    missing = [field for field in KEPT_FIELDS if field not in raw]
    if missing:
        raise PrunerMissingFieldError(
            f"lookup_order response missing required field(s): {', '.join(missing)}"
        )

    return {field: raw[field] for field in KEPT_FIELDS}
