"""
Pseudonymization for anything that may reach the AI layer.

Design choice: HMAC-based, deterministic, one-way.
- Deterministic: the same employee always maps to the same token within a
  tenant, so an AI-assisted triage flow can refer to "EMP-a1b2c3" across
  multiple calls without re-identifying anyone.
- One-way: derived from a secret (app.core.config.pseudonymization_secret)
  that is never given to the AI layer. Without that secret, a token cannot
  be reversed back to an employee ID - it can only be looked up in our own
  database, which is exactly where that lookup should happen.

This module is the concrete enforcement of the privacy boundary, not just
documentation of it: any code path that wants to hand employee data to an
AI-assisted component should only ever be able to reach a token here, never
the underlying employee_id.
"""

import hmac
from hashlib import sha256


def pseudonymize(identifier: str, secret: str, *, prefix: str = "EMP") -> str:
    """
    Derive a stable, non-reversible token for `identifier`.

    `secret` is passed explicitly (rather than imported from settings here)
    so this stays a pure function - easy to test, and impossible to call
    without deliberately supplying the tenant's secret.
    """
    digest = hmac.new(secret.encode(), identifier.encode(), sha256).hexdigest()
    return f"{prefix}-{digest[:10]}"
