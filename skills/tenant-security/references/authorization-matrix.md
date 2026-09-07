# Authorization Matrix Guide

Building a Principal-Action-Resource (PAR) matrix is the foundational step for a tenant security audit. It defines what access is expected, serving as the blueprint for your probes.

## Enumerating Principals
Identify all distinct actors that will interact with the system.
- **Roles:** e.g., Tenant Administrator, Tenant Member, Read-Only User.
- **Service Accounts:** API keys or machine-to-machine tokens.
- **Unauthenticated Users:** Anonymous access or expired tokens.
- Ensure you have credentials for at least two distinct tenants (Tenant A and Tenant B) to test cross-tenant isolation.

## Enumerating Resources
Identify all entities that belong to a tenant and are accessible via the application.
- **API Endpoints:** `/api/v1/invoices`, `/api/v1/users/{id}`
- **Database Tables:** `invoices`, `users`, `settings`
- **File Storage:** S3 buckets or local directories separated by tenant ID.

## Mapping Actions
For each resource, determine the supported CRUD (Create, Read, Update, Delete) operations.
- Map specific HTTP methods (GET, POST, PUT, PATCH, DELETE) or GraphQL mutations/queries to these actions.

## Matrix Format
Construct a table detailing the expected outcome for each Principal-Action-Resource combination.

| Principal (Tenant A) | Resource (Tenant A) | Resource (Tenant B) | Action | Expected Outcome |
|----------------------|---------------------|---------------------|--------|------------------|
| Tenant A Admin       | `invoices/1`        | -                   | READ   | ALLOW            |
| Tenant A Admin       | -                   | `invoices/2`        | READ   | DENY             |
| Tenant A Member      | `settings`          | -                   | UPDATE | DENY (Role)      |
| Unauthenticated      | `invoices/1`        | -                   | READ   | DENY (Authn)     |

## Common Patterns & Edge Cases
- **Role Hierarchy:** Verify that lower-privileged roles cannot escalate privileges within their tenant.
- **Shared Resources:** Identify resources accessible by multiple tenants (e.g., global reference data) and verify they are read-only.
- **Batch Endpoints:** Endpoints like `/api/v1/invoices/export` must filter data by the requesting tenant.
- **GraphQL:** Ensure tenant filters are applied in resolvers, not just at the entry point.
- **Background Jobs:** Verify that asynchronous tasks respect tenant context.
