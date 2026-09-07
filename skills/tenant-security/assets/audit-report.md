# Tenant Security Audit Report

## Summary
- **Target:**
- **Date:**
- **Status:** [secure / vulnerable / partial]
- **Findings:** X vulnerabilities, Y verified boundaries

## Authorization Matrix
| # | Principal | Resource | Action | Expected | Actual | Evidence | Status |
|---|-----------|----------|--------|----------|--------|----------|--------|
| | | | | | | | |

## Findings
### Finding [N]: [Title]
- **Severity:** [Critical / High / Medium / Low]
- **Type:** [IDOR / Enumeration / State Mutation / Data Leak]
- **Principal:** (who can exploit)
- **Resource:** (what is exposed)
- **Evidence:**
  - Request: `[method] [url]`
  - Response status: [code]
  - Response body contains: [excerpt showing leaked data]
  - Database state: [before/after comparison]
- **Remediation:** [applied fix]
- **Re-verification:** [result after fix]

## Regression Test Suite
- **Location:**
- **How to run:**
- **Coverage:** X of Y boundaries tested

## Limitations
- Boundaries not tested and why
- Environment constraints
- Timing/cache considerations
