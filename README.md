# Tether: Postpartum Cardiometabolic Monitoring on JupyterHealth

Shared working repository for Tether, our entry to the Edge Medicine Innovation Challenge (Center for Edge Medicine, UCSF and UC Berkeley).

## Project goal

Tether is a twelve-month monitoring platform and care protocol, built on JupyterHealth, for patients after gestational diabetes (GDM) or a hypertensive disorder of pregnancy (HDP). Both complications carry elevated short-term risk after delivery and lasting cardiometabolic consequences, and follow-up commonly lapses as care transfers from obstetrics to primary care. Tether extends monitoring from the point at which existing programs conclude through the full postpartum year, and ends with a structured handoff to primary care.

The platform has three components:

1. **Data layer.** Home blood pressure, glucose, wearable, and mental health screening data collected into the JupyterHealth Exchange under patient consent.
2. **Analytic layer.** Rule-based safety alerts and predictive engagement models, developed as auditable notebooks on JupyterHub.
3. **Care protocol.** The rules by which a partner health system's clinicians respond to alerts, escalate mental health concerns, and receive the twelve-month handoff.

Care proceeds in two phases. The safety phase (weeks 0 to 6) applies validated blood pressure threshold rules, and no model overrides them. The prevention phase (months 2 to 12) tracks each patient against her own baseline, prompts glucose screening after GDM, and schedules depression screening. The predictive core addresses the central risk: losing the patient from care altogether.

## Repository layout

| Path | Contents |
| --- | --- |
| `docs/00_project-brief.md` | Goal, MVP scope, open decisions |
| `docs/01_jupyterhealth-primer.md` | How JupyterHealth works, from a blank account to a plotted observation |
| `docs/02_data-inventory.md` | Data we have, data we need, and candidate sources for each gap |
| `docs/03_team-workflow.md` | Branching, review, and data-handling rules |
| `docs/04_glossary.md` | Platform vocabulary with relevance to Tether |
| `notebooks/01_connect_and_inventory.ipynb` | Connects to the Exchange and enumerates every study, patient, consent scope, and observation type visible to the account |
| `notebooks/02_postpartum_monitoring.ipynb` | Live Exchange wearable and glucose data alongside a simulated six-week postpartum blood pressure dashboard, with ACOG thresholds and a drafted primary care handoff card |
| `notebooks/03_dropout_model.ipynb` | Early-warning dropout model on the simulated cohort, evaluated for calibration and fairness across insurance, race, and language |
| `notebooks/04_synthetic_cohort.ipynb` | Generates the twelve-month Tether cohort and protocol timeline from `tether_cohort.py` |
| `notebooks/pp_synth.py` | Six-week postpartum blood pressure simulator used by notebooks 02 and 03 |
| `notebooks/tether_cohort.py` | Twelve-month cohort generator; every parameter is tagged as a published pilot value, a Tether target, or an assumption |
| `notebooks/archive/` | Superseded prototypes, kept for reference |
| `data/` | Local scratch space, ignored by git. No patient-level data is ever committed. |
| `outputs/` | Aggregate outputs only (counts, figures on synthetic data) |

## About the synthetic data

The Exchange contains no pregnancy records or postpartum blood pressure, so Tether's analytic layer is developed on simulated cohorts. Each generator states its parameters and their sources in the code. Any difference in engagement across insurance, language, or race exists because the configuration places it there; these cohorts demonstrate the pipeline and do not constitute evidence about real patients.

## Getting started

### 1. Get onto the JupyterHealth Hub

1. Obtain an Exchange invite code from the repository maintainer, or request one in the `#jupyterhealth` channel on the Jupyter Zulip: <https://jupyter.zulipchat.com/#narrow/channel/531270-jupyterhealth>
2. Sign up on the demo Exchange: <https://berkeley-jhe-demo.jupyterhealth.org/>
3. Log in to the Hub with the same credentials and start a server: <https://jupyter-health.2i2c.cloud/>

Full walkthrough: `docs/01_jupyterhealth-primer.md`.

### 2. Clone this repository inside the Hub

Open a terminal in JupyterLab (File, New, Terminal) and run:

```bash
cd ~
git clone https://github.com/ElvisHan2022/edge-medicine-jupyterhealth.git
cd edge-medicine-jupyterhealth
pip install -r requirements.txt
```

