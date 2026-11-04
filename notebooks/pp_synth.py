"""Synthetic postpartum blood pressure cohort for the Edge Medicine prototype.
 
Generates patients with hypertensive disorders of pregnancy (HDP) who are
enrolled in remote blood pressure monitoring at delivery discharge, together
with their home readings in the Open mHealth blood-pressure:4.0 format used by
JupyterHealth Exchange.
 
Every parameter is labeled with its source. Parameters marked ASSUMPTION are
design choices with no direct empirical anchor and should be read as such.
Because the cohort is simulated, any model trained on it demonstrates a
pipeline; it does not establish external validity.
 
Sources
-------
[S1] Hauspurg et al., JAMA Cardiology 2024 (n=2705 remote-monitored HDP):
     81.8% ongoing hypertension after discharge, about 14% severe hypertension.
[S2] Indianapolis RCT, Obstet Gynecol 2023;142:855: 91.7% ascertainment within
     10 days with remote monitoring; median 14 days of use (IQR 9-16).
[S3] Attendance predictors, n=1041 (Thieme, 2021): aOR 0.68 for non-Hispanic
     Black vs White; aOR 0.65 for public vs private insurance.
[S4] Pittsburgh program (Lemon et al., 2024): enrollees more likely White and
     commercially insured.
[S5] Hoppe et al., Pregnancy Hypertens 2019: BP falls after delivery, then
     rises to a peak between postpartum days 3 and 6.
[S6] POP-HT (Kitt et al., JAMA 2023): 40% gestational hypertension, 60%
     preeclampsia; once-daily readings, twice daily when out of range.
"""
 
from __future__ import annotations
 
import uuid
from dataclasses import dataclass, field
 
import numpy as np
import pandas as pd
 
FOLLOW_UP_DAYS = 42  # ACOG comprehensive postpartum visit by 6 weeks
 
 
@dataclass
class CohortParams:
    n_patients: int = 400
    seed: int = 7
    start_date: str = "2026-09-01"
 
    # Population mix. ASSUMPTION, loosely shaped on a diverse urban
    # academic center; edit to match a target site.
    race_probs: dict = field(default_factory=lambda: {
        "Black": 0.24, "Hispanic": 0.26, "White": 0.32, "Asian": 0.18})
    p_public_insurance: float = 0.45          # ASSUMPTION
    p_non_english: float = 0.15               # ASSUMPTION
    subtype_probs: dict = field(default_factory=lambda: {
        "gestational_hypertension": 0.40,     # [S6]
        "preeclampsia": 0.45,                 # [S6], split by ASSUMPTION
        "preeclampsia_severe": 0.15})
 
    # Engagement. Odds ratios from [S3] are for in-person attendance; applying
    # them to remote engagement is an ASSUMPTION the pitch must state.
    target_ascertainment_10d: float = 0.88    # between [S2] arms, ASSUMPTION
    or_black: float = 0.68                    # [S3]
    or_public: float = 0.65                   # [S3]
    or_non_english: float = 0.75              # ASSUMPTION
    median_active_days: float = 16.5          # tuned so observed median use is ~14 d [S2]
    weibull_shape: float = 1.6                # ASSUMPTION, gives IQR near [S2]
    hr_public_active: float = 1.35            # ASSUMPTION, faster disengagement
    hr_black_active: float = 1.25             # ASSUMPTION
    p_reading_per_active_day: float = 0.85    # ASSUMPTION
    # Latent engagement trait shared by reading frequency and persistence, so
    # patients who measure often early also tend to keep going. ASSUMPTION;
    # consistent with adherence literature but with no postpartum estimate.
    trait_on_frequency: float = 0.9           # log-odds per SD
    trait_on_persistence: float = 0.6         # log-hazard per SD
 
    # BP trajectory. Calibrated so ~80% have any reading >=140/90 and ~14%
    # any severe-range reading [S1]; peak timing from [S5].
    sbp_baseline: dict = field(default_factory=lambda: {
        "gestational_hypertension": 130.0,
        "preeclampsia": 134.0,
        "preeclampsia_severe": 154.0})
    sbp_patient_sd: float = 8.0
    sbp_peak_rise: float = 6.0
    peak_day: float = 5.0
    sbp_decline_per_day: float = 0.45
    sbp_noise_sd: float = 4.5
    dbp_slope: float = 0.6
    dbp_intercept: float = 6.0
    dbp_noise_sd: float = 4.5
 
 
