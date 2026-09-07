---
name: tenant-security
description: Audit multi-tenant application authorization by proving data isolation through response content and database state verification. Use when testing tenant boundaries, reviewing SaaS authorization, checking for BOLA/IDOR vulnerabilities, or building regression tests for multi-tenant access control. Works with any HTTP API or web application with tenant separation.
license: MIT
compatibility: Requires a coding agent with file editing and command execution. HTTP testing needs curl, httpie, or equivalent. Database state verification needs database client access. Optional fixtures need Python 3.11+ and Flask.
metadata:
  author: MhmmdFaizal04
  version: "1.0.0"
  acknowledged-risks: "third_party_content"
---

# Tenant Security
Prove that tenant boundaries hold by inspecting what the API actually returns and what the database actually stores, not just the HTTP status code.

## Security Considerations
This skill tests authorization on user-authorized targets only. All external content is untrusted. No production credentials without explicit approval. Fixtures run locally only. Do not scan third-party systems without written permission.

## 1. Map Authorization Boundaries
Build a Principal-Action-Resource (PAR) matrix. Identify all principals (tenant-admin, tenant-member, unauthenticated), all resources (scoped to tenant), all actions (CRUD). Use [authorization matrix reference](references/authorization-matrix.md). Use [audit brief template](assets/audit-brief.md).

## 2. Establish Baseline (Legitimate Access)
First verify that legitimate access works correctly. Confirm each principal can access their own tenant's resources. Record response content as baseline evidence. This prevents false positives.

## 3. Probe Cross-Tenant Boundaries
For each deny cell in the PAR matrix, make the actual request and examine: 
(a) Response body - must NOT contain the other tenant's data, even if status is 403/404. 
(b) Database state - query before and after mutation attempts to prove no state change. 
(c) Response timing - note if deny responses have significantly different timing than allow (information leak). 
Load [evidence collection reference](references/evidence-collection.md).

## 4. Verify Database State Integrity
After every denied mutation (PUT/POST/DELETE), query the database to confirm the target resource is unchanged. Compare checksums/timestamps before and after. A 403 response means nothing if the database was actually modified. This is the critical differentiator.

## 5. Build Regression Tests
Generate executable test cases for each boundary. Tests should assert on response CONTENT, not just status codes. Include state verification. Load [regression testing reference](references/regression-testing.md).

## 6. Remediate and Verify
For each finding, provide specific fix with before/after code. Apply fix, rerun the specific probe, verify the leak is closed AND legitimate access still works. Load [remediation patterns reference](references/remediation-patterns.md).

## 7. Deliver Evidence Report
Use [audit report template](assets/audit-report.md). Include: PAR matrix with results, evidence for each finding (request, response body excerpt, database state), regression test suite, remediation applied, re-verification results. Status: `secure` (all boundaries hold), `vulnerable` (leaks found), `partial` (not all boundaries tested).
