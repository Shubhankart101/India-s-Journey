# Authentication: Google and Microsoft (Outlook) only

The web app has **no local usernames or passwords** for site users. People sign in with a Google account or a Microsoft account (Outlook.com, Hotmail, Live, Microsoft 365 work or school). Accounts are created automatically the first time someone signs in. The only password login is the Django admin at `/admin/`, and it is only for staff created with `createsuperuser`.

| Piece | Where |
| --- | --- |
| Provider config | `SOCIALACCOUNT_PROVIDERS` in [`webapp/journey/settings.py`](../webapp/journey/settings.py) |
| Provider allow-list and adapters | [`webapp/indicators/auth.py`](../webapp/indicators/auth.py) |
| Sign-in page | [`frontend/src/pages/AuthPage.jsx`](../frontend/src/pages/AuthPage.jsx) |
| Tests | [`webapp/indicators/tests/test_oauth.py`](../webapp/indicators/tests/test_oauth.py), [`frontend/e2e/auth.spec.js`](../frontend/e2e/auth.spec.js) |

## How sign-in works

1. `/login` calls `GET /api/auth/providers/`, which returns only the providers that have a client ID configured.
2. Each provider button is a **POST** form (CSRF-protected) to `/accounts/<provider>/login/`. A plain GET does not start a login (`SOCIALACCOUNT_LOGIN_ON_GET = False`), so other sites cannot trigger one.
3. django-allauth redirects to Google or Microsoft using the authorization-code flow with **PKCE**, `prompt=select_account` and minimal scopes:
   - Google: `openid profile email`;
   - Microsoft: `User.Read`.
4. The provider redirects back to `/accounts/<provider>/login/callback/`. allauth creates or updates the user, starts a Django session, and redirects to `next`. `next` must be a same-site path; anything else is ignored.
5. The React app reads `GET /api/auth/me/`. `POST /api/auth/logout/` ends the session.

Errors on the way back render a page with HTTP 401 and links to try again or to use the backup site. If a provider is not configured, its route redirects to `/login?error=unavailable` rather than returning a 500.

Visiting `/register`, `/accounts/login/` or `/accounts/signup/` redirects to `/login`. Local signup is closed in `AccountAdapter.is_open_for_signup`.

### Account linking

`SOCIALACCOUNT_EMAIL_AUTHENTICATION` links a new social login to an existing user with the same email **only if the provider reports that email as verified**. allauth treats Microsoft email addresses as unverified, so a Microsoft sign-in never takes over an account that was created through Google. This protects against nOAuth-style account takeover.

Provider access tokens are not stored (`SOCIALACCOUNT_STORE_TOKENS = False`).

## Configuring the providers

Each provider takes its credentials from environment variables. You can instead add a *Social application* in the Django admin, attached to the current Site. If a provider has no credentials, it is hidden from the sign-in page.

| Variable | Notes |
| --- | --- |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 web client |
| `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET` | Microsoft Entra ID app registration |
| `MICROSOFT_TENANT` | `common` (default: personal and work accounts), `consumers` (Outlook.com only), `organizations`, or a tenant ID |

### Google

Google OAuth clients cannot be created with Terraform, so set this one up by hand:

1. Open Google Cloud console, go to **APIs & Services**, then **OAuth consent screen**:
   - choose the *External* user type;
   - add the app name, support email and the `openid`, `email` and `profile` scopes;
   - publish the app.
2. Go to **Credentials**, then **Create credentials**, then **OAuth client ID**, and choose **Web application**.
3. Add an **Authorized redirect URI** for every host:
   - `https://indias-journey.onrender.com/accounts/google/login/callback/`
   - `https://<custom-domain>/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/` (local development only)

   `terraform output google_redirect_uris` prints the production list.
4. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in Render. With Terraform, use `TF_VAR_google_client_id` and `TF_VAR_google_client_secret`.

### Microsoft (Outlook)

**With Terraform (recommended):** [`infra/terraform/modules/azuread_oauth_app`](../infra/terraform/modules/azuread_oauth_app) does the whole setup:
- creates the app registration with `AzureADandPersonalMicrosoftAccount` sign-in, v2 tokens and the Microsoft Graph `User.Read` scope, with implicit grant disabled;
- adds callback URIs for every host;
- creates a client secret that rotates every 180 days;
- passes the credentials to Render.

**By hand:**
1. In the Entra admin center, go to **App registrations**, then **New registration**.
2. For *Supported account types*, choose **Accounts in any organizational directory and personal Microsoft accounts**.
3. Under *Redirect URI*, choose **Web** and enter `https://<host>/accounts/microsoft/login/callback/`.
4. Under **Certificates & secrets**, create a new client secret. Copy its **Value**, not its ID.
5. Under **API permissions**, keep only Microsoft Graph `User.Read` (delegated).
6. Set `MICROSOFT_CLIENT_ID` (the *Application (client) ID*), `MICROSOFT_CLIENT_SECRET` and `MICROSOFT_TENANT=common`.

## Local development

Without credentials, the sign-in page says that sign-in isn't configured yet. Everything else in the app still works. To test a real login locally:
1. Create development OAuth clients with `http://localhost:8000/...` callbacks. For Microsoft, set `allow_localhost_redirects = true` in Terraform.
2. Export the variables.
3. Use `npm run build` and the Django server on port 8000. The Vite dev server on 5173 also proxies `/accounts`.

## Admin

Run `python webapp/manage.py createsuperuser` and sign in at `/admin/`. Staff can view users and their linked social accounts, and can manage Social applications there.
