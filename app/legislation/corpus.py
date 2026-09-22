"""
Legislation corpus for the Netherlands, tax year 2026.

Everything in this file is a paraphrased summary of published, public
statutory figures (Belastingdienst tarieven/heffingskortingen releases,
Nieuwsbrief Loonheffingen 2026, Staatscourant). No client or employee data
of any kind belongs in this file, or in anything derived from it - that's
what keeps this module on the safe side of the AI/data boundary from the
rest of the platform.

This is a starting corpus, not a complete legal reference. Expand it
deliberately, one dated, sourced entry at a time - don't paste raw statute
text in here; keep summarizing in plain language so it stays reviewable.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LegislationDoc:
    doc_id: str
    title: str
    text: str
    citation: str


NL_LEGISLATION_CORPUS: tuple[LegislationDoc, ...] = (
    LegislationDoc(
        doc_id="nl-box1-brackets-2026",
        title="Box 1 income tax brackets (2026)",
        text=(
            "For employees who have not reached state pension (AOW) age, Box 1 "
            "wage income is taxed in three bands for 2026: 35.75% up to "
            "EUR 38,883; 37.56% from EUR 38,883 up to EUR 78,426; and 49.50% "
            "above EUR 78,426. These rates already include the combined "
            "national insurance premiums (AOW/ANW/Wlz) for the first band, so "
            "no separate national insurance deduction is applied on top."
        ),
        citation="Belastingdienst, Tarieven en heffingskortingen voorlopige aanslag 2026",
    ),
    LegislationDoc(
        doc_id="nl-box1-brackets-aow-2026",
        title="Box 1 income tax brackets for AOW-age employees (2026)",
        text=(
            "Employees who have reached AOW age no longer pay the AOW premium, "
            "so their first Box 1 band is taxed at 17.85% instead of 35.75%. "
            "For those born on or after 1 January 1946, this lower rate applies "
            "up to EUR 38,883, the same threshold as the non-AOW brackets. For "
            "those born before 1 January 1946, the lower-rate band extends "
            "further, up to EUR 41,123. Above these thresholds, both groups pay "
            "the same 37.56% and 49.50% rates as non-AOW employees."
        ),
        citation="Belastingdienst, Tarieven en heffingskortingen voorlopige aanslag 2026",
    ),
    LegislationDoc(
        doc_id="nl-algemene-heffingskorting-2026",
        title="Algemene heffingskorting (general tax credit), 2026",
        text=(
            "Every Dutch taxpayer is entitled to the algemene heffingskorting, "
            "which reduces income tax and national insurance premiums owed. For "
            "2026, the maximum credit is EUR 3,115 for income up to "
            "EUR 29,736. Between EUR 29,736 and EUR 78,426, the credit is "
            "reduced by 6.398% of income above the threshold. Above "
            "EUR 78,426, the credit is EUR 0. For AOW-age taxpayers, the "
            "maximum credit is lower, at EUR 1,556, and it phases out over the "
            "same income range at roughly half the non-AOW reduction rate "
            "(3.195%)."
        ),
        citation="Belastingdienst, Tarieven en heffingskortingen voorlopige aanslag 2026",
    ),
    LegislationDoc(
        doc_id="nl-arbeidskorting-2026",
        title="Arbeidskorting (labor tax credit), 2026",
        text=(
            "The arbeidskorting is a tax credit available to anyone with labor "
            "income (wages, sick-pay benefits, or business profit). For 2026 it "
            "builds up from 8.324% of income up to EUR 11,965, continues "
            "building at 31.009% up to EUR 25,845 and 1.950% up to EUR 45,592, "
            "reaches a maximum of EUR 5,685, then phases out at 6.510% of "
            "income above EUR 45,592 until it reaches EUR 0 at EUR 132,920."
        ),
        citation="Belastingdienst, Tarieven en heffingskortingen voorlopige aanslag 2026",
    ),
    LegislationDoc(
        doc_id="nl-employer-premiums-2026",
        title="Employer social insurance premiums, 2026",
        text=(
            "Employers pay several premiums on top of gross wages, up to an "
            "annual wage cap of EUR 79,409 per employee for 2026. The AWf "
            "(unemployment fund) premium is 2.74% for employees on a permanent "
            "contract and 7.74% for flexible contracts. The Aof "
            "(disability fund) premium is 6.27% for small employers and 7.63% "
            "for large employers. The Whk (return-to-work fund) premium "
            "averages 1.52% across sectors in 2026, but is actually set "
            "individually per employer by the Belastingdienst - the sector "
            "average should only be used as a placeholder until a client's "
            "actual assessed rate is known. The employer's Zvw (health "
            "insurance) contribution is 6.10% of wages up to the same cap."
        ),
        citation=(
            "Belastingdienst premie-overzicht 2026; Staatscourant, "
            "Definitieve percentages ZVW-premie 2026"
        ),
    ),
)
