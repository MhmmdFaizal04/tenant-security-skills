# Evidence Collection Guide

Proper evidence collection is critical. A 403 Forbidden status code is insufficient proof of security if the response body contains sensitive data or the database state was modified.

## Response Content Analysis
When testing cross-tenant boundaries, inspect the full response body.
- **Data Leaks:** Look for tenant identifiers, usernames, PII, or internal resource IDs that belong to the target tenant.
- **Error Messages:** Verbose error messages (e.g., "Invoice 1234 belongs to Tenant B") leak existence and association.
- **Headers:** Check custom headers for leaked metadata.
- **Proper vs. Improper Denial:** A proper denial returns a 403/404 with a generic message and NO sensitive data. An improper denial returns a 403 but includes the requested data in the response body.

## Database State Snapshots
For mutation attempts (POST/PUT/DELETE) across tenant boundaries, verify the database state.
1. **Pre-mutation snapshot:** Query the target resource in the database and record its state (e.g., timestamps, values).
2. **Attempt mutation:** Execute the cross-tenant request.
3. **Post-mutation snapshot:** Query the target resource again.
4. **Comparison:** Prove the state has not changed. If the API returns 403 but the database record is updated, the application is vulnerable.

## Timing and Cache Leaks
- **Timing Attacks:** If a request for an existing cross-tenant resource takes 500ms (and returns 404) but a request for a non-existent resource takes 10ms, the timing difference leaks existence.
- **Cache Leaks:** Ensure that accessing a resource as Tenant A does not cache the response for Tenant B. Verify Cache-Control headers.

## Aggregate Endpoints
When testing endpoints that return multiple resources (e.g., search, list):
- Authenticate as Tenant A.
- Search for a unique string known to exist only in Tenant B's data.
- The response must be empty. If Tenant B's data is returned, tenant isolation is broken at the query level.

## Format of Evidence
Record findings systematically:
- **Request:** Full HTTP request (Method, URL, Headers).
- **Response Status:** HTTP status code.
- **Response Body:** Excerpt demonstrating the leak (if applicable).
- **Database Query:** The SQL/NoSQL query used for verification.
- **Database Result:** State comparison (before/after).
