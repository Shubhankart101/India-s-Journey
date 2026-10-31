# Terraform samples

These are sample modules that provision the India's Journey web app and its supporting services. They are a starting point to review and adapt; nothing here runs automatically.

```
infra/terraform/
├── modules/
│   ├── render_web_service/   Render Docker web service, env vars, disk, custom domains, maintenance → backup site
│   ├── azuread_oauth_app/    Microsoft Entra ID app registration for "Sign in with Microsoft (Outlook)"
│   └── github_repository/    Actions variables/secrets, the outage label, optional branch protection
└── environments/
    └── production/           Wires the three modules together
```

## Prerequisites

| Provider | Credentials |
| --- | --- |
| `render-oss/render` ~> 1.7 | `RENDER_API_KEY`, `RENDER_OWNER_ID` |
| `hashicorp/azuread` ~> 3.0 | `az login`, or `ARM_TENANT_ID` + `ARM_CLIENT_ID` + `ARM_CLIENT_SECRET` (needs `Application.ReadWrite.OwnedBy`) |
| `integrations/github` ~> 6.0 | `GITHUB_TOKEN` with repository admin |

Terraform 1.6 or later is required (1.7 or later for `mock_provider` in the tests).

## Usage

```bash
cd infra/terraform/environments/production
cp terraform.tfvars.example terraform.tfvars        # git-ignored
export TF_VAR_google_client_secret=...               # never commit secrets
terraform init
terraform plan
terraform apply
terraform output google_redirect_uris                # paste into the Google OAuth client
```

Enable a remote backend (the commented `azurerm` block in `main.tf`, or S3, GCS or Terraform Cloud) before applying. The Microsoft client secret is stored in state.

### Google OAuth

Google does not provide an API for creating OAuth clients for consumer sign-in. Create the client by hand in Google Cloud console ([steps](../../docs/AUTHENTICATION.md#google)) and pass `google_client_id` and `google_client_secret` in.

### Avoiding a dependency cycle

The Microsoft redirect URIs need the app's hostname, and the Render service needs the Microsoft credentials. The environment therefore builds the hostnames up front, as `"<service_name>.onrender.com"` plus `custom_domains`, instead of reading them from the Render resource.

## Module reference

### `render_web_service`

| Input | Default | Notes |
| --- | --- | --- |
| `name` | `indias-journey` | Also the `onrender.com` subdomain |
| `plan` / `region` | `starter` / `singapore` | `region` is validated |
| `repo_url`, `branch` | this repository, `main` | Auto-deploys on push |
| `disk_size_gb` | `1` | `0` means no disk (SQLite is ephemeral). Otherwise the disk mounts at `/var/data` and `DJANGO_SQLITE_PATH` is set |
| `custom_domains` | `[]` | Also sets `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` |
| `google_*`, `microsoft_*` | empty | Set only when non-empty |
| `backup_site_url` | GitHub Pages | Error-page links and the maintenance-mode redirect |
| `maintenance_mode` | `false` | `true` sends all visitors to the backup |
| `extra_env` | `{}` | Any additional variables |

Outputs: `id`, `url`, `hostname`.

### `azuread_oauth_app`

| Input | Default | Notes |
| --- | --- | --- |
| `hostnames` | (required) | Each one gets `https://<host>/accounts/microsoft/login/callback/` |
| `sign_in_audience` | `AzureADandPersonalMicrosoftAccount` | Allows Outlook.com/Hotmail and work accounts |
| `allow_localhost` | `false` | Adds `http://localhost:8000/...` |
| `secret_rotation_days` | `180` | Rotated with `time_rotating` |
| `owners` | the caller | |

Outputs: `client_id`, `client_secret` (sensitive), `tenant` (`common`, `consumers`, `organizations` or the tenant ID), `redirect_uris`.

### `github_repository`

Sets the Actions variables `APP_URL` and `BACKUP_SITE_URL` (read by `uptime-monitor.yml`), any `actions_secrets`, and the `outage` label. It can optionally protect the default branch so the Web app CI checks are required. Output: `pages_url`.

## Tests

Each module and the production environment have `terraform test` suites (`tests/*.tftest.hcl`). They use **mock providers**, so they need no cloud credentials:

```bash
for d in modules/* environments/*; do terraform -chdir=$d init -backend=false && terraform -chdir=$d test; done
```

They check:
- health-check wiring, generated secrets, disk handling, custom domains and maintenance mode;
- OAuth environment variables;
- Microsoft redirect URIs, sign-in audience, v2 tokens, disabled implicit grant, the least-privilege Graph scope and tenant selection;
- input validation;
- the composed outputs.

CI runs `fmt -check`, `validate` and `test` in the **terraform** job of [`webapp-ci.yml`](../../.github/workflows/webapp-ci.yml).
