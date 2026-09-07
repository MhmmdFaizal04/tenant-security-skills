<p align="center">
  <h1 align="center">Tenant Security Skills</h1>
  <p align="center">
    Prove tenant isolation through response content and database state, not just HTTP status codes.
  </p>
</p>

<p align="center">
  <a href="https://github.com/MhmmdFaizal04/tenant-security-skills/actions/workflows/ci.yml"><img src="https://github.com/MhmmdFaizal04/tenant-security-skills/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://github.com/MhmmdFaizal04/tenant-security-skills/releases/latest"><img src="https://img.shields.io/github/v/release/MhmmdFaizal04/tenant-security-skills?label=version&color=blue" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/MhmmdFaizal04/tenant-security-skills?color=green" alt="License"></a>
  <a href="https://github.com/MhmmdFaizal04/tenant-security-skills/stargazers"><img src="https://img.shields.io/github/stars/MhmmdFaizal04/tenant-security-skills?style=social" alt="Stars"></a>
  <a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/Agent%20Skills-v1.0-blueviolet" alt="Agent Skills"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/flask-3.1-000000?logo=flask&logoColor=white" alt="Flask"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> &middot;
  <a href="#the-problem">The Problem</a> &middot;
  <a href="#how-it-works">How It Works</a> &middot;
  <a href="#try-it-locally">Try It</a> &middot;
  <a href="#comparison">Comparison</a> &middot;
  <a href="docs/README.id.md">Bahasa Indonesia</a>
</p>

---

## The Problem

Most BOLA (Broken Object Level Authorization) and IDOR (Insecure Direct Object Reference) testing only checks HTTP status codes:

```
GET /api/projects/3  -->  403 Forbidden  -->  "Looks secure!"
```

**But a 403 does not prove safety.** The response body might still contain leaked data. A denied PUT might still modify the database. Real tenant security demands proof at the content and state level.

```
Traditional:   Status 403         -->  "Secure"
This skill:    Status 403         -->  Check response body for leaked data
               PUT returns 403    -->  Query DB to verify zero state change
```

## What This Skill Does

| Capability | Description |
|:-----------|:------------|
| Authorization Mapping | Build a Principal-Action-Resource (PAR) matrix for all tenant boundaries |
| Content-Level Probing | Inspect response bodies for cross-tenant data leaks, not just status codes |
| Database State Verification | Query database before and after denied mutations to prove zero state change |
| Regression Test Generation | Generate executable tests with content-based assertions |
| Evidence-Based Remediation | Fix vulnerabilities with before/after code and re-verification |
| Structured Reporting | Deliver findings with full evidence: request, response excerpt, DB state |

## Installation

```bash
npx skills add MhmmdFaizal04/tenant-security-skills
```

After installation, the skill activates automatically when you ask your agent to audit tenant boundaries, check for BOLA/IDOR, or review multi-tenant authorization.

## Example Prompts

Use these directly with your AI coding agent:

```
Audit the /api/projects endpoints for cross-tenant data leaks using tenant-security.
```

```
Check if PUT /api/users/{id} allows cross-tenant database mutations.
Build a regression test suite for all tenant authorization boundaries.
```

```
Review our SaaS API authorization. Map every endpoint into a principal-action-resource
matrix, probe cross-tenant access, verify database state after denied mutations,
and generate regression tests.
```

## How It Works

```
  1. MAP              2. BASELINE           3. PROBE
  Build PAR matrix    Verify legitimate     Test cross-tenant
  of all boundaries   access works first    boundaries
       |                    |                    |
       v                    v                    v
  4. EVIDENCE         5. REGRESS            6. REPORT
  Capture response    Generate tests        Deliver findings
  content + DB state  with content asserts  with full evidence
```

**Step 1 -- Map:** Enumerate all principals (roles), resources (endpoints), and actions (CRUD). Build a matrix of expected allow/deny outcomes.

**Step 2 -- Baseline:** Confirm each principal can access their own tenant's resources. This prevents false positives and establishes evidence baselines.

**Step 3 -- Probe:** For every deny cell in the matrix, make the actual request. Examine the response body for leaked data, not just the status code.

**Step 4 -- Evidence:** After every denied mutation (PUT/POST/DELETE), query the database to confirm zero state change. A 403 means nothing if the database was modified.

**Step 5 -- Regress:** Generate executable test cases that assert on response content and database state, not just HTTP status codes.

**Step 6 -- Report:** Deliver an evidence report with the PAR matrix, findings, evidence bundles, remediation applied, and re-verification results.

## Try It Locally

The repo includes runnable Flask fixtures with synthetic data -- no external services needed.

### Vulnerable API (4 intentional bugs)

```bash
cd fixtures/vulnerable-api
pip install -r requirements.txt
python app.py
# Running on http://localhost:5001
```

```bash
# Cross-tenant IDOR -- Acme admin reads Globex's project
curl -H "X-API-Key: acme-admin-key-001" http://localhost:5001/api/projects/3
# {"id":3, "tenant_id":2, "name":"Project Gamma", "budget":75000.0, ...}
#          ^^^^^^^^^^^^ This is Globex's data -- tenant boundary broken!
```

### Secure API (all bugs fixed)

```bash
cd fixtures/secure-api
python app.py
# Running on http://localhost:5002
```

