"""Anti-pattern audit.

Verifies, by static AST analysis, that the agentic loop does NOT:
- use string-membership tests against text content to drive control flow
- use an integer-literal iteration cap as its primary stopping mechanism
- omit reference to `stop_reason` as the loop-breaking signal

And that the package broadly does not branch on `claim_type` equality
outside of the tool-schema definitions and the cost-estimate module.

Each test parses the relevant file with `ast` and walks the tree. There are
no runtime imports of claims_intake here — the audit is static, so it works
even if loop.py / tools.py do not run end-to-end.
"""

from __future__ import annotations

import ast
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "claims_intake"
LOOP_PY = PKG / "loop.py"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


# ---------------------------------------------------------------------------
# Anti-pattern 1 — no string-membership tests against assistant text in the loop
# ---------------------------------------------------------------------------
def test_no_string_membership_against_text_in_loop() -> None:
    """No `"some_token" in <something>` expressions in loop.py.

    Heuristic: any `ast.Compare` node using `ast.In` whose `left` operand is a
    string `ast.Constant` is flagged. The loop has no legitimate reason to test
    for the presence of a magic string inside the model's output — that would be
    natural-language-driven control flow.
    """
    tree = _parse(LOOP_PY)
    offenders: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not any(isinstance(op, ast.In) for op in node.ops):
            continue
        if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            offenders.append(ast.unparse(node))

    assert not offenders, (
        "Found string-membership control flow in loop.py: " + "; ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Anti-pattern 2 — no integer-literal iteration cap as the primary stop mechanism
# ---------------------------------------------------------------------------
def test_no_integer_literal_iteration_cap_in_loop() -> None:
    """No `for _ in range(<int literal>)` and no `while <var> < <int literal>` in loop.py.

    Token/wall-clock/config-sourced budgets are explicitly allowed because they
    read their cap from a `Budget` instance (an attribute access or a function
    arg), not from a literal. If you need a cap, pass it in.
    """
    tree = _parse(LOOP_PY)
    offenders: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            iter_expr = node.iter
            if (
                isinstance(iter_expr, ast.Call)
                and isinstance(iter_expr.func, ast.Name)
                and iter_expr.func.id == "range"
                and any(
                    isinstance(arg, ast.Constant) and isinstance(arg.value, int)
                    for arg in iter_expr.args
                )
            ):
                offenders.append(ast.unparse(node))

        if isinstance(node, ast.While) and isinstance(node.test, ast.Compare):
            test = node.test
            if any(
                isinstance(comp, ast.Constant) and isinstance(comp.value, int)
                for comp in test.comparators
            ):
                offenders.append(ast.unparse(node))

    assert not offenders, (
        "Found literal iteration cap in loop.py; use a Budget instead: "
        + "; ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Positive evidence — stop_reason is the value that breaks the while loop
# ---------------------------------------------------------------------------
def test_stop_reason_is_loop_control() -> None:
    """loop.py references `stop_reason` AND a `while` loop exits via return/raise on it."""
    tree = _parse(LOOP_PY)

    has_stop_reason_ref = any(
        (isinstance(node, ast.Attribute) and node.attr == "stop_reason")
        or (isinstance(node, ast.Name) and node.id == "stop_reason")
        for node in ast.walk(tree)
    )
    assert has_stop_reason_ref, "loop.py must reference stop_reason"

    while_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.While)]
    assert while_nodes, "loop.py must use a while loop for the agentic loop"

    loop_exits_on_stop_reason = False
    for while_node in while_nodes:
        body_src = "\n".join(ast.unparse(stmt) for stmt in while_node.body)
        if "stop_reason" in body_src and (
            "return" in body_src or "raise" in body_src
        ):
            loop_exits_on_stop_reason = True
            break

    assert loop_exits_on_stop_reason, (
        "A while-loop body in loop.py must exit via return/raise based on stop_reason"
    )


# ---------------------------------------------------------------------------
# Decision-tree-in-Python — no `if claim_type == "..."` branches in the package
# ---------------------------------------------------------------------------
def test_no_claim_type_equality_branching_in_package() -> None:
    """Decision logic about claim type lives in the model, not in Python.

    tools.py is exempt (it defines the enum in input_schema).
    pricing.py is exempt (it may map claim_type to per-queue cost weights).
    """
    offenders: list[str] = []

    for path in PKG.rglob("*.py"):
        if path.name in {"tools.py", "pricing.py", "__init__.py"}:
            continue

        tree = _parse(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            if not any(isinstance(op, ast.Eq) for op in node.ops):
                continue

            left = node.left
            left_is_claim_type = (
                isinstance(left, ast.Name)
                and left.id == "claim_type"
                or isinstance(left, ast.Attribute)
                and left.attr == "claim_type"
            )
            if not left_is_claim_type:
                continue

            right_has_string = any(
                isinstance(comp, ast.Constant) and isinstance(comp.value, str)
                for comp in node.comparators
            )
            if right_has_string:
                rel = path.relative_to(PKG.parent)
                offenders.append(f"{rel}:{node.lineno}: {ast.unparse(node)}")

    assert not offenders, (
        "Found claim_type equality branching in Python. "
        "Move this decision into the model via tool calls: "
        + "; ".join(offenders)
    )