def _logit(p):
    return np.log(p / (1 - p))
 
 
def _sigmoid(x):
    return 1 / (1 + np.exp(-x))
 
 
def _engagement_intercept(p: CohortParams, covariate_logodds: np.ndarray) -> float:
    """Solve for the intercept that hits the target overall ascertainment."""
    lo, hi = -10.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _sigmoid(mid + covariate_logodds).mean() < p.target_ascertainment_10d:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
 
 
def generate_patients(p: CohortParams | None = None) -> pd.DataFrame:
    p = p or CohortParams()
    rng = np.random.default_rng(p.seed)
    n = p.n_patients
 
    race = rng.choice(list(p.race_probs), size=n, p=list(p.race_probs.values()))
    public = rng.random(n) < p.p_public_insurance
    non_english = rng.random(n) < p.p_non_english
    subtype = rng.choice(list(p.subtype_probs), size=n,
                         p=list(p.subtype_probs.values()))
    age = np.clip(rng.normal(31, 5.5, n), 18, 46).round()
    start = pd.Timestamp(p.start_date)
    discharge = start + pd.to_timedelta(rng.integers(0, 30, n), unit="D")
 
    lo = (np.log(p.or_black) * (race == "Black")
          + np.log(p.or_public) * public
          + np.log(p.or_non_english) * non_english)
    b0 = _engagement_intercept(p, lo)
    p_engage = _sigmoid(b0 + lo)
    engaged = rng.random(n) < p_engage
 
    # Active monitoring duration (Weibull), scaled so the engaged median is ~14 d.
    trait = rng.normal(0, 1, n)
    hr = ((p.hr_public_active ** public) * (p.hr_black_active ** (race == "Black"))
          * np.exp(-p.trait_on_persistence * trait))
    k = p.weibull_shape
    scale = p.median_active_days / (np.log(2) ** (1 / k))
    u = rng.random(n)
    active_days = scale * (-np.log(u) / hr) ** (1 / k)
    active_days = np.where(engaged, np.clip(active_days, 1, FOLLOW_UP_DAYS), 0)
    first_day = np.where(engaged, rng.choice([1, 1, 1, 2, 2, 3, 4, 6], n), np.nan)
 
    return pd.DataFrame({
        "patient_id": [f"PP{i:04d}" for i in range(n)],
        "age": age.astype(int),
        "race_ethnicity": race,
        "insurance": np.where(public, "public", "private"),
        "language": np.where(non_english, "non-English", "English"),
        "hdp_subtype": subtype,
        "discharge_date": discharge,
        "p_engage_true": p_engage.round(3),
        "engaged_true": engaged,
        "first_reading_day_true": first_day,
        "active_days_true": active_days.round(1),
        "sbp_patient_level": rng.normal(0, p.sbp_patient_sd, n),
        "engagement_trait_true": trait.round(3),
    })
 
 
