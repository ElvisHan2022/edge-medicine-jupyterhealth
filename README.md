# Edge Medicine: Postpartum Continuous Monitoring on JupyterHealth

Shared working repository for our Edge Medicine Innovation Challenge entry (Center for Edge Medicine, UCSF and UC Berkeley).

## Project goal

We are building a JupyterHealth-based continuous monitoring platform for women's health. The narrowed minimum viable product monitors patients after a complicated pregnancy and produces a structured handoff to primary care. The clinical anchor is the postpartum window, during which hypertensive disorders of pregnancy and gestational diabetes carry elevated short-term risk and long-term cardiometabolic consequences, and during which follow-up commonly lapses as care transfers from obstetrics to primary care.

The repository serves three functions:

1. A shared, reproducible environment for working against the JupyterHealth Exchange.
2. A living inventory of the data we can access today and the data the MVP requires.
3. A home for the prototype notebooks and dashboard that will support the pitch.

## Repository layout

| Path | Contents |
| --- | --- |
| `docs/00_project-brief.md` | Goal, MVP scope, open decisions |
| `docs/01_jupyterhealth-primer.md` | How JupyterHealth works, from a blank account to a plotted observation |
| `docs/02_data-inventory.md` | Data we have, data we need, and candidate sources for each gap |
| `docs/03_team-workflow.md` | Branching, review, and data-handling rules |
| `docs/04_glossary.md` | Platform vocabulary with relevance to our MVP |
| `notebooks/01_connect_and_inventory.ipynb` | Connects to the Exchange and enumerates every study, patient, consent scope, and observation type we can see |
| `notebooks/02_postpartum_bp_prototype.ipynb` | First prototype: postpartum blood pressure flags and an ACOG follow-up window check |
| `data/` | Local scratch space. Ignored by git. No patient-level data is ever committed. |
| `outputs/` | Aggregate outputs only (counts, figures on synthetic data) |

## Getting started

### 1. Get onto the JupyterHealth Hub

1. Request an Exchange invite code in the `#jupyterhealth` channel on the Jupyter Zulip: <https://jupyter.zulipchat.com/#narrow/channel/531270-jupyterhealth>
2. Sign up on the demo Exchange: <https://berkeley-jhe-demo.jupyterhealth.org/>
3. Log in to the Hub and start a server: <https://jupyter-health.2i2c.cloud/>

Full walkthrough: `docs/01_jupyterhealth-primer.md`.

### 2. Clone this repository inside the Hub

Open a terminal in JupyterLab (File, New, Terminal) and run:

```bash
git clone https://github.com/<OWNER>/edge-medicine-jupyterhealth.git
cd edge-medicine-jupyterhealth
pip install -r requirements.txt
```

Because the repository is private, git will ask for your GitHub username and a personal access token in place of a password. Create a fine-grained token scoped to this repository only (GitHub, Settings, Developer settings, Personal access tokens).

### 3. Run the inventory notebook

Open `notebooks/01_connect_and_inventory.ipynb` and run all cells. On the Hub, `JHE_URL` and `JHE_TOKEN` are already set, so no credentials are needed. The notebook writes an aggregate snapshot to `outputs/inventory_snapshot.csv`. Paste the summary into `docs/02_data-inventory.md` under "Observed on the Exchange."

### Working outside the Hub

Copy `.env.example` to `.env`, paste a personal Exchange token (see <https://docs.jupyterhealth.org/hub/get-a-token>), and load it before starting Jupyter. Tokens expire after one day.

## Team

| Member | Domain lead |
| --- | --- |
| Elvis Han | Longevity; repository maintainer |
| _(add name)_ | _(domain)_ |
| _(add name)_ | _(domain)_ |

Advising: Christine Wan (UCSF pharmacometrics).

## Key references

- JupyterHealth Hub guide: <https://docs.jupyterhealth.org/hub/>
- Client library: <https://jupyterhealth-client.readthedocs.io/>
- Exchange software docs: <https://docs.jupyterhealth.org/software-documentation/>
- Demo notebooks: <https://docs.jupyterhealth.org/demos/>
- 2i2c Hub user guide: <https://docs.2i2c.org/user/>
