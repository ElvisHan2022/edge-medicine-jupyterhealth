# Team Workflow

## Branching and review

1. `main` holds work the team has reviewed. Nobody pushes to `main` directly.
2. Each piece of work lives on a short-lived branch named `<initials>/<topic>`, for example `eh/inventory-run`.
3. Open a pull request when the branch is ready. One teammate reviews before merge.
4. Clear notebook outputs before committing unless the outputs are aggregate results on synthetic data. In JupyterLab: Edit, Clear Outputs of All Cells.

## Data handling rules

1. No patient-level data is committed, including synthetic demo records. The `data/` folder is ignored by git for this reason.
2. Only aggregate outputs (counts, summary tables, figures on synthetic data) go in `outputs/`.
3. Tokens and credentials live in `.env`, which is ignored by git. Never paste a token into a notebook cell.
4. Any real-world data source (All of Us, nuMoM2b, clinical partners) is analyzed only inside its approved environment, under its own data use terms. Results leave that environment only in the aggregated form its terms permit.

## Recording decisions

Material decisions go in `docs/00_project-brief.md` under "Open decisions," moved to a dated "Decisions" list once settled. Data findings go in `docs/02_data-inventory.md`.

## Requesting data

Open an issue with the "Data request" template for any new data element or source. The issue becomes the record of who is pursuing it and what was learned.