```bash
# Same request, but tenant boundary is enforced
curl -H "X-API-Key: acme-admin-key-001" http://localhost:5002/api/projects/3
# {"error":"Not found"}   (404 -- no data leaked, no enumeration)
```

## Fixture Architecture

Two identical Flask APIs with SQLite in-memory databases. Same endpoints, same data, different authorization logic.

### Test Tenants

| Tenant | Users | API Keys | Projects |
|:-------|:------|:---------|:---------|
| Acme Corp (id=1) | Alice (admin), Bob (member) | `acme-admin-key-001`, `acme-member-key-001` | Project Alpha (id=1), Project Beta (id=2) |
| Globex Inc (id=2) | Charlie (admin), Diana (member) | `globex-admin-key-001`, `globex-member-key-001` | Project Gamma (id=3), Project Delta (id=4) |

### Vulnerabilities Demonstrated

| ID | Type | Endpoint | Severity | What Happens |
|:---|:-----|:---------|:---------|:-------------|
| VULN-001 | IDOR | `GET /api/projects/:id` | Critical | Returns any project regardless of tenant |
| VULN-002 | State Mutation | `PUT /api/projects/:id` | Critical | Modifies any project AND database state changes |
| VULN-003 | Enumeration | `GET /api/users` | High | Returns all users from all tenants |
| VULN-004 | IDOR | `GET /api/users/:id` | High | Returns any user profile regardless of tenant |

### Test Suite (15 tests, all passing)

```
tests/test_fixtures.py::test_health                              PASSED
tests/test_fixtures.py::test_missing_api_key                     PASSED
tests/test_fixtures.py::test_invalid_api_key                     PASSED
tests/test_fixtures.py::test_legitimate_project_list             PASSED
tests/test_fixtures.py::test_legitimate_project_read             PASSED
tests/test_fixtures.py::test_legitimate_user_list_secure         PASSED
tests/test_fixtures.py::test_vuln_idor_project_read              PASSED
tests/test_fixtures.py::test_vuln_cross_tenant_mutation          PASSED
tests/test_fixtures.py::test_vuln_user_enumeration               PASSED
tests/test_fixtures.py::test_vuln_idor_user_read                 PASSED
tests/test_fixtures.py::test_secure_idor_project_blocked         PASSED
tests/test_fixtures.py::test_secure_cross_tenant_mutation_blocked PASSED
tests/test_fixtures.py::test_secure_user_enumeration_fixed       PASSED
tests/test_fixtures.py::test_secure_idor_user_blocked            PASSED
tests/test_fixtures.py::test_expected_findings_structure         PASSED
```

## Evidence Levels

| Level | Evidence | What It Proves |
|:------|:---------|:---------------|
| 1 | HTTP status code only | Request was denied (but data may have leaked) |
| 2 | Response content analysis | Response body contains no cross-tenant data |
| 3 | Database state verification | Denied mutation caused zero state change |
| 4 | Regression test suite | Boundaries hold across code changes |

This skill operates at **levels 2-4**. Most traditional BOLA testing stops at level 1.

## Comparison

| Feature | Traditional BOLA Testing | Tenant Security Skills |
|:--------|:------------------------|:----------------------|
| Status code check | Yes | Yes |
| Response body analysis | Rarely | Always |
| Database state verification | No | Yes |
| Automated regression tests | Manual | Generated |
| Evidence-based report | Checklist | Full evidence bundle |
| Synthetic fixtures included | No | Yes (vulnerable + secure) |
| Works with AI coding agents | No | Yes (Agent Skills spec) |

## Compatibility

| Agent / Tool | Status |
|:-------------|:-------|
| Claude Code | Compatible |
| Antigravity | Compatible |
| Any Agent Skills CLI (`npx skills`) | Compatible |
| Python | 3.11+ required for fixtures |
| Flask | 3.1+ for fixtures |

## Project Structure

```
tenant-security-skills/
  skills/tenant-security/
    SKILL.md                          # Agent Skill entry point
    references/
      authorization-matrix.md         # PAR matrix guide
      evidence-collection.md          # Response + DB evidence guide
      regression-testing.md           # Test generation guide
      remediation-patterns.md         # Fix patterns (middleware, RLS, ORM)
    assets/
      audit-brief.md                  # Audit brief template
      audit-report.md                 # Evidence report template
  fixtures/
    vulnerable-api/app.py             # Flask API with 4 intentional bugs
    secure-api/app.py                 # Same API, all bugs fixed
    expected/                         # Expected findings for validation
  tests/
    test_fixtures.py                  # 15 pytest tests
    validate_repo.py                  # Structure validation
  evals/
    cases.json                        # 8 evaluation case definitions
  docs/
    README.id.md                      # Indonesian documentation
```

## Security

This skill tests authorization on **user-authorized targets only**. Fixtures use synthetic data in SQLite in-memory databases. Do not use this skill against systems without explicit written permission. See [SECURITY.md](SECURITY.md) for the full security policy.

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good first issues:**
- Add a fixture for GraphQL tenant isolation
- Add a fixture for JWT-based tenant authentication
- Add evaluation case for batch endpoint testing
- Add PostgreSQL RLS remediation example
- Translate documentation to another language

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built by <a href="https://github.com/MhmmdFaizal04">MhmmdFaizal04</a>. Not affiliated with OWASP, Anthropic, or any security certification body.</sub>
</p>
