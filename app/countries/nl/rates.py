"""
Netherlands payroll rates for tax year 2026.

Sources (as published, 2025-09 and 2025-11 releases):
- Belastingdienst, "Tarieven en heffingskortingen voorlopige aanslag 2026"
- Belastingdienst, "Nieuwsbrief Loonheffingen 2026" (incl. 2nd/corrected edition)
- Staatscourant, definitieve ZVW-premie 2026

IMPORTANT: these are the *published statutory* rates for 2026. Before this
module is used against real payroll:
  1. Reconcile every figure below against the official Belastingdienst
     "Handboek Loonheffingen 2026" / rekentabellen, not just this summary.
  2. This module currently covers employees who have NOT reached AOW age.
     AOW-age employees use a lower first-bracket rate and a different
     algemene heffingskorting maximum - not yet implemented (see payroll.py).
  3. Whk (Werkhervattingskas) is employer-specific in reality (differentiated
     premium set by Belastingdienst per employer). WHK_SECTOR_AVERAGE below
     is the published *average* rate and must be replaced with each client's
     actual assessed rate before go-live.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TaxBracket:
    lower: float
    upper: float | None  # None = no upper bound
    rate: float


# --- Box 1 income tax (employees below AOW age), 2026 ------------------
BOX1_BRACKETS: tuple[TaxBracket, ...] = (
    TaxBracket(0, 38_883, 0.3575),
    TaxBracket(38_883, 78_426, 0.3756),
    TaxBracket(78_426, None, 0.4950),
)

# --- Algemene heffingskorting (general tax credit), 2026 ---------------
ALGEMENE_HEFFINGSKORTING_MAX = 3_115.0
ALGEMENE_HEFFINGSKORTING_PHASEOUT_START = 29_736.0
ALGEMENE_HEFFINGSKORTING_PHASEOUT_END = 78_426.0
ALGEMENE_HEFFINGSKORTING_PHASEOUT_RATE = 0.06398

# --- Arbeidskorting (labor tax credit), 2026 - piecewise on labor income
@dataclass(frozen=True)
class ArbeidskortingSegment:
    lower: float
    upper: float | None
    base: float
    rate: float  # applied to (income - lower)


ARBEIDSKORTING_SEGMENTS: tuple[ArbeidskortingSegment, ...] = (
    ArbeidskortingSegment(0, 11_965, 0.0, 0.08324),
    ArbeidskortingSegment(11_965, 25_845, 996.0, 0.31009),
    ArbeidskortingSegment(25_845, 45_592, 5_300.0, 0.01950),
    ArbeidskortingSegment(45_592, 132_920, 5_685.0, -0.06510),
    ArbeidskortingSegment(132_920, None, 0.0, 0.0),
)

# --- Employer social insurance premiums, 2026 ---------------------------
AWF_LOW = 0.0274  # permanent contract
AWF_HIGH = 0.0774  # flexible contract
AOF_LOW = 0.0627  # small employer
AOF_HIGH = 0.0763  # large employer
WHK_SECTOR_AVERAGE = 0.0152  # placeholder - replace with client's actual rate
ZVW_EMPLOYER = 0.0610

# SV-loon / bijdrageloon cap: premiums apply only up to this annual amount
MAX_PREMIELOON = 79_409.0
