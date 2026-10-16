# Litestar Application Template

This repository is a Python 3.12+ starter application built with
[Litestar](https://litestar.dev/). It provides an application factory, an
environment-driven configuration layer, async SQLAlchemy persistence through
Advanced Alchemy, JWT-based account access, token/session management, Alembic
migrations, and a small sample CRUD domain.

The code is organized into **core infrastructure**, **database**, and
**domain** packages. Domain packages contain HTTP controllers, request and
response schemas, dependency providers, guards, and services. Shared framework
configuration and reusable helpers live under `app.core`.

## Project layout

```text
.
├── README.md
├── pyproject.toml
├── uv.lock
└── src/
    └── app/
        ├── __main__.py
        ├── __metadata__.py
        ├── cli/
        │   └── commands.py
        ├── core/
        │   ├── server/
        │   │   ├── asgi.py
        │   │   ├── core.py
        │   │   └── plugins.py
        │   ├── settings/
        │   │   ├── app.py
        │   │   ├── config.py
        │   │   ├── constants.py
        │   │   ├── db.py
        │   │   ├── log.py
        │   │   └── server.py
        │   └── utils/
        │       ├── crypt.py
        │       ├── deps.py
        │       ├── engine_factory.py
        │       ├── env.py
        │       ├── exceptions.py
        │       ├── log.py
        │       ├── oauth.py
        │       ├── schema.py
        │       ├── serialization.py
        │       ├── validation.py
        │       └── domain/
        │           ├── _config.py
        │           ├── _discovery.py
        │           ├── _plugin.py
        │           └── _state.py
        ├── db/
        │   ├── fixtures/
        │   ├── migrations/
        │   │   ├── env.py
        │   │   └── versions/
        │   └── models/
        └── domain/
            ├── accounts/
            │   ├── controller/
            │   ├── schemas/
            │   └── services/
            └── samples/
```

### Top-level package

- `app.__main__` is the installed `app` command's entry point. It sets
  Litestar-related environment defaults, configures logging, and invokes the
  Litestar CLI.
- `app.__metadata__` provides package/version metadata with a fallback when
  the expected installed distribution metadata is unavailable. It currently
  looks up the distribution name `litestar-init`, while `pyproject.toml`
  declares the project name as `app`; align these values if installed package
  metadata should provide the actual version.
- `app.py.typed` marks the package as typed for downstream type checkers.
- `app.cli.commands` is the place for application-specific CLI commands. The
  sample user-management command wiring in the application core is currently
  commented out.
- Package `__init__.py` files establish the package hierarchy and, where
  applicable, re-export the public model, schema, and service names.

## Application startup and request flow

1. `app.__main__.run_cli()` prepares environment defaults and starts the
   Litestar command-line group.
2. The CLI's configured application factory is
   `app.core.server.asgi:create_app`.
3. `create_app()` creates a Litestar instance with `ApplicationCore`.
4. `ApplicationCore.on_app_init()` configures debug mode, the application path,
   OpenAPI/Scalar documentation, CORS, JWT authentication, exception handlers,
   dependency providers, and active plugins.
5. The active domain plugin scans `app.domain` for controllers and other
   exported domain components. Discovered controllers are registered as route
   handlers.
6. A request is matched to a controller. Litestar provides declared
   dependencies, and domain services use Advanced Alchemy repositories over an
   async SQLAlchemy session to perform persistence work.

`ApplicationCore` configures `app_config.path` as `/api/v1/`. The controller
decorators below declare their own paths (for example `/api/access/login` and
`/samples/`). Check the generated OpenAPI document or the running application
when confirming final externally visible URLs, especially if changing the
application path.

## Core modules

### Server and plugins

- `core/server/asgi.py` exposes the ASGI application factory.
- `core/server/core.py` owns application-level Litestar configuration and
  registers shared dependencies such as `current_user` and `settings`. It maps
  application and repository exceptions to HTTP responses.
- `core/server/plugins.py` constructs the Structlog, Advanced Alchemy,
  Granian, Problem Details, OAuth helper, and domain-discovery plugins.
- The plugins registered by `ApplicationCore` are **Advanced Alchemy**,
  **OAuth2 helper**, and **domain discovery**. Structlog, Granian, and Problem
  Details plugin objects are defined but commented out in that plugin list.
  Logging configuration is also initialized from the CLI entry point.

### Settings

- `core/settings/__init__.py` combines app, database, server, and logging
  settings into a cached `Settings` object. It loads `.env` from the current
  working directory when present; existing process environment variables take
  precedence.
- `core/settings/app.py` defines application identity, secret/JWT settings,
  CORS, cookies, OAuth credentials, and frontend/static URL values.
- `core/settings/db.py` defines database pool and Alembic settings and lazily
  creates the SQLAlchemy engine.
- `core/settings/server.py` defines host, port, reload, and keep-alive values.
- `core/settings/log.py` defines log levels, extracted request/response fields,
  and which cookie/header values should be obscured.
- `core/settings/constants.py` holds shared defaults such as pagination size
  and role names.
- `core/settings/config.py` creates shared compression, CORS, database,
  problem-details, and logging configuration objects.

### Shared utilities

- `utils/crypt.py` hashes and verifies passwords using Argon2, handles TOTP
  codes/provisioning QR codes, and verifies backup codes.
- `utils/deps.py` wraps Advanced Alchemy service providers and can manage
  multiple services that share a database session.
- `utils/engine_factory.py` configures async SQLAlchemy engines, connection
  pools, JSON serialization, and PostgreSQL JSON/JSONB codecs.
- `utils/env.py` contains environment-value parsing helpers used by settings.
- `utils/exceptions.py` defines application/client exception types and maps
  repository, integrity, authorization, and application errors to HTTP
  responses.
- `utils/log.py` contains Structlog processors and request/response logging
  support; `core/settings/log.py` supplies its configuration.
- `utils/oauth.py` provides OAuth callback/state helpers and registers OAuth
  types with Litestar's signature namespace. This helper does not by itself
  mean provider login routes are implemented.
- `utils/schema.py` supplies common Msgspec and Pydantic base schemas,
  including camel-case serialization.
- `utils/serialization.py` uses Msgspec for JSON and handles UUID, date,
  datetime, and Pydantic values.
- `utils/validation.py` contains reusable validation routines for account
  fields and password strength.
- `utils/domain/` implements configurable discovery of domain controllers,
  listeners, schemas, services, and repositories. Discovery uses exported
  names (`__all__`) for schema/service/repository/listener modules and caches
  controller results.

## Database layer

- `db/models/` contains SQLAlchemy models. The shared base comes from
  Advanced Alchemy and supplies UUIDv7 IDs and audit timestamps.
- `db/models/_user.py` defines `User`, including account status, profile
  fields, password hash, verification/reset state, encrypted TOTP secret,
  MFA state, and relationships to reset and refresh tokens.
- `db/models/_password_reset_token.py` and
  `db/models/_refresh_token.py` represent one-time password-reset credentials
  and rotating refresh-token sessions.
- `db/models/sample.py` is the sample CRUD model.
- `db/models/__init__.py` re-exports these models for convenient imports.
- `db/fixtures/` is the configured location for JSON fixtures; no fixture data
  is included in the current tree.
- `db/migrations/env.py` configures Alembic for online async and offline
  migration execution using Advanced Alchemy's metadata registry.
- `db/migrations/alembic.ini` sets the migration script location and naming
  template; `db/migrations/script.py.mako` is the revision-file template, and
  migration files are in `db/migrations/versions/`.

The checked-in migration history currently creates the user account table,
then the password-reset and refresh-token tables. Although the sample model
and sample routes exist, **there is no sample-table migration in the current
migration history**. Add and apply a migration before using sample endpoints
against a newly initialized database.

## Domain modules

### Accounts

`domain/accounts/` contains account-specific request handling and business
logic:

- `controller/_access.py` implements login/logout, refresh-token rotation,
  active-session listing and revocation, signup, and password-reset endpoints.
- `guards.py` configures JWT bearer authentication and user retrieval, and
  defines active/verified-user guards.
- `deps.py` builds request-scoped service providers for users, password-reset
  tokens, and refresh tokens.
- `schemas/` contains request and response structures for authentication,
  users, sessions, and password reset. Shared structures use camel-case field
  aliases.
- `services/_user.py` handles account persistence, password authentication,
  verification, and password changes.
- `services/_password_reset.py` hashes reset tokens, enforces their validity
  window, invalidates previous active tokens, and checks request rate limits.
- `services/_refresh_token.py` stores only SHA-256 token hashes, rotates
  refresh tokens, revokes token families, and lists/cleans up sessions.

Declared account route paths:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/access/login` | Authenticate with email/password and issue access and refresh credentials. |
| `POST` | `/api/access/logout` | Revoke the presented refresh-token family and clear auth cookies. |
| `POST` | `/api/access/refresh` | Rotate a refresh token and issue a new access token. |
| `GET` | `/api/access/sessions` | List active sessions for the authenticated user. |
| `DELETE` | `/api/access/sessions/{session_id}` | Revoke a session/token family belonging to the current user. |
| `DELETE` | `/api/access/sessions` | Revoke all other active sessions. |
| `POST` | `/api/access/signup` | Create an account. |
| `POST` | `/api/access/forgot-password` | Return a generic response for unknown/inactive users; an existing user's rate-limit branch returns a distinct response. |
| `GET` | `/api/access/reset-password?token=...` | Validate a password-reset token. |
| `POST` | `/api/access/reset-password` | Consume a valid reset token and update the password. |

Refresh tokens are returned in an HTTP-only cookie named `refresh_token` with
a seven-day max age and `/api/access` path. The `COOKIE_SECURE` setting controls
the `Secure` attribute. Login currently uses password authentication; the MFA
challenge flow is present only as commented code.

Password-reset delivery is not wired to an email service in the current
controller. The forgot-password handler performs account/rate-limit checks and
returns a generic response for unknown or inactive accounts, but token creation
and sending a reset link are not currently invoked there. The rate-limited
response is distinct, so that branch can reveal that the supplied address
belongs to an account.

### Samples

`domain/samples/` is an example domain:

- `controller.py` defines list, get-by-ID, create, update, and delete routes
  under the controller prefix `/samples`.
- `schemas.py` defines the sample response, create, and update payloads.
- `services.py` defines an Advanced Alchemy service/repository for `Sample`.
- `deps.py` exposes the sample service to Litestar dependency injection and
  prepares filter dependencies.
- `guards.py` requires an authenticated active user for sample routes.

Use this domain as the reference pattern when adding a new feature area.

## Configuration reference

All values are read from the process environment, with `.env` loading
supported by the settings module. Defaults listed here are development
defaults, not production recommendations.

| Variable | Purpose | Default / behavior |
| --- | --- | --- |
| `APP_URL` | Frontend/application base URL | `http://localhost:8000` |
| `LITESTAR_DEBUG` | Litestar debug mode | `true` |
| `SECRET_KEY` | Signing and encryption key | Randomly generated at process initialization if unset; configure a stable secret for deployments. |
| `ALLOWED_CORS_ORIGINS` | CORS origin list | `*`; accepts a comma-separated string or JSON list. Restrict this in production. |
| `COOKIE_SECURE` | Mark auth cookies Secure | `false`; enable behind HTTPS. |
| `STATIC_URL` | Static asset URL prefix | `/static/web/` |
| `VITE_DEV_MODE` | Frontend development-mode flag | `false` |
| `GOOGLE_OAUTH2_CLIENT_ID`, `GOOGLE_OAUTH2_CLIENT_SECRET` | Google OAuth credentials | Empty; OAuth is considered configured only when both are set. |
| `GITHUB_OAUTH2_CLIENT_ID`, `GITHUB_OAUTH2_CLIENT_SECRET` | GitHub OAuth credentials | Empty; OAuth is considered configured only when both are set. |
| `ENV_SECRETS` | Intended secret source/path setting | `runtime-secrets`; current settings code reads this value but does not load secrets from a secret manager. |
| `DATABASE_URL` | SQLAlchemy database connection URL | A placeholder default; set a real URL before startup. The engine explicitly supports async PostgreSQL URLs such as `postgresql+asyncpg://...` and async SQLite URLs such as `sqlite+aiosqlite://...`. |
| `DATABASE_ECHO`, `DATABASE_ECHO_POOL` | SQLAlchemy SQL/pool logging | `false` |
| `DATABASE_POOL_DISABLED` | Use `NullPool` instead of the configured pool | `false` |
| `DATABASE_POOL_SIZE` | Base connection pool size | `5` |
| `DATABASE_MAX_POOL_OVERFLOW` | Connections allowed beyond pool size | `10` |
| `DATABASE_POOL_TIMEOUT` | Pool acquisition timeout in seconds | `30` |
| `DATABASE_POOL_RECYCLE` | Connection recycle interval in seconds | `300` |
| `DATABASE_PRE_POOL_PING` | Ping before handing out a pooled connection | `false` |
| `DATABASE_MIGRATION_CONFIG` | Alembic INI path | `src/app/db/migrations/alembic.ini` |
| `DATABASE_MIGRATION_PATH` | Alembic script path | `src/app/db/migrations` |
| `DATABASE_MIGRATION_DDL_VERSION_TABLE` | Alembic version table name | `ddl_version` |
| `DATABASE_FIXTURE_PATH` | JSON fixture directory | `src/app/db/fixtures` |
| `LITESTAR_HOST`, `LITESTAR_PORT` | Server bind address | `0.0.0.0:8000` |
| `LITESTAR_KEEPALIVE` | Keep-alive seconds | `65` |
| `LITESTAR_RELOAD` | Enable reload | `false` |
| `LITESTAR_RELOAD_DIRS` | Paths watched for reload | Application package directory |
| `LOG_LEVEL` | Root logging threshold | `30` (`WARNING`) |
| `LOG_REQUEST_FIELDS`, `LOG_RESPONSE_FIELDS` | Fields extracted for request/response logs | Request path/method/query/path parameters and response status code |
| `SAQ_LOG_LEVEL`, `SQLALCHEMY_LOG_LEVEL` | SAQ and SQLAlchemy logger levels | `50` and `30` |
| `ASGI_ACCESS_LOG_LEVEL`, `ASGI_ERROR_LOG_LEVEL` | Server access/error logger levels | `30` |

Settings are cached for the process. Configure environment variables before
starting the application; changing them after settings have been loaded will
not refresh the cached settings object.

## Getting started

The project uses `uv` and declares Python `>=3.12`.

1. Install the project and locked dependencies:

   ```bash
   uv sync
   ```

2. Set at least `DATABASE_URL` and a stable `SECRET_KEY` in your environment or
   local `.env` file. Use a non-wildcard CORS allowlist and secure cookies when
   deploying behind HTTPS.

3. Inspect the available CLI commands:

   ```bash
   uv run app --help
   ```

4. Start the Litestar server using the `run` command exposed by the application
   CLI:

   ```bash
   uv run app run
   ```

5. Use the CLI help to find the installed Advanced Alchemy database commands,
   then apply the migrations before exercising routes that use the database.
   The migration history does not currently include the sample table.

The OpenAPI configuration uses Scalar as a rendering plugin. Consult the
generated schema from the running app for the exact documentation URL and
resolved route paths.

## Adding a domain

1. Create a package under `src/app/domain/<feature>/`.
2. Put route handlers in a module or package named `controller`, `controllers`,
   `route`, or `routes`. The discovery plugin scans these names and registers
   public `Controller` subclasses it finds.
3. Define request/response schemas under `schemas/` and export discovered
   types from that module's `__all__` where they need to be discovered into
   Litestar's signature namespace.
4. Define SQLAlchemy models in `db/models/` and re-export them from
   `db/models/__init__.py`.
5. Define a repository-backed service and a provider in the domain's `services/`
   and dependency module. Inject the provider into controllers rather than
   creating database sessions in route handlers.
6. Add and apply an Alembic migration for each schema change.
7. Add route guards where access must be restricted and tests for the behavior.

## Implementation notes

- The package/project metadata in `pyproject.toml` is currently a minimal
  template. Review the project name, description, author, and version before
  publishing.
- No `.env.example`, automated test suite, deployment manifest, or sample
  fixture data is included in the current repository tree.
- The app's compression and Problem Details configurations are constructed in
  settings, but their corresponding plugin/config is not currently attached in
  `ApplicationCore`.
- OAuth clients/callback helpers, MFA/TOTP helpers, event/listener discovery,
  and extensible service/repository discovery are framework support; they do
  not imply that full OAuth, MFA, email verification, or background-job
  workflows are currently exposed as routes.
- Keep production secrets out of source control. In particular, use an
  explicitly managed stable key: the generated development fallback is not
  suitable for deployments that need tokens or encrypted values to remain
  valid across restarts.