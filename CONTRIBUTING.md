# Contributing

Thanks for helping improve India's Journey. Data accuracy comes first: every series must come from an official or clearly cited public source, and gaps are documented rather than filled in.

## Setup

```bash
git clone https://github.com/Shubhankart101/India-s-Journey && cd India-s-Journey
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r webapp/requirements.txt
python webapp/manage.py migrate && python webapp/manage.py import_catalog
cd frontend && npm ci && npx playwright install chromium
```

- Run the app: `python webapp/manage.py runserver`, and `npm run dev` in `frontend/`.
- Preview the static site: `python -m http.server 8000 --directory docs`.
- Sign-in needs OAuth credentials. See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md). Everything else works without them.

## Before opening a pull request

Run the suites your change touches. All of them run in CI.

```bash
cd webapp && python manage.py test indicators
cd webapp && python manage.py spectacular --validate --fail-on-warn --file openapi-schema.yml
cd frontend && npm test && npm run build && npm run test:e2e
terraform fmt -recursive infra/terraform     # if you touched infra/
python -m unittest discover -s tests          # if you touched collectors or docs/
```

See [docs/TESTING.md](docs/TESTING.md) for what each suite covers.

## Guidelines

- **New data series:** add the collector under `scripts/`, give the series a `meta` block (title, group, subgroup, unit, source), schedule it in a workflow that fits the source's release cadence, and document it in [docs/PIPELINES.md](docs/PIPELINES.md). Use Indian number formatting (lakh/crore), except for USD series, which use international formatting.
- **API changes:** annotate views with `@extend_schema` so that Swagger at `/api/docs/` stays accurate. `test_docs_and_errors.py` fails if the schema and the responses drift apart. Update [docs/API.md](docs/API.md).
- **Authentication:** do not add local password sign-in. Only Google and Microsoft are supported, by design.
- **Errors:** user-facing failures should offer the backup site (`BackupLinks` in React, `errors/error.html` in Django).
- **Mobile:** check every UI change at a 390 px width. The Playwright *mobile* project runs on a Pixel 7.
- **Commits:** keep them small and descriptive. Never commit secrets, `terraform.tfvars` or state files.
