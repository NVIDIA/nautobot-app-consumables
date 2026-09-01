# Security Policy: Consumables Tracking for Nautobot

## Reporting a Vulnerability

If you discover a potential security vulnerability in Consumables Tracking for Nautobot, please **do not open a public issue, pull request, or discussion**.

Use one of the following private reporting channels:

- **NVIDIA Vulnerability Disclosure Program** (preferred): https://www.nvidia.com/en-us/security/
- **Email**: [psirt@nvidia.com](mailto:psirt@nvidia.com)
  - NVIDIA encourages use of the public PGP key for sensitive reports: https://www.nvidia.com/en-us/security/pgp-key
- **GitHub Private Vulnerability Reporting**: Use this repository's **Security** tab and select **Report a vulnerability**

Please include the following information in your report:

- Product/project name and affected version, branch, or commit
- Vulnerability type, affected component, and affected interface
- Step-by-step reproduction instructions
- Proof-of-concept code or request samples, if available
- Expected and actual behavior
- Impact assessment, including any confidentiality, integrity, or availability impact
- Relevant configuration details, deployment mode, logs, or screenshots

Detailed reports help NVIDIA evaluate and address issues faster. NVIDIA's Product Security Incident Response Team (PSIRT) will acknowledge receipt, validate severity, coordinate fixes, and publish security bulletins or other advisories as appropriate.

## Security Architecture & Context

Consumables Tracking for Nautobot is a Python Django/Nautobot application packaged as `nautobot-consumables`. It extends Nautobot with data models, UI views, REST API view sets, template extensions, and development tooling for tracking consumable asset types, consumable products, location-based pools, and checked-out consumables assigned to Nautobot devices.

This software operates at the **Application / Nautobot App** level. Its primary security responsibility is to preserve the integrity and authorized visibility of consumable inventory metadata inside a Nautobot deployment. This includes user-defined consumable type schemas, consumable product records, pool quantities and locations, and checked-out consumable assignments to devices.

**Repository Exposure Classification:** Not determined.
Basis: origin remote is hosted on github.com, but repository visibility was not confirmed; this document is written to public-safe detail.

**Service Exposure Classification:** External / Regulated (high confidence).
Basis: confirmed by the requesting user; repository evidence shows an externally distributed Nautobot app with REST API/UI surfaces, packaged release metadata, and inventory data handling.

Key security boundaries and interfaces include:

- **Nautobot host boundary:** The app depends on Nautobot and Django for authentication, session handling, CSRF protection, object permissions, REST framework behavior, database access, and deployment security controls.
- **UI and API boundary:** `nautobot_consumables/urls.py` registers UI view sets and object tabs for consumables, consumable pools, consumable types, and checked-out consumables. `nautobot_consumables/api/urls.py` registers REST API endpoints for the same models.
- **Authorization boundary:** `nautobot_consumables/views.py` checks specific Nautobot permissions before showing primary key bulk-action columns in related-object tables. Core create, update, delete, list, and API operations are delegated to Nautobot view set permission behavior.
- **Data modeling boundary:** `nautobot_consumables/models.py` stores user-managed `schema` and `data` values in JSON fields and validates them with `jsonschema.Draft4Validator`.
- **Client-side schema editing boundary:** `nautobot_consumables/static/nautobot_consumables/js/nautobot-jsoneditor.js` renders and updates JSON schema/data forms in the browser, including loading schema content from app API URLs.
- **Development and test boundary:** `development/nautobot_config.py`, development Docker Compose files, and management commands provide local development services, default credentials, fixture generation, and database operations. These are intended for development/test use and are not production hardening guidance.

The app does not implement its own cryptography, identity provider integration, TLS listener, rate limiting, or standalone network service. Those responsibilities are expected to be provided by Nautobot, Django, the deployment environment, and upstream infrastructure.

## Threat Model

The following scenarios represent the primary security concerns for this project, based on the repository's application code and support tooling:

1. **Unauthorized Consumables Modification Through UI or API Routes:** The app exposes CRUD-style UI view sets in `nautobot_consumables/urls.py` and REST API view sets in `nautobot_consumables/api/urls.py` and `nautobot_consumables/api/views.py`. If Nautobot permissions are misconfigured, bypassed, or not consistently enforced by the inherited view set behavior, a user could create, modify, or delete consumable types, pools, quantities, or checked-out assignments that affect inventory integrity.

2. **JSON Schema or Data Abuse in Consumable Type Forms:** `nautobot_consumables/models.py` stores user-defined JSON schemas and data in `JSONField` columns and validates them with `jsonschema.Draft4Validator`. `nautobot_consumables/forms.py`, `nautobot_consumables/fields.py`, and `nautobot_consumables/static/nautobot_consumables/js/nautobot-jsoneditor.js` expose schema and data editing in forms. Maliciously large or complex schemas, unexpected schema features, or malformed data could cause excessive validation cost, confusing form behavior, or integrity issues if accepted from users with insufficiently constrained permissions.

