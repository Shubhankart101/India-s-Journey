# Public JSON resources and Swagger UI

This is a static GitHub Pages project, not a backend service. The Swagger UI at [`api.html`](api.html) documents read-only `GET` access to the project's JSON files; it does not expose mutation endpoints or guarantee an API service-level objective.

## Interactive checks

1. Open the [API explorer](api.html).
2. Choose **Run all endpoint checks** to fetch every documented JSON file from the current deployment and validate its JSON response.
3. Expand an operation in Swagger UI and choose **Try it out** for an individual resource.

## Documented resources

| Resource | Contents |
| --- | --- |
| `/data/chart-latest.json` | Generated chart series and provenance |
| `/data/election-results.json` | Current ECI and U.S. election snapshots |
| `/data/historical-elections.json` | Candidate-level records parsed from available ECI workbooks; partial coverage |
| `/data/us-campaign-finance.json` | FEC candidate-finance aggregates for Presidential, Senate and House cycles |
| `/data/economic-survey-monthly.json` | Monthly indicators collated from Economic Survey tables |
| `/data/ncrb-and-analyses.json` | NCRB and public-safety data |
| `/data/pew-india-reports.json` | Public Pew India report catalog |
| `/data/pew-snapshots.json` | Dated survey snapshots |
| `/data/indian-matrix-latest.json` | Public Indian Matrix article feed |
| `/data/substack-latest.json` | Public Polity and Policy article feed |

The OpenAPI source is [`openapi.json`](openapi.json). Tests check that every specification path maps to a parseable source JSON file and that the deployment copy matches it. The automated daily endpoint workflow also exercises the deployed dashboard and live-source checks.

## Local preview

From the repository root, run `python -m http.server 8000 --directory docs`, then open `http://localhost:8000/api.html`. The Swagger specification's server URL points to the public GitHub Pages deployment; the on-page all-resource check uses the local `data/` directory when served locally.
