# Authentication integration (temporarily disabled)

The React app currently exposes no account, sign-in or saved-chart UI. The Django authentication integration and session-backed API remain in place for a future release. The following notes describe that dormant integration for maintainers; the only active password login is the staff-only Django admin at `/admin/`.

| Piece | Where |
| --- | --- |
| Provider config | `SOCIALACCOUNT_PROVIDERS` in [`webapp/journey/settings.py`](../webapp/journey/settings.py) |
| Provider allow-list and adapters | [`webapp/indicators/auth.py`](../webapp/indicators/auth.py) |
| Sign-in UI | Removed from the React app; restore `frontend/src/auth.jsx`, `pages/AuthPage.jsx` and `pages/Saved.jsx` from git history when accounts return |
| Tests | [`webapp/indicators/tests/test_oauth.py`](../webapp/indicators/tests/test_oauth.py), [`frontend/e2e/auth.spec.js`](../frontend/e2e/auth.spec.js) |

## Sign-in flow when re-enabled

1. `/login` calls `GET /api/auth/providers/`, which returns only the providers that have a client ID configured.
2. Each provider button is a **POST** form (CSRF-protected) to `/accounts/<provider>/login/`. A plain GET does not start a login (`SOCIALACCOUNT_LOGIN_ON_GET = False`), so other sites cannot trigger one.
3. django-allauth redirects to Google or Microsoft using the authorization-code flow with **PKCE**, `prompt=select_account` and minimal scopes:
   - Google: `openid profile email`;
   - Microsoft: `User.Read`.
4. The provider redirects back to `/accounts/<provider>/login/callback/`. allauth creates or updates the user, starts a Django session, and redirects to `next`. `next` must be a same-site path; anything else is ignored.
5. The React app reads `GET /api/auth/me/`. `POST /api/auth/logout/` ends the session.

When the UI is re-enabled, errors on the way back render a page with HTTP 401 and links to try again or to use the backup site. If a provider is not configured, its route redirects to `/login?error=unavailable` rather than returning a 500.

The `/login`, `/register` and `/saved` React routes are not mounted while account UI is disabled. The legacy `/accounts/login/` and `/accounts/signup/` aliases redirect to the dashboard. Local signup remains closed in `AccountAdapter.is_open_for_signup`.

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

Set up the Google OAuth client in the Google Cloud console:

1. Open Google Cloud console, go to **APIs & Services**, then **OAuth consent screen**:
   - choose the *External* user type;
   - add the app name, support email and the `openid`, `email` and `profile` scopes;
   - publish the app.
2. Go to **Credentials**, then **Create credentials**, then **OAuth client ID**, and choose **Web application**.
3. Add an **Authorized redirect URI** for every host:
   - `https://<your-host>/accounts/google/login/callback/` (if you host the app)
   - `http://localhost:8000/accounts/google/login/callback/` (local development; see below)
4. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in your host's environment settings, or in `.env` for local development.

### Microsoft (Outlook)

1. In the Entra admin center, go to **App registrations**, then **New registration**.
2. For *Supported account types*, choose **Accounts in any organizational directory and personal Microsoft accounts**.
3. Under *Redirect URI*, choose **Web** and enter `https://<host>/accounts/microsoft/login/callback/`.
4. Under **Certificates & secrets**, create a new client secret. Copy its **Value**, not its ID.
5. Under **API permissions**, keep only Microsoft Graph `User.Read` (delegated).
6. Set `MICROSOFT_CLIENT_ID` (the *Application (client) ID*), `MICROSOFT_CLIENT_SECRET` and `MICROSOFT_TENANT=common`.

## Local development

To turn on real Google and Microsoft sign-in locally after restoring the UI routes:

1. Create the Google OAuth client and the Microsoft app registration as described above, with these redirect URIs (use the port you run Django on):
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/microsoft/login/callback/` (platform **Web**; Microsoft only accepts plain `http` for `localhost`)
2. Copy [`.env.example`](../.env.example) to `.env` in the repository root and fill in the client IDs and secrets. `.env` is gitignored and excluded from the Docker image. Django reads it on start (`load_env_file` in `settings.py`). Real environment variables take precedence, and `manage.py test` ignores the file. Set `DJANGO_ENV_FILE` to read a different file.
3. Restore the account routes, build the frontend (`cd frontend; npm run build`), start Django (`cd webapp; python manage.py runserver 8000`), and open **http://localhost:8000/login**. Use `localhost`, not `127.0.0.1`, so the callback matches the registered URI. The Vite dev server on 5173 also proxies `/accounts`.

Check what is configured with `curl http://localhost:8000/api/auth/providers/`. Each provider with credentials is listed.

## Admin

Run `python webapp/manage.py createsuperuser` and sign in at `/admin/`. Staff can view users and their linked social accounts, and can manage Social applications there.
