# Project Brief

_Last updated: October 17, 2026_

## Context

The Center for Edge Medicine, a joint UCSF and UC Berkeley initiative built around the JupyterHealth platform, hosts an innovation challenge for data science and biology researchers who aim to translate research into ventures. Our team initially considered four domains for a continuous monitoring product: women's health, longevity, neurodegenerative disease, and bipolar disorder. In October 2026 the team converged on women's health.

## Goal

Build a JupyterHealth-based continuous monitoring platform for women's health, demonstrated through a narrowed MVP: remote monitoring of patients after a complicated pregnancy, with a structured handoff to primary care.

## Clinical rationale

Hypertensive disorders of pregnancy and gestational diabetes are the two most common complications that persist into the postpartum period. Professional guidance recommends blood pressure assessment within 72 hours of discharge and again at 7 to 10 days postpartum for patients with a hypertensive disorder of pregnancy, and randomized evidence shows that home-based, text-mediated blood pressure surveillance meets these windows far more reliably than office follow-up (Hirshberg et al., BMJ Quality and Safety, 2018). Both conditions also confer elevated lifetime cardiometabolic risk, which places primary care at the end of the pathway.

## Why JupyterHealth fits

The Exchange already recognizes five observation types: blood pressure, blood glucose, heart rate, sleep stage summary, and food entry. The two measurements at the center of postpartum follow-up, blood pressure and glucose, are therefore native to the platform. The demo deployment ships with synthetic blood pressure and continuous glucose monitor studies, and the platform supports SMART on FHIR launch from an EHR, which is the natural path for a primary care handoff.

## MVP scope

| Component | Description | Status |
| --- | --- | --- |
| Ingestion | Home BP cuff and CGM readings flow into a study on the Exchange under patient consent | Supported by platform |
| Risk logic | Flag readings at or above 140/90 and severe-range readings at or above 160/110; track coverage of the 72-hour and 7 to 10 day windows | Prototype in `notebooks/02` |
| Clinician view | Dashboard summarizing trajectory, flags, and window adherence | To build (Voila) |
| Primary care handoff | One-page summary pushed at the end of the postpartum window | To design |
| Model layer | Predictive component, for example early identification of persistent postpartum hypertension | Requires training data (see `02_data-inventory.md`) |

## Open decisions

1. Whether the pitch leads with hypertension alone or with hypertension and glucose together.
2. Which real-world cohort supports the model layer (All of Us, nuMoM2b, or a clinical partner).
3. Whether the repository remains private through the challenge.

## Principal risk

Pregnancy context does not live on the Exchange. Delivery date, diagnosis, gestational age, and medications sit in the EHR. The measurement layer is ready; the clinical context layer is the gap this team must close.
