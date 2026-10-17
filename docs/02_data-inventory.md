# Data Inventory

_Status as of October 17, 2026. Update after each run of `notebooks/01_connect_and_inventory.ipynb`._

The inventory answers two questions: what data the team can work with today, and what data the MVP requires that we do not yet hold. Each row carries an owner and a status so the table doubles as a task list.

## Summary

The measurement layer of the MVP is native to JupyterHealth: blood pressure and blood glucose are recognized observation types, and the demo Exchange contains synthetic studies for both. The clinical context layer is absent from the Exchange: delivery date, pregnancy complication diagnoses, gestational age, and postpartum medications reside in the EHR. A credible model layer additionally requires a real-world cohort with both pregnancy outcomes and longitudinal measurements, for which All of Us and nuMoM2b are the leading candidates.

## A. Observed on the Exchange

_Populate from `outputs/inventory_snapshot.csv`._

| Study ID | Study name | Organization | Patients | Consented scopes | Observation counts by type | Date range |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

## B. Data the MVP requires

| # | Data element | MVP function | On JupyterHealth today? | Candidate source | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Home blood pressure, systolic and diastolic | Hypertension flags, severe-range alerts, ACOG window adherence | Yes (`omh:blood-pressure:4.0`); synthetic demo study | Demo Exchange; local Exchange with synthetic data | | Available |
| 2 | Continuous or fingerstick glucose | Postpartum glycemic follow-up after gestational diabetes | Yes (`omh:blood-glucose:4.0`); synthetic CGM demo | Demo Exchange | | Available |
| 3 | Resting heart rate, sleep | Recovery and wellbeing context; possible mood signal | Yes (`omh:heart-rate:2.0`, `ieee:sleep-stage-summary:1.0`) | Oura via Open Wearables integration | | Available, synthetic only |
| 4 | Delivery date | Anchors every postpartum day count | No | EHR via SMART on FHIR (Encounter, Procedure), either clinician launch or patient portal import; manual entry for prototype | | Gap |
| 5 | Complication diagnosis (gestational hypertension, preeclampsia, HELLP, gestational diabetes) | Defines the eligible cohort and thresholds | No | EHR (FHIR Condition), clinician launch or patient portal import | | Gap |
| 6 | Antihypertensive and glucose-lowering medications | Interpreting readings; titration context | No | EHR (FHIR MedicationRequest), clinician launch or patient portal import | | Gap |
| 7 | Postpartum outcomes (readmission, ED visit, persistent hypertension at 6 weeks) | Labels for any predictive model; evaluation metrics | No | Real-world cohort (see section C) | | Gap |
| 8 | Depression screening (EPDS or PHQ-9) | Optional extension toward postpartum mental health | No | Patient-reported questionnaire; FHIR QuestionnaireResponse | | Deferred |
| 9 | Primary care destination and handoff timing | Routing of the end-of-window summary | No | EHR or patient intake | | Gap |

## C. Candidate real-world cohorts for the model layer

| Source | What it offers | Access path | Fit | Next step |
| --- | --- | --- | --- | --- |
| All of Us Research Program | EHR with pregnancy and delivery phenotypes, Fitbit data, surveys; prior work has computationally phenotyped pregnancy periods and built Fitbit-based models of the postpartum period (Hurwitz et al., JMIR mHealth and uHealth, 2024) | Researcher Workbench registration; Elvis has existing access | High for wearable signals; home blood pressure is sparse | Scope a delivery cohort with HDP or GDM diagnoses and count Fitbit coverage |
| nuMoM2b | Large prospective cohort of nulliparous pregnancies with detailed outcomes and follow-up | NICHD data repository request (verify current terms) | High for outcome labels; limited continuous data | Confirm availability and application timeline |
| Clinical partner data | Real postpartum remote monitoring readings | Requires IRB and a data use agreement | Highest validity; slowest path | Raise with Center for Edge Medicine advisors |
| Synthetic generation | Unlimited, controllable cohorts for demo and testing | Local Exchange plus a simulation script | Demo only; no validity claims | Build in `notebooks/` once the schema is fixed |

## D. Open questions

1. Can the team create its own study on the Berkeley demo Exchange, or is a local Exchange required for custom synthetic data?
2. Which FHIR resource types does the demo Exchange expose beyond Observation? Run `client.list_fhir_resource_types()` and record the answer here.
3. Is the patient portal import path (SMART on FHIR, patient-initiated) live on the demo deployment, and which FHIR resources does it bring in? This is the most direct route to pregnancy context without a hospital data agreement.
4. Does the Center for Edge Medicine provide any partner datasets to challenge participants?
