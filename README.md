# Tenant Security Skills

> Prove tenant isolation through response content and database state, not just HTTP status codes.

Tenant Security Skills is an Agent Skill that audits multi-tenant SaaS applications for authorization isolation bugs. It provides a robust testing framework that proves isolation by analyzing response content and database state, ensuring no data leaks occur even when access is purportedly denied.

## The Problem

Most BOLA (Broken Object Level Authorization) and IDOR (Insecure Direct Object Reference) testing only checks HTTP status codes like 403 Forbidden or 404 Not Found. However, a 403 response does not guarantee that sensitive data wasn't leaked in the response body. Similarly, a denied PUT request doesn't prove the database wasn't actually modified before the error was returned. Real tenant security requires content-level and state-level verification to ensure complete isolation.

## What This Skill Does

- Maps authorization boundaries with a Principal-Action-Resource matrix.
- Tests cross-tenant access by inspecting response content, not just status codes.
- Verifies database state integrity after denied mutation attempts.
- Generates regression tests that assert on response content.
- Provides evidence-based remediation with before/after verification.

## Quick Start

### Installation

```bash
npx skills add MhmmdFaizal04/tenant-security-skills
```

### Example Prompt

```text
Use tenant-security-skills to audit the /api/projects endpoints for cross-tenant data leaks.
```

```text
Verify if the PUT /api/users/{id} endpoint allows cross-tenant database mutations.
```

```text
Generate a regression test suite for the tenant authorization boundaries on the /api/reports endpoints.
```

## How It Works

1. **Map** -> Build authorization matrix
2. **Baseline** -> Verify legitimate access works
3. **Probe** -> Test cross-tenant boundaries
4. **Evidence** -> Capture response content + database state
5. **Regress** -> Generate test suite
6. **Fix** -> Apply and verify remediation

## Try It Locally

```bash
# Start the vulnerable test API
cd fixtures/vulnerable-api
pip install -r requirements.txt
python app.py  # Runs on port 5001

# In another terminal, try a cross-tenant request:
curl -H "X-API-Key: acme-admin-key-001" http://localhost:5001/api/projects/3
# Returns Globex's project data - this is the vulnerability!

# Now try the secure version:
cd fixtures/secure-api
python app.py  # Runs on port 5002
curl -H "X-API-Key: acme-admin-key-001" http://localhost:5002/api/projects/3
# Returns 404 - tenant boundary enforced
```

## Fixture Details

| Tenant | User | Project ID | App Version | Status |
|---|---|---|---|---|
| Acme | Alice (Admin) | 1, 2 | Vulnerable | Allows cross-tenant access |
| Acme | Bob (User) | 1, 2 | Secure | Denies cross-tenant access |
| Globex | Charlie (Admin)| 3, 4 | Vulnerable | Allows cross-tenant access |
| Globex | Dave (User) | 3, 4 | Secure | Denies cross-tenant access |

## Compatibility

- Agent Skills CLI (`npx skills`)
- Claude Code / Antigravity / any Agent Skills-compatible coding agent
- Fixtures require Python 3.11+ and Flask

## Evidence Levels

| Evidence | What It Proves |
|----------|---------------|
| HTTP status code only | Request was denied (but data may have leaked) |
| Response content check | No tenant data in response body |
| Database state verification | Denied mutation did not alter state |
| Regression test suite | Boundaries hold across code changes |

## Comparison

| Feature | Traditional BOLA Testing | This Skill |
|---------|------------------------|------------|
| Status code check | Yes | Yes |
| Response content analysis | Rarely | Always |
| Database state verification | No | Yes |
| Automated regression tests | Manual | Generated |
| Evidence-based report | Checklist | Full evidence bundle |

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