3. **Client-Side Schema Loading and JSON Editor Behavior:** `nautobot_consumables/static/nautobot_consumables/js/nautobot-jsoneditor.js` builds a schema URL from form state and performs a synchronous AJAX request for schema content. If an attacker can influence the relevant form values, API URL field, or returned schema content through authorized-but-untrusted data, the browser-side editor may render unexpected schema-controlled UI and submit generated JSON back to the server.

4. **Inventory Relationship Integrity Failure During Bulk Pool Updates:** `nautobot_consumables/views.py` implements custom bulk update behavior for consumable pools. When a pool's location changes, checked-out consumables from that pool are deleted inside a transaction. Incorrect authorization, unexpected form input, or operator error on this path could cause unintended check-in of consumables or loss of assignment records.

5. **Sensitive Development Credential Reuse:** `development/nautobot_config.py`, `development/creds.example.env`, and `nautobot_consumables/management/commands/create_consumables_env.py` define development defaults and environment-variable names for secrets, database passwords, superuser credentials, and API tokens. If copied into a non-development deployment without replacement, these defaults could enable unauthorized administrative access or service compromise.

6. **Database Utility Command Misuse:** `tasks/control.py` includes development helper tasks for database shell access, import, and backup that compose database client commands from environment variables and file arguments. If these tasks are used with untrusted input or in an environment with broader privileges than intended, they could expose database contents, overwrite data, or execute unintended database operations.

7. **Sensitive Data Exposure Through Related Object Tables and Template Extensions:** `nautobot_consumables/views.py`, `nautobot_consumables/tables.py`, and `nautobot_consumables/template_content.py` add related consumable pool and checked-out consumable information to Device and Location pages. If object permissions or table column visibility are not aligned with the deployment's access model, users may see inventory relationships, device associations, locations, or internal identifiers beyond their intended scope.

## Critical Security Assumptions

- **Nautobot enforces authentication and object permissions:** The app assumes Nautobot's authentication, session management, API authentication, and permission framework are correctly configured and consistently applied to inherited UI and API view set operations.

- **Only trusted administrators can define consumable type schemas:** The app assumes users allowed to create or edit `ConsumableType` records and their JSON schemas are trusted to affect how consumable data-entry forms are rendered and validated.

- **Deployment TLS and transport security are handled outside this app:** The repository does not define production TLS, certificate, HSTS, proxy, or network listener hardening. It assumes production deployments provide HTTPS and secure service-to-service communication through Nautobot deployment infrastructure.

- **Development defaults are not used in production:** The development configuration, example credentials, Docker Compose files, and fixture-generation management command assume local or test use only. Production deployments must provide unique secrets, strong database credentials, and appropriate Nautobot settings.

- **Nautobot and Django provide input sanitization and template safety:** The app relies on Django templates, Nautobot form widgets, REST framework serializers, and `jsonschema` validation to safely handle user-supplied form data, API payloads, and JSON values.

- **Database integrity constraints remain enforced:** The app depends on Django model validation, database uniqueness constraints, and transactions to preserve relationships among consumables, pools, locations, and devices.

- **Operators restrict access to database maintenance tasks:** Invoke tasks and management commands that flush, import, back up, or seed databases are assumed to run only in controlled development or administrative environments.

## Dependency Security

Security-relevant dependencies and platforms include:

- **Nautobot**: Primary application framework, authentication and authorization provider, UI/API framework, model base classes, and plugin host.
- **Django and Django REST Framework via Nautobot**: Web framework, forms, sessions, CSRF handling, ORM, serializers, and request processing.
- **jsonschema**: Validation of user-managed consumable schemas and data.
- **django-tables2 and Nautobot UI helpers**: Rendering of object tables, bulk-selection controls, and related-object UI.
- **JSON editor static assets**: Browser-side rendering and manipulation of JSON schema/data forms.
- **Development services**: PostgreSQL or MySQL and Redis are used in development Compose configurations.

Maintain dependency updates through the normal Nautobot app release process, monitor upstream Nautobot and Django security advisories, and validate that supported Nautobot versions remain compatible with security fixes.

## Deployment Assumptions

- Deploy this app only inside a supported Nautobot deployment.
- Use production-grade Nautobot settings for `SECRET_KEY`, `ALLOWED_HOSTS`, database credentials, session/cookie security, CSRF settings, and debug behavior.
- Do not expose development database, Redis, documentation, or debug services beyond the intended local development boundary.
- Restrict schema-editing permissions to users who are trusted to define consumable metadata structures.
- Review Nautobot object permissions for Device, Location, Manufacturer, Consumable Type, Consumable, Consumable Pool, and Checked Out Consumable models together, because the app displays cross-model relationships.