def generate_readings(patients: pd.DataFrame, p: CohortParams | None = None) -> pd.DataFrame:
    """Home BP readings, one row per reading, with columns matching
    jupyterhealth_client.list_observations_df for blood-pressure:4.0."""
    p = p or CohortParams()
    rng = np.random.default_rng(p.seed + 1)
    rows = []
    for pt in patients.itertuples():
        if not pt.engaged_true:
            continue
        base = p.sbp_baseline[pt.hdp_subtype] + pt.sbp_patient_level
        first, last = int(pt.first_reading_day_true), int(pt.first_reading_day_true + pt.active_days_true)
        p_day = _sigmoid(_logit(p.p_reading_per_active_day)
                         + p.trait_on_frequency * pt.engagement_trait_true)
        for day in range(first, min(last, FOLLOW_UP_DAYS) + 1):
            if rng.random() > p_day:
                continue
            # Rise to a peak near day 5 [S5], then gradual decline.
            trend = (p.sbp_peak_rise * np.exp(-0.5 * ((day - p.peak_day) / 2.0) ** 2)
                     - p.sbp_decline_per_day * max(day - p.peak_day, 0))
            sbp_mean = base + trend
            n_readings = 2 if sbp_mean >= 140 else 1          # [S6] protocol
            for r in range(n_readings):
                hour = 8 if r == 0 else 19
                ts = (pt.discharge_date + pd.Timedelta(days=day, hours=hour)
                      + pd.Timedelta(minutes=int(rng.integers(0, 60))))
                sbp = sbp_mean + rng.normal(0, p.sbp_noise_sd)
                dbp = p.dbp_intercept + p.dbp_slope * sbp + rng.normal(0, p.dbp_noise_sd)
                rows.append({
                    "patient_id": pt.patient_id,
                    "postpartum_day": day,
                    "effective_time_frame_date_time_local": ts,
                    "systolic_blood_pressure_value": round(sbp),
                    "systolic_blood_pressure_unit": "mmHg",
                    "diastolic_blood_pressure_value": round(dbp),
                    "diastolic_blood_pressure_unit": "mmHg",
                    "code": "omh:blood-pressure:4.0",
                    "modality": "sensed",
                })
    return pd.DataFrame(rows)
 
 
def to_omh_record(row) -> dict:
    """One reading as an OMH blood-pressure:4.0 data point (for CSV Upload)."""
    return {
        "header": {
            "uuid": str(uuid.uuid4()),
            "schema_id": {"namespace": "omh", "name": "blood-pressure", "version": "4.0"},
            "modality": "sensed",
            "acquisition_provenance": {"source_name": "edge-medicine-synthetic-postpartum"},
        },
        "body": {
            "systolic_blood_pressure": {"value": int(row.systolic_blood_pressure_value), "unit": "mmHg"},
            "diastolic_blood_pressure": {"value": int(row.diastolic_blood_pressure_value), "unit": "mmHg"},
            "effective_time_frame": {"date_time": row.effective_time_frame_date_time_local.isoformat() + "-08:00"},
        },
    }
 
 
# ACOG Practice Bulletin 222 / Committee Opinion 736 thresholds.
def classify_bp_acog(sbp, dbp) -> str:
    if sbp >= 160 or dbp >= 110:
        return "severe"
    if sbp >= 140 or dbp >= 90:
        return "hypertensive"
    return "controlled"
 
 
def engagement_summary(patients: pd.DataFrame, readings: pd.DataFrame) -> pd.DataFrame:
    """Per-patient engagement and clinical flags, computed only from what the
    platform observes (no *_true columns), as a deployed system would."""
    r = readings.copy()
    r["category"] = [classify_bp_acog(s, d) for s, d in
                     zip(r.systolic_blood_pressure_value, r.diastolic_blood_pressure_value)]
    g = r.groupby("patient_id")
    s = pd.DataFrame({
        "n_readings": g.size(),
        "days_with_reading": g.postpartum_day.nunique(),
        "first_day": g.postpartum_day.min(),
        "last_day": g.postpartum_day.max(),
        "any_hypertensive": g.category.agg(lambda c: (c != "controlled").any()),
        "any_severe": g.category.agg(lambda c: (c == "severe").any()),
        "max_sbp": g.systolic_blood_pressure_value.max(),
    })
    out = patients.set_index("patient_id").join(s)
    out["n_readings"] = out.n_readings.fillna(0).astype(int)
    out["days_with_reading"] = out.days_with_reading.fillna(0).astype(int)
    out["ascertained_10d"] = out.first_day.le(10).fillna(False)
    out["still_active_day14"] = out.last_day.ge(14).fillna(False)
    out["any_hypertensive"] = out.any_hypertensive.fillna(False).astype(bool)
    out["any_severe"] = out.any_severe.fillna(False).astype(bool)
    return out
 