To push, git asks for your GitHub username and a personal access token in place of a password (nothing appears on screen as you paste it). Create a fine-grained token scoped to this repository with Contents set to Read and write (GitHub, Settings, Developer settings, Personal access tokens).

To receive teammates' changes, run `git pull` inside the repository before you start work.

### 3. Run the notebooks

Open each notebook in `notebooks/` in numerical order and select Run, Run All Cells. On the Hub, `JHE_URL` and `JHE_TOKEN` are already set, so no credentials are needed. Notebook 01 writes an aggregate snapshot to `outputs/inventory_snapshot.csv`; notebook 04 writes the synthetic cohort to `data/synthetic/`, which git ignores.

### Working outside the Hub

Copy `.env.example` to `.env`, paste a personal Exchange token (see <https://docs.jupyterhealth.org/hub/get-a-token>), and load it before starting Jupyter. Tokens expire after one day.

## Team

We are three students in UCSF's Master of Science in Health Data Science program, trained to build and test predictive models on clinical data, the core of Tether, and we pair that training with clinical research experience.

| Member | Focus on Tether |
| --- | --- |
| Elvis Han | JupyterHealth build, simulated patient cohort, engagement models; repository maintainer |
| Starlette Khim | Mental health screening, escalation design, and disengagement |
| Sachit Sinha | Translating biological and clinical questions into quantitative analysis and scientific insight |

**Starlette Khim** is a Clinical Research Coordinator in UCSF's Department of Psychiatry and Behavioral Sciences, where she manages the participant enrollment, data collection, and retention on which remote monitoring depends. She holds a B.A. in Psychology with a minor in Data Science from UC Berkeley, and her behavioral health background informs Tether's mental health screening, escalation design, and attention to disengagement.

**Sachit Sinha** brings research experience in bioinformatics and entomology from the University of Illinois Urbana-Champaign. His foundation in the biological sciences, combined with his training in data science, allows him to translate biological and clinical questions into quantitative analysis and to communicate computational findings as meaningful scientific insight.

**Elvis Han** holds a B.A. in Public Health Studies and Economics, with a minor in Applied Mathematics and Statistics, from Johns Hopkins University. He conducts research on consumer wearable and health record data in the All of Us Research Program, where his analysis of sleep changes after patients begin GLP-1 medications was accepted for oral presentation at the Western Medical Research Conference. He also builds machine learning tools that evaluate digital behavioral health programs in the TECH Lab at UCSF. He leads Tether's JupyterHealth build, the simulated patient cohort, and the engagement models.

We have already begun. We have obtained access to the JupyterHealth demo platform, built the simulated postpartum cohort on which our prototype runs, reviewed the published postpartum monitoring programs, and organized our work through a shared code repository and scheduled build sessions.

## Advisors

Two UCSF faculty members have agreed to advise our team.

| Advisor | Position | Advises on |
| --- | --- | --- |
| Karla Lindquist, PhD | Department of Obstetrics, Gynecology and Reproductive Sciences, UCSF | Modeling and validation design; clinician connections |
| Peter Washington, PhD | Assistant Professor, Division of Clinical Informatics and Digital Transformation, UCSF; Director, TECH Lab | Engagement models and their validation |

**Karla Lindquist, PhD**, a specialist in UCSF's Department of Obstetrics, Gynecology and Reproductive Sciences, brings data science expertise and published work on postpartum depression and anxiety. She has already reviewed this proposal and shaped its modeling and validation design, and she will connect us with clinicians in her department.

**Peter Washington, PhD**, Assistant Professor in UCSF's Division of Clinical Informatics and Digital Transformation, directs the TECH Lab, which develops machine learning methods for digital health and wearable data, and he will advise on the engagement models and their validation.

We will also recruit a perinatal mental health clinician to help design the escalation pathway. UCSF places us near the clinicians, patients, and health system data Tether requires, and our program allows us to continue building it beyond the challenge.

## Key references

- JupyterHealth Hub guide: <https://docs.jupyterhealth.org/hub/>
- Client library: <https://jupyterhealth-client.readthedocs.io/>
- Exchange software docs: <https://docs.jupyterhealth.org/software-documentation/>
- Demo notebooks: <https://docs.jupyterhealth.org/demos/>
- 2i2c Hub user guide: <https://docs.2i2c.org/user/>