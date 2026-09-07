# Remediation Patterns

When tenant isolation vulnerabilities are found, apply the appropriate remediation pattern based on the application's architecture.

## 1. Middleware-Level Tenant Scoping
Ensure the tenant context is established early in the request lifecycle and made immutable.

**Vulnerable:**
```javascript
// Trusting client input for tenant ID
app.get('/api/data', (req, res) => {
  const tenantId = req.query.tenantId;
  Data.find({ tenant: tenantId }).then(data => res.json(data));
});
```

**Remediation:**
```javascript
// Extracting tenant from verified JWT
app.use((req, res, next) => {
  req.tenantId = req.user.tenantId; 
  next();
});

app.get('/api/data', (req, res) => {
  Data.find({ tenant: req.tenantId }).then(data => res.json(data));
});
```

## 2. Query-Level Tenant Filtering
Every database query must include the tenant identifier.

**Vulnerable:**
```python
def get_invoice(invoice_id):
    # Missing tenant filter allows IDOR
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()
```

**Remediation:**
```python
def get_invoice(invoice_id, current_tenant_id):
    # Enforces tenant boundary
    return db.query(Invoice).filter(
        Invoice.id == invoice_id, 
        Invoice.tenant_id == current_tenant_id
    ).first()
```

## 3. Row-Level Security (PostgreSQL)
Push tenant isolation down to the database level to prevent application bugs from leaking data.

**Remediation (SQL):**
```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON invoices
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```
*Application must set `app.current_tenant` at the start of each transaction.*

## 4. ORM-Level Tenant Context
Use ORM features (like global scopes) to automatically apply tenant filters.

**Remediation (Example concept):**
```ruby
# Rails default_scope example
class ApplicationRecord < ActiveRecord::Base
  self.abstract_class = true
  default_scope { where(tenant_id: Current.tenant_id) if Current.tenant_id.present? }
end
```

## Verification Steps
After applying a fix:
1. Run the specific cross-tenant probe that failed previously.
2. Verify the data leak is closed (response body is safe).
3. Verify database state integrity holds (no unauthorized mutations).
4. Run legitimate access tests to ensure standard functionality is not broken.

## Common Mistakes
- Fixing the API endpoint but forgetting background workers processing the same data.
- Securing single-resource lookups (`GET /id`) but missing batch/search endpoints.
- Relying on UI hiding rather than backend enforcement.
