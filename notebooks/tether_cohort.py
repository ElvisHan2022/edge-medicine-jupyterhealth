"""
tether_cohort.py
Synthetic postpartum cohort for the Tether demo (step 1 of the synthetic pipeline). This is our official start.

Generates one row per patient after a complicated pregnancy (gestational diabetes,
a hypertensive disorder of pregnancy, or both), together with the protocol timeline
that later steps use to generate observations:

    Phase 1, safety:      weeks 0 to 6, one row per week
    Phase 2, prevention:  months 2 to 12, one row per month

Where the numbers come from
    Every value carries one of three tags, so a reader can see what each rests on:

    [PILOT]     Observed in a published pilot or program cited in the Tether
                proposal. Bracketed numbers are the proposal's reference list.
    [TARGET]    A goal the proposal sets for Tether, not an observed value.
    [ASSUMED]   Chosen for demonstration. Plausible, but not taken from a cited
                pilot; verify before quoting any of these as a figure.

    The pilot results themselves are collected in PILOT_BENCHMARKS below. They are
    the baselines Tether must beat, and later steps compare simulated outcomes
    against them. Call benchmarks_table() to display them.

Nothing in this cohort is evidence about real patients. In particular, any
engagement difference across insurance, language, or race exists only because
CONFIG puts it there; set CONFIG["engagement_effects_on"] = False to generate a
cohort without them.

Usage
    from tether_cohort import generate_cohort, protocol_timeline
    cohort = generate_cohort(n=400, seed=7)
    timeline = protocol_timeline()
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CONFIG = {
    # Enrollment window: deliveries spread over this period            [ASSUMED]
    "delivery_start": "2026-01-01",
    "delivery_end": "2026-06-30",
    # Twelve-month follow-up from delivery                             [TARGET]
    # Proposal Q3: Tether extends care through the full postpartum year.
    "follow_up_days": 365,

    # Complication mix within the Tether population (all have >= 1)   [ASSUMED]
    "complication": {"HDP only": 0.58, "GDM only": 0.30, "HDP + GDM": 0.12},
    # Hypertensive disorder subtype, among patients with HDP            [ASSUMED]
    "hdp_subtype": {
        "gestational hypertension": 0.45,
        "preeclampsia": 0.30,
        "preeclampsia with severe features": 0.17,
        "chronic hypertension with superimposed preeclampsia": 0.08,
    },

    # Demographic and clinical covariates                               [ASSUMED]
    # Approximate US birth shares, not taken from the proposal's references.
    "insurance": {"Medicaid": 0.42, "Private": 0.50, "Uninsured/Other": 0.08},
    "race_ethnicity": {"White": 0.50, "Hispanic": 0.24, "Black": 0.14,
                       "Asian": 0.06, "Other/Multiracial": 0.06},
    "language": {"English": 0.85, "Spanish": 0.11, "Other": 0.04},
    "p_cesarean": 0.32,
    "p_nulliparous": 0.40,
    "p_owns_wearable": 0.40,

    # Enrollment among eligible patients                                [TARGET]
    # Proposal target is 65%, against 37% in a year-long Pittsburgh pilot [30].
    # Bedside enrollment is the lever: 99% of women with GDM completed a glucose
    # test offered two days after delivery, versus 68% at 4 to 12 weeks [43].
    "p_enrolled": 0.65,

    # Engagement propensity (log-odds scale, used later to simulate dropout)
    # The DIRECTION of each effect follows the proposal's predictors (insurance,
    # parity, delivery mode, depression scores) and its concern about who opts
    # in; the SIZE of each effect is [ASSUMED]. Depression is associated with
    # missed postpartum care [14].
    "engagement_effects_on": True,
    "engagement_intercept": 1.2,
    "engagement_effects": {
        "insurance=Medicaid": -0.35,
        "insurance=Uninsured/Other": -0.55,
        "language=Spanish": -0.25,
        "language=Other": -0.35,
        "multiparous": -0.20,
        "cesarean": -0.10,
        "epds_baseline_per_point": -0.04,
        "owns_wearable": 0.25,
    },
}

# EPDS screening points                                                 [ASSUMED]
# The proposal specifies the Edinburgh Postnatal Depression Scale [45] at
# "scheduled points" without naming them; these are our placeholder schedule.
EPDS_WEEKS = [1, 5]      # week 1 (first home week) and week 5 (the 6-week visit)
EPDS_MONTHS = [3, 6, 12]

# Retention checkpoints                                                 [TARGET]
# Proposal: retention is measured at six weeks, six months, and twelve months.
RETENTION_CHECKPOINTS = {"6 weeks": 42, "6 months": 182, "12 months": 365}

# Published pilot and program results cited in the proposal.           [PILOT]
# These are the baselines Tether is measured against. "tether_target" is the
# proposal's goal where one is stated; None means the proposal sets no target.
PILOT_BENCHMARKS = [
    {"metric": "Enrollment among eligible patients",
     "pilot_value": "37%", "source": "Year-long Pittsburgh pilot [30]",
     "tether_target": "65%"},
    {"metric": "Lost to follow-up within 6 weeks",
     "pilot_value": "35.8%", "source": "University of Florida program [25]",
     "tether_target": "75% retained at 12 months"},
    {"metric": "Glucose test completion after GDM",
     "pilot_value": "99% at 2 days vs 68% at 4 to 12 weeks",
     "source": "Rhode Island hospital [43]", "tether_target": None},
    {"metric": "Postpartum primary care attendance",
     "pilot_value": "57 to 60%", "source": "[8]", "tether_target": "75%"},
    {"metric": "Glucose screening after GDM (checkup attendees, 2022)",
     "pilot_value": "55.8%", "source": "National data [10]", "tether_target": "75%"},
    {"metric": "Incident chronic hypertension at 12 months",
     "pilot_value": "22%", "source": "Year-long Pittsburgh pilot [30]",
     "tether_target": None},
    {"metric": "BP-related readmission reduction",
     "pilot_value": "50% reduction", "source": "Heart Safe Motherhood [21]",
     "tether_target": "Benchmark to match"},
    {"metric": "Emergency visits, remote monitoring vs standard care",
     "pilot_value": "9.0% vs 4.4%", "source": "Meta-analysis of 4 RCTs [47]",
     "tether_target": None},
    {"metric": "Readmission if no early postpartum weight loss",
     "pilot_value": "14.1% vs 4.5 to 5.8%", "source": "[44]",
     "tether_target": None},
]


def _draw(rng, mapping: dict, n: int) -> np.ndarray:
    keys, probs = zip(*mapping.items())
    probs = np.array(probs, dtype=float)
    return rng.choice(keys, size=n, p=probs / probs.sum())


def generate_cohort(n: int = 400, seed: int = 7, config: dict | None = None) -> pd.DataFrame:
    """Return one row per synthetic patient with baseline characteristics at discharge."""
    cfg = {**CONFIG, **(config or {})}
    rng = np.random.default_rng(seed)

    start = pd.Timestamp(cfg["delivery_start"])
    span = (pd.Timestamp(cfg["delivery_end"]) - start).days
    delivery = start + pd.to_timedelta(rng.integers(0, span + 1, n), unit="D")

    complication = _draw(rng, cfg["complication"], n)
    has_hdp = np.char.find(complication.astype(str), "HDP") >= 0
    has_gdm = np.char.find(complication.astype(str), "GDM") >= 0
    hdp_subtype = np.where(has_hdp, _draw(rng, cfg["hdp_subtype"], n), "none")
    severe = np.isin(hdp_subtype, ["preeclampsia with severe features",
                                   "chronic hypertension with superimposed preeclampsia"])

    age = np.clip(rng.normal(30.5, 5.5, n), 18, 46).round().astype(int)
    bmi = np.clip(rng.normal(29 + 2 * has_gdm, 6, n), 18, 55).round(1)
    insurance = _draw(rng, cfg["insurance"], n)
    race = _draw(rng, cfg["race_ethnicity"], n)
    language = _draw(rng, cfg["language"], n)
    cesarean = rng.random(n) < cfg["p_cesarean"] + 0.08 * severe
    nulliparous = rng.random(n) < cfg["p_nulliparous"]
    owns_wearable = rng.random(n) < cfg["p_owns_wearable"] + 0.10 * (insurance == "Private")

    # Discharge blood pressure: higher with HDP and with severe subtypes [ASSUMED]
    # Phase 1 alerts apply validated threshold rules from Heart Safe Motherhood
    # and POP-HT [21, 23]; the distributions here only need to cross them.
    sbp = rng.normal(118, 9, n) + has_hdp * rng.normal(16, 6, n) + severe * rng.normal(8, 4, n)
    dbp = rng.normal(74, 7, n) + has_hdp * rng.normal(10, 4, n) + severe * rng.normal(5, 3, n)
    on_antihypertensive = has_hdp & ((sbp >= 150) | (dbp >= 100) | severe)

    # Baseline EPDS (0 to 30)                                          [ASSUMED]
    # >= 13 is the commonly used screen-positive cutoff for the EPDS [45].
    epds = np.clip(rng.gamma(2.2, 3.0, n) + 1.5 * severe, 0, 30).round().astype(int)

    # Engagement propensity, kept as a latent column for the dropout step
    lp = np.full(n, cfg["engagement_intercept"], dtype=float)
    if cfg["engagement_effects_on"]:
        e = cfg["engagement_effects"]
        lp += e["insurance=Medicaid"] * (insurance == "Medicaid")
        lp += e["insurance=Uninsured/Other"] * (insurance == "Uninsured/Other")
        lp += e["language=Spanish"] * (language == "Spanish")
        lp += e["language=Other"] * (language == "Other")
        lp += e["multiparous"] * (~nulliparous)
        lp += e["cesarean"] * cesarean
        lp += e["epds_baseline_per_point"] * epds
        lp += e["owns_wearable"] * owns_wearable
    lp += rng.normal(0, 0.5, n)  # unexplained individual variation

    cohort = pd.DataFrame({
        "patient_id": [f"TETH-{i:04d}" for i in range(1, n + 1)],
        "delivery_date": delivery.normalize(),
        "follow_up_end": (delivery + pd.Timedelta(days=cfg["follow_up_days"])).normalize(),
        "complication": complication,
        "has_hdp": has_hdp,
        "has_gdm": has_gdm,
        "hdp_subtype": hdp_subtype,
        "age": age,
        "bmi_prepregnancy": bmi,
        "parity": np.where(nulliparous, "nulliparous", "multiparous"),
        "delivery_mode": np.where(cesarean, "cesarean", "vaginal"),
        "insurance": insurance,
        "race_ethnicity": race,
        "language": language,
        "discharge_sbp": sbp.round().astype(int),
        "discharge_dbp": dbp.round().astype(int),
        "on_antihypertensive": on_antihypertensive,
        "epds_baseline": epds,
        "epds_positive_baseline": epds >= 13,
        # Device kit issued at bedside enrollment (proposal Q3); over-the-counter
        # glucose sensor for GDM [34, 35]; wearable only if already owned
        "device_bp_cuff": True,
        "device_glucose_sensor": has_gdm,
        "device_wearable": owns_wearable,
        "enrolled": rng.random(n) < cfg["p_enrolled"],
        "engagement_logit": lp.round(3),
    })
    return cohort


def protocol_timeline(follow_up_days: int = 365) -> pd.DataFrame:
    """Return the protocol grid: weekly periods for weeks 0 to 6, monthly for months 2 to 12."""
    rows = []
    for w in range(0, 6):  # week 0 = days 0 to 6, ..., week 5 = days 35 to 41
        rows.append({
            "phase": "1 safety", "period": f"week {w}", "unit": "week",
            "start_day": 7 * w, "end_day": 7 * w + 6,
            "bp_readings_expected": 14,          # twice daily home BP [ASSUMED]
            "glucose_expected": "continuous (GDM)",
            "epds_due": w in EPDS_WEEKS,
            "alerting": "threshold rules only",  # [21, 23]; no model overrides
        })
    for m in range(2, 13):  # month 2 = days 42 to 71, ..., month 12 ends at follow-up
        start = 42 + 30 * (m - 2)
        end = follow_up_days - 1 if m == 12 else start + 29
        rows.append({
            "phase": "2 prevention", "period": f"month {m}", "unit": "month",
            "start_day": start, "end_day": end,
            "bp_readings_expected": 8,           # twice weekly home BP [ASSUMED]
            "glucose_expected": "screening prompt (GDM)" if m in (2, 3, 12) else "none",
            "epds_due": m in EPDS_MONTHS,
            "alerting": "baseline-trajectory tracking",
        })
    tl = pd.DataFrame(rows)
    tl["retention_checkpoint"] = ""
    for label, day in RETENTION_CHECKPOINTS.items():
        tl.loc[(tl.start_day <= day - 1) & (tl.end_day >= day - 1), "retention_checkpoint"] = label
    return tl


def benchmarks_table() -> pd.DataFrame:
    """Published pilot baselines and Tether targets, for display in the demo."""
    return pd.DataFrame(PILOT_BENCHMARKS).fillna("Not set")


def summarize(cohort: pd.DataFrame) -> pd.DataFrame:
    """Compact table-one style summary for the demo."""
    parts = []
    for col in ["complication", "hdp_subtype", "insurance", "race_ethnicity",
                "language", "delivery_mode", "parity"]:
        s = cohort[col].value_counts(normalize=True).mul(100).round(1)
        parts.append(pd.DataFrame({"variable": col, "level": s.index, "percent": s.values}))
    return pd.concat(parts, ignore_index=True)


if __name__ == "__main__":
    c = generate_cohort()
    print(c.head())
    print(summarize(c))
    print(protocol_timeline())
    print(benchmarks_table())