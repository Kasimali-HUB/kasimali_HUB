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
  2. Arbeidskorting is applied identically regardless of AOW status - no
     AOW-specific arbeidskorting table was found during research. This is
     an assumption, not a confirmed figure; verify before relying on it
     for AOW-age employees.
  3. Whk (Werkhervattingskas) is employer-specific in reality (differentiated
     premium set by Belastingdienst per employer). WHK_SECTOR_AVERAGE below
     is the published *average* rate. employer_cost.py now flags in its
     output whenever this fallback was used instead of a real client rate.
  4. No figure below has been cross-checked against an official Belastingdienst
     worked example yet - box1_tax() bracket-boundary output for the non-AOW
     and AOW (born on/after 1946) tables matches a published reference
     calculation (13,900.67 and 6,940.62 respectively at the 38,883 boundary),
     which is a good sign but is not a substitute for a full reconciliation.
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

# --- Box 1, employees who have reached AOW age, born on/after 1 Jan 1946 -
# Same bracket thresholds as below-AOW-age; only the first-bracket rate is
# lower, because AOW premium is no longer withheld.
BOX1_BRACKETS_AOW_BORN_ON_OR_AFTER_1946: tuple[TaxBracket, ...] = (
    TaxBracket(0, 38_883, 0.1785),
    TaxBracket(38_883, 78_426, 0.3756),
    TaxBracket(78_426, None, 0.4950),
)

# --- Box 1, employees who have reached AOW age, born before 1 Jan 1946 --
# Same rates, but the first bracket extends further (to 41,123).
BOX1_BRACKETS_AOW_BORN_BEFORE_1946: tuple[TaxBracket, ...] = (
    TaxBracket(0, 41_123, 0.1785),
    TaxBracket(41_123, 78_426, 0.3756),
    TaxBracket(78_426, None, 0.4950),
)

# --- Algemene heffingskorting (general tax credit), 2026 ---------------
ALGEMENE_HEFFINGSKORTING_MAX = 3_115.0
ALGEMENE_HEFFINGSKORTING_PHASEOUT_START = 29_736.0
ALGEMENE_HEFFINGSKORTING_PHASEOUT_END = 78_426.0
ALGEMENE_HEFFINGSKORTING_PHASEOUT_RATE = 0.06398

# AOW-age version: lower max, and the phase-out rate is roughly halved
# (published as "a halving of the non-AOW rate" - 3.195% vs 6.398%).
# Same phase-out start/end thresholds as the non-AOW credit.
ALGEMENE_HEFFINGSKORTING_AOW_MAX = 1_556.0
ALGEMENE_HEFFINGSKORTING_AOW_PHASEOUT_RATE = 0.03195

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
