# Tenant Security Audit Brief

## Target Application
- **Name:**
- **Type:** [SaaS API / Web Application / Internal Service]
- **Base URL:**
- **Authorization:** [API Key / JWT / Session / OAuth]

## Tenant Model
- **Isolation level:** [Database per tenant / Schema per tenant / Row-level / Shared tables]
- **Tenant identifier:** [Header / Subdomain / Path / Token claim]
- **Number of test tenants:** (minimum 2)

## Principals
| Principal | Tenant | Role | Auth Credential |
|-----------|--------|------|------------------|
| | | | |

## Resources in Scope
| Resource | Endpoint Pattern | Actions | Tenant-scoped |
|----------|-----------------|---------|---------------|
| | | | |

## Constraints
- **Database access:** [Direct / ORM / Read-only / None]
- **Environment:** [Local / Staging / Production (read-only)]
- **Budget:** [Number of probe rounds]
