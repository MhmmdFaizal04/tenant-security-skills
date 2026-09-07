# Regression Testing Guide

Regression tests ensure that verified tenant boundaries remain secure over time. Tests must validate both response content and database state.

## Test Structure
A robust tenant security test follows this pattern:
1. **Setup:** Provision data for Tenant A and Tenant B.
2. **Authenticate:** Obtain credentials for Tenant A.
3. **Pre-State (Mutations):** Record database state for Tenant B's resource.
4. **Execute:** Make the request as Tenant A against Tenant B's resource.
5. **Assert Content:** Verify response status AND ensure response body does not contain Tenant B's data.
6. **Assert State (Mutations):** Verify database state for Tenant B's resource is unchanged.
7. **Cleanup:** Remove provisioned data.

## Content-Based Assertions
Do not rely solely on `assert response.status_code == 403`.
- Verify the response body is empty or contains only a generic error.
- Explicitly assert that sensitive strings (e.g., Tenant B's names, specific IDs) are not present in the response text.

## Database State Verification
Incorporate direct database queries into the test suite.
- Connect to the test database.
- Fetch the record before the HTTP request.
- Fetch the record after the HTTP request.
- Assert equality of critical fields and `updated_at` timestamps.

## Example (Python/pytest)
```python
def test_cross_tenant_update_prevented(db_session, api_client, tenant_a_token, tenant_b_invoice):
    # Setup
    client = api_client(token=tenant_a_token)
    
    # Pre-State
    original_amount = db_session.query(Invoice).get(tenant_b_invoice.id).amount
    
    # Execute
    payload = {"amount": 9999}
    response = client.put(f"/api/invoices/{tenant_b_invoice.id}", json=payload)
    
    # Assert Content
    assert response.status_code in [403, 404]
    assert "9999" not in response.text
    assert str(original_amount) not in response.text # Ensure original data not leaked
    
    # Assert State
    current_amount = db_session.query(Invoice).get(tenant_b_invoice.id).amount
    assert current_amount == original_amount
```

## Handling Flakiness
- Use isolated test databases or schema per test run.
- Avoid hardcoded IDs; dynamically provision resources during setup.
- If testing timing attacks, use statistical significance rather than hard thresholds, though automated timing tests are notoriously flaky and better left to manual verification.
