# OAuth & Admin Employee Authorization

QuerySafe supports OAuth sign-in (Google, GitHub) and an admin approval workflow so administrators can authorize employees and assign their roles.

## How it works

1. **Employee registers** (email/password or OAuth) → account status is `pending`.
2. **Admin** opens **Dashboard → Manage employees** (`/dashboard/admin`).
3. Admin **approves** the employee and selects a **role** (hr, finance, sales, support, viewer) and **department**.
4. Employee completes **2FA setup**, then signs in and uses features allowed for their assigned role.

Roles control which database tables the AI may query (RBAC). The role in the JWT is enforced on `/ai/*` endpoints — clients cannot override it.

## Environment variables

Add to `.env`:

```env
# OAuth redirect (backend public URL)
OAUTH_REDIRECT_BASE=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Google OAuth (https://console.cloud.google.com/)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# GitHub OAuth (https://github.com/settings/developers) — optional
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Dev-only in-memory admin (when Postgres is not used)
BOOTSTRAP_ADMIN_EMAIL=admin@querysafe.io
BOOTSTRAP_ADMIN_PASSWORD=QsBootstrap9!
```

### OAuth redirect URIs

Register these callback URLs with your provider:

- Google: `{OAUTH_REDIRECT_BASE}/auth/oauth/google/callback`
- GitHub: `{OAUTH_REDIRECT_BASE}/auth/oauth/github/callback`

Example for local dev: `http://localhost:8000/auth/oauth/google/callback`

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth/oauth/google/authorize` | Start Google OAuth |
| GET | `/auth/oauth/github/authorize` | Start GitHub OAuth |
| GET | `/auth/oauth/providers` | Which providers are configured |
| GET | `/auth/me` | Current user profile |
| GET | `/admin/users?status_filter=pending` | List employees (admin) |
| POST | `/admin/users/{id}/approve` | Approve + assign role |
| POST | `/admin/users/{id}/reject` | Reject request |
| PATCH | `/admin/users/{id}/role` | Change role for approved user |

## Default admin (Postgres seed)

Migration seeds `admin@querysafe.io` with password `AdminPass123!` (bcrypt; change in production). For in-memory dev, bootstrap uses `QsBootstrap9!` unless `BOOTSTRAP_ADMIN_PASSWORD` is set.

## Database migration

Run `migrations/002_oauth_and_approval.sql` on existing databases, or recreate Postgres volume so init scripts apply it.
