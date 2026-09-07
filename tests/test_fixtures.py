"""Tests for tenant security fixtures.

Verifies that the vulnerable API has the expected vulnerabilities
and that the secure API properly enforces tenant boundaries.
Uses real Flask test clients against the actual fixture code.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name, filepath):
    """Import a module by file path to avoid naming conflicts."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vuln_mod = _load_module('vuln_app', ROOT / 'fixtures' / 'vulnerable-api' / 'app.py')
secure_mod = _load_module('secure_app', ROOT / 'fixtures' / 'secure-api' / 'app.py')

ACME_ADMIN = {'X-API-Key': 'acme-admin-key-001'}
ACME_MEMBER = {'X-API-Key': 'acme-member-key-001'}
GLOBEX_ADMIN = {'X-API-Key': 'globex-admin-key-001'}


# -- Fixtures --

@pytest.fixture
def vuln_client():
    """Create a test client for the vulnerable API."""
    app = vuln_mod.create_app()
    vuln_mod.init_db(app)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def secure_client():
    """Create a test client for the secure API."""
    app = secure_mod.create_app()
    secure_mod.init_db(app)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# -- Health --

def test_health(vuln_client, secure_client):
    """Both apps respond to health check."""
    assert vuln_client.get('/health').status_code == 200
    assert secure_client.get('/health').status_code == 200


# -- Authentication --

def test_missing_api_key(vuln_client):
    """Requests without an API key are rejected."""
    resp = vuln_client.get('/api/projects')
    assert resp.status_code == 401


def test_invalid_api_key(vuln_client):
    """Requests with an invalid API key are rejected."""
    resp = vuln_client.get('/api/projects', headers={'X-API-Key': 'fake-key'})
    assert resp.status_code == 401


# -- Legitimate access (both apps) --

def test_legitimate_project_list(vuln_client, secure_client):
    """Users can list their own tenant's projects."""
    for client in [vuln_client, secure_client]:
        resp = client.get('/api/projects', headers=ACME_ADMIN)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        assert all(p['tenant_id'] == 1 for p in data)


def test_legitimate_project_read(vuln_client, secure_client):
    """Users can read their own tenant's project by ID."""
    for client in [vuln_client, secure_client]:
        resp = client.get('/api/projects/1', headers=ACME_ADMIN)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == 1
        assert data['tenant_id'] == 1


def test_legitimate_user_list_secure(secure_client):
    """Secure app returns only own tenant's users."""
    resp = secure_client.get('/api/users', headers=ACME_ADMIN)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert all(u['tenant_id'] == 1 for u in data)


# -- Vulnerable app: IDOR on project read --

def test_vuln_idor_project_read(vuln_client):
    """VULNERABILITY: Acme admin can read Globex project (cross-tenant IDOR)."""
    resp = vuln_client.get('/api/projects/3', headers=ACME_ADMIN)
    assert resp.status_code == 200, "Expected 200 because the vulnerability allows it"
    data = resp.get_json()
    # Evidence: response body contains another tenant's data
    assert data['tenant_id'] == 2, "Response leaks Globex (tenant 2) data"
    assert data['name'] == 'Project Gamma'


# -- Vulnerable app: cross-tenant state mutation --

def test_vuln_cross_tenant_mutation(vuln_client):
    """VULNERABILITY: Acme admin can modify Globex project (cross-tenant mutation)."""
    # Record state before
    before = vuln_client.get('/api/projects/3', headers=GLOBEX_ADMIN).get_json()
    original_budget = before['budget']

    # Attempt cross-tenant mutation
    resp = vuln_client.put(
        '/api/projects/3',
        headers=ACME_ADMIN,
        json={'budget': 999999.0},
    )
    assert resp.status_code == 200, "Expected 200 because the vulnerability allows it"

    # Evidence: database state was actually modified
    after = vuln_client.get('/api/projects/3', headers=GLOBEX_ADMIN).get_json()
    assert after['budget'] == 999999.0, "Database was mutated by cross-tenant request"
    assert after['budget'] != original_budget


# -- Vulnerable app: user enumeration --

def test_vuln_user_enumeration(vuln_client):
    """VULNERABILITY: User listing returns users from ALL tenants."""
    resp = vuln_client.get('/api/users', headers=ACME_ADMIN)
    assert resp.status_code == 200
    data = resp.get_json()
    tenant_ids = {u['tenant_id'] for u in data}
    # Evidence: response contains users from tenant 2
    assert 2 in tenant_ids, "Response leaks Globex (tenant 2) user data"
    assert len(data) == 4, "All four users returned regardless of tenant"


# -- Vulnerable app: IDOR on user read --

def test_vuln_idor_user_read(vuln_client):
    """VULNERABILITY: Acme admin can read Globex user profile."""
    resp = vuln_client.get('/api/users/3', headers=ACME_ADMIN)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['tenant_id'] == 2, "Response leaks Globex user data"
    assert data['name'] == 'charlie'


# -- Secure app: IDOR fixed --

def test_secure_idor_project_blocked(secure_client):
    """FIX: Cross-tenant project read returns 404."""
    resp = secure_client.get('/api/projects/3', headers=ACME_ADMIN)
    assert resp.status_code == 404, "Cross-tenant access should be denied"
    data = resp.get_json()
    # Evidence: response does NOT contain Globex data
    assert 'tenant_id' not in data
    assert 'Gamma' not in json.dumps(data)


# -- Secure app: cross-tenant mutation blocked --

def test_secure_cross_tenant_mutation_blocked(secure_client):
    """FIX: Cross-tenant project mutation returns 404 and DB is unchanged."""
    # Record state before via Globex admin (legitimate access)
    before = secure_client.get('/api/projects/3', headers=GLOBEX_ADMIN).get_json()
    original_budget = before['budget']

    # Attempt cross-tenant mutation as Acme admin
    resp = secure_client.put(
        '/api/projects/3',
        headers=ACME_ADMIN,
        json={'budget': 999999.0},
    )
    assert resp.status_code == 404, "Cross-tenant mutation should be denied"

    # Evidence: database state is UNCHANGED
    after = secure_client.get('/api/projects/3', headers=GLOBEX_ADMIN).get_json()
    assert after['budget'] == original_budget, "Database must not be modified"


# -- Secure app: enumeration fixed --

def test_secure_user_enumeration_fixed(secure_client):
    """FIX: User listing returns only own tenant's users."""
    resp = secure_client.get('/api/users', headers=ACME_ADMIN)
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(u['tenant_id'] == 1 for u in data), "No cross-tenant users"
    assert len(data) == 2, "Only Acme's two users returned"


# -- Secure app: user IDOR fixed --

def test_secure_idor_user_blocked(secure_client):
    """FIX: Cross-tenant user read returns 404."""
    resp = secure_client.get('/api/users/3', headers=ACME_ADMIN)
    assert resp.status_code == 404
    data = resp.get_json()
    assert 'charlie' not in json.dumps(data)


# -- Expected findings validation --

def test_expected_findings_structure():
    """Expected findings files are well-formed."""
    vuln_path = ROOT / 'fixtures' / 'expected' / 'vulnerable-findings.json'
    secure_path = ROOT / 'fixtures' / 'expected' / 'secure-findings.json'

    vuln_findings = json.loads(vuln_path.read_text(encoding='utf-8'))
    secure_findings = json.loads(secure_path.read_text(encoding='utf-8'))

    assert len(vuln_findings) == 4, "Vulnerable API should have 4 findings"
    assert len(secure_findings) == 0, "Secure API should have 0 findings"
    assert all('id' in f and 'type' in f and 'severity' in f for f in vuln_findings)
