# Glossary

Terms used across the JupyterHealth documentation, condensed from <https://docs.jupyterhealth.org/>, with a note on each term's relevance to our MVP.

| Term | Definition | Relevance to our MVP |
| --- | --- | --- |
| Platform | The set of JupyterHealth tools built to work together, principally the Exchange and the Hub | The full stack we build on |
| Deployment | A running service hosted with JupyterHealth tools; may include an Exchange, a Hub, or both. The Berkeley demo has both | We analyze on the Berkeley deployment and prototype on a local one |
| Distribution | A JupyterHub bundled with configuration, software, and services so it works as one product | The Hub is a distribution; its configuration is public and adaptable |
| Exchange (JHE) | Back-end service that stores patient-consented data and serves it through APIs, including FHIR | Holds our blood pressure and glucose readings |
| Hub | Opinionated JupyterHub distribution that logs in through the Exchange and ships with the client library | Where the team writes notebooks and dashboards |
| Client library | `jupyterhealth-client`, a Python package that returns observations as pandas DataFrames | Used in every notebook in this repository |
| Organization | Exchange group that manages access; researchers, clinicians, patients, and studies belong to one or more | Our team's access boundary |
| Study | A group of patients whose data an organization collects for one purpose; patients choose what to share with each study | The postpartum cohort |
| Patient-consented data | Data a patient has explicitly agreed to share with a specific study; the Exchange accepts only consented data types | Consent screens become part of the product flow |
| Patient-generated data | Data patients collect outside the clinic from wearables, sensors, apps, and surveys | Home blood pressure and CGM readings |
| Data product | A dashboard, app, or report built from health data for clinicians or patients, often in a notebook and shared through Voila or Jupyter Book | The clinician dashboard and the primary care handoff summary |
| FHIR | HL7 standard for exchanging clinical data over a web API; lets EHR data and wearable data be read the same way | Common format for readings and pregnancy context |
| SMART on FHIR | Standard that lets an outside app log in to an EHR or patient portal and read limited FHIR data. JupyterHealth uses it in two ways: clinicians open dashboards from their EHR, and patients bring in records from their hospital's patient portal | Clinician launch supports the handoff; patient portal import is a candidate route for delivery date, diagnoses, and medications |
| MRN | Medical record number; dashboards launched from an EHR use it to find the same patient in the Exchange | Links an EHR-launched dashboard to the right postpartum patient |
| Open mHealth | Open schema standard for mobile and wearable data | Storage format of observations |
| IEEE 1752 | IEEE mobile health data standard derived from Open mHealth | Used for sleep and food entry schemas |
| CommonHealth | Android app from The Commons Project that patients use to connect devices and send readings to the Exchange; a partner project | The patient-side ingestion app for the MVP |
| Open Wearables | Self-hosted platform that connects to vendors such as Oura; the Exchange can pull from it | Route for heart rate and sleep if we add a wearable |
| EHR | Electronic health record system, such as Epic or Cerner | Source of pregnancy context |
| CGM | Continuous glucose monitor, recording glucose every few minutes | Postpartum follow-up after gestational diabetes |
| MCP | Model Context Protocol; the Exchange has an optional, separately deployed MCP server so AI tools can query health data | Possible conversational layer for clinicians, with governance implications |
