# JupyterHealth Primer: From a Blank Account to a Plotted Observation

This primer explains what JupyterHealth is, how its parts connect, and the exact sequence of steps that takes a new team member from no account to a working analysis. A visual version of this walkthrough accompanies the repository.

## 1. The system in one paragraph

JupyterHealth is an open-source platform that separates health data infrastructure into two services. The **JupyterHealth Exchange** is a Django application that stores patient-consented health data as FHIR R5 Observations and exposes it through REST, FHIR, and MCP APIs. The **JupyterHealth Hub** is a cloud-hosted JupyterLab environment, operated by the nonprofit 2i2c, that authenticates against the Exchange and lets researchers query that data from notebooks. Data enters the Exchange from personal devices and apps, typically through the CommonHealth Android app or the Open Wearables integration, and from electronic health records through SMART on FHIR. SMART on FHIR serves two roles: clinicians open dashboards from inside their EHR, with the medical record number used to match the patient in the Exchange, and patients import their own records from their hospital's patient portal. Consent is the gate between the two: no observation reaches a researcher unless the patient has consented to the specific measurement type for the specific study.

## 2. Architecture

```
  DATA SOURCES                 EXCHANGE (Django + Postgres)            HUB (2i2c JupyterLab)
  -------------                -----------------------------           ---------------------
  BP cuff (iHealth)  ─┐        Organization                            Notebook
  CGM                ─┤          └─ Study (FHIR Group)                   from jupyterhealth_client
  Oura via OW        ─┼──▶          ├─ Data Sources                       import JupyterHealthClient
  Phone app (Health  ─┤             ├─ Scope Requests (BP, glucose…)     client = JupyterHealthClient()
   Connect)          ─┘             └─ Patients ──consent──▶ Observations    │
                                                     (OMH JSON in            ▼
  EHR (SMART on FHIR) ───────────▶  FHIR R5 / REST / MCP API ◀──token── pandas DataFrame
                                                                          │
                                                                          ▼
                                                                  Voila dashboard / report
```

## 3. The data model

| Entity | What it is | Why it matters to us |
| --- | --- | --- |
| Organization | A group of practitioners, patients, and studies; may be hierarchical | Our team would sit under a UCSF or Berkeley organization |
| Study | A FHIR Group of patients, owned by one organization | Our postpartum cohort would be one study |
| Scope request | The measurement types a study asks for | We request blood pressure and blood glucose |
| Patient | Registered by a practitioner; must consent per scope | Consent is per study and per measurement type |
| Data source | Anything that produces observations (a device or app) | For example an iHealth cuff or a CGM |
| Observation | One measurement, stored as base64-encoded Open mHealth JSON | The unit we analyze |
| Client | An OAuth 2.0 application | Patient apps use invitation links; analysis clients use tokens |

Observation types recognized by the client library today:

| `Code` member | Schema |
| --- | --- |
| `BLOOD_PRESSURE` | `omh:blood-pressure:4.0` |
| `BLOOD_GLUCOSE` | `omh:blood-glucose:4.0` |
| `HEART_RATE` | `omh:heart-rate:2.0` |
| `SLEEP_STAGE_SUMMARY` | `ieee:sleep-stage-summary:1.0` |
| `FOOD_ENTRY` | `ieee:food-entry:0.1` |

## 4. Starting from a blank space

### Path A: the hosted demo Hub (recommended for analysis)

**Step 1. Request an invite code.** Post in the `#jupyterhealth` channel on the Jupyter Zulip and ask for an invite to the Berkeley demo Exchange.

**Step 2. Create an Exchange account.** Go to <https://berkeley-jhe-demo.jupyterhealth.org/>, choose Sign Up, and enter the invite code, an email address, and a password. A successful login shows the Exchange dashboard with Organizations, Patients, and Studies in the sidebar.

**Step 3. Launch a Hub session.** Go to <https://jupyter-health.2i2c.cloud/>. Because the Hub authenticates through the Exchange, the existing login carries over. Start a server, which opens JupyterLab.

**Step 4. Connect from a blank notebook.** The Hub injects two environment variables, `JHE_URL` and `JHE_TOKEN`, so the client needs no arguments.

```python
from jupyterhealth_client import JupyterHealthClient, Code

client = JupyterHealthClient()
client.get_user()
```

**Step 5. See what you can access.**

```python
for study in client.list_studies():
    print(study["id"], study["name"], study["organization"]["name"])
```

```python
study_id = 30001  # replace with an id printed above

for patient in client.list_patients(study_id=study_id):
    print(patient["id"], patient["nameGiven"], patient["nameFamily"])
```

**Step 6. Pull observations into a DataFrame.** At least one of `study_id` or `patient_id` is required; `code` is optional.

```python
bp = client.list_observations_df(study_id=study_id, code=Code.BLOOD_PRESSURE)

bp = bp[[
    "subject_reference",
    "effective_time_frame_date_time",
    "systolic_blood_pressure_value",
    "diastolic_blood_pressure_value",
]]
bp.head()
```

**Step 7. Plot.**

```python
bp.groupby("subject_reference").plot(
    x="effective_time_frame_date_time",
    y=["systolic_blood_pressure_value", "diastolic_blood_pressure_value"],
    style="o",
)
```

Tokens expire after one day. When requests begin to fail, log out, log back in, and restart the server.

### Path B: a local Exchange (recommended for building the product)

The Exchange can be run on a laptop with seeded example users, which lets the team create its own organization, a postpartum study, synthetic patients, and synthetic observations without waiting on the shared demo.

```bash
git clone https://github.com/jupyterhealth/jupyterhealth-exchange.git
cd jupyterhealth-exchange
uv sync
cp .env.example .env            # set the DB_* values for a local Postgres
python manage.py migrate
python manage.py seed           # example orgs, users, and the admin OAuth app
python manage.py runserver      # http://localhost:8000
```

The seed command documents example practitioner logins and a default sign-up invitation code in the Exchange README. Change those credentials before any non-local use. The README quick start then covers creating an organization and study, adding scopes and data sources, generating a patient invitation link, and uploading observations through the FHIR API.

## 5. JupyterHealth repositories worth knowing

| Repository | Role for our project |
| --- | --- |
| [`jupyterhealth-exchange`](https://github.com/jupyterhealth/jupyterhealth-exchange) | The data platform; source for Path B |
| [`jupyterhealth-client`](https://github.com/jupyterhealth/jupyterhealth-client) | Python client used in every notebook here |
| [`demos`](https://github.com/jupyterhealth/demos) | Blood pressure tutorial, CGM dashboard, researcher views; the template for our clinician dashboard |
| [`sof-cgm-demo`](https://github.com/jupyterhealth/sof-cgm-demo) and [`jhe-smart-demo`](https://github.com/jupyterhealth/jhe-smart-demo) | SMART on FHIR launch from an EHR; the reference for the primary care handoff |
| [`omh-shim`](https://github.com/jupyterhealth/omh-shim) | Converts vendor wearable payloads to Open mHealth; relevant if we add a device |
| [`software-documentation`](https://github.com/jupyterhealth/software-documentation) | Architecture, auth, access control, FHIR docs |
| [`team-compass`](https://github.com/jupyterhealth/team-compass) | Meeting notes and roadmap signals from the core team |

## 6. Vocabulary

See `docs/04_glossary.md` for the platform's terms and their relevance to our MVP.

## 7. Where to ask questions

The `#jupyterhealth` stream on the Jupyter Zulip is the primary channel. Issues on the relevant repository are appropriate for bugs or documentation gaps.
