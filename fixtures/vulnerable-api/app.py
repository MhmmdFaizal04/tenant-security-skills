"""Vulnerable multi-tenant API fixture.

Intentionally contains IDOR and enumeration vulnerabilities for testing.
This is synthetic test code -- do not use in production.
"""
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, jsonify, g


def create_app(database=':memory:'):
    """Create the Flask application.

    Args:
        database: SQLite database path. Defaults to in-memory with a shared
                  connection so data persists across request contexts.
    """
    app = Flask(__name__)
    app.config['DATABASE'] = database

    # For in-memory databases, maintain a persistent connection
    # so seeded data survives across request contexts.
    if database == ':memory:':
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        app.extensions['shared_db'] = conn
    else:
        app.extensions['shared_db'] = None

    def get_db():
        shared = app.extensions.get('shared_db')
        if shared is not None:
            return shared
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(exc):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def require_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({"error": "Missing API key"}), 401
            db = get_db()
            row = db.execute(
                "SELECT u.id, u.tenant_id, u.name, u.role "
                "FROM users u JOIN api_keys k ON u.id = k.user_id "
                "WHERE k.key = ?",
                (api_key,),
            ).fetchone()
            if not row:
                return jsonify({"error": "Invalid API key"}), 401
            g.current_user = dict(row)
            return f(*args, **kwargs)
        return decorated

    # -- Routes --

    @app.route('/health')
    def health():
        return jsonify({"status": "ok"})

    @app.route('/api/projects', methods=['GET'])
    @require_auth
    def list_projects():
        db = get_db()
        # This endpoint is correctly filtered by tenant
        rows = db.execute(
            "SELECT id, tenant_id, name, description, budget, updated_at "
            "FROM projects WHERE tenant_id = ?",
            (g.current_user['tenant_id'],),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/projects/<int:pid>', methods=['GET'])
    @require_auth
    def get_project(pid):
        db = get_db()
        # VULNERABILITY: No tenant boundary check -- returns any project by ID
        row = db.execute(
            "SELECT id, tenant_id, name, description, budget, updated_at "
            "FROM projects WHERE id = ?",
            (pid,),
        ).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(row))

    @app.route('/api/projects/<int:pid>', methods=['PUT'])
    @require_auth
    def update_project(pid):
        db = get_db()
        # VULNERABILITY: No tenant boundary check -- modifies any project
        row = db.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        data = request.get_json(silent=True) or {}
        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            "UPDATE projects SET name=?, description=?, budget=?, updated_at=? WHERE id=?",
            (
                data.get('name', row['name']),
                data.get('description', row['description']),
                data.get('budget', row['budget']),
                now,
                pid,
            ),
        )
        db.commit()
        updated = db.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
        return jsonify(dict(updated))

    @app.route('/api/users', methods=['GET'])
    @require_auth
    def list_users():
        db = get_db()
        # VULNERABILITY: No tenant filter -- returns ALL users across tenants
        rows = db.execute(
            "SELECT id, tenant_id, name, email, role FROM users"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/users/<int:uid>', methods=['GET'])
    @require_auth
    def get_user(uid):
        db = get_db()
        # VULNERABILITY: No tenant boundary check -- returns any user by ID
        row = db.execute(
            "SELECT id, tenant_id, name, email, role FROM users WHERE id = ?",
            (uid,),
        ).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(row))

    return app


def init_db(app):
    """Seed the database with two tenants, four users, and four projects."""
    shared = app.extensions.get('shared_db')
    if shared:
        db = shared
    else:
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row

    db.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            name TEXT NOT NULL, email TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','member'))
        );
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            name TEXT NOT NULL, description TEXT,
            budget REAL DEFAULT 0, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id)
        );
    """)

    now = datetime.now(timezone.utc).isoformat()

    db.execute("INSERT OR IGNORE INTO tenants VALUES (1,'Acme Corp')")
    db.execute("INSERT OR IGNORE INTO tenants VALUES (2,'Globex Inc')")

    db.execute("INSERT OR IGNORE INTO users VALUES (1,1,'alice','alice@acme.test','admin')")
    db.execute("INSERT OR IGNORE INTO users VALUES (2,1,'bob','bob@acme.test','member')")
    db.execute("INSERT OR IGNORE INTO users VALUES (3,2,'charlie','charlie@globex.test','admin')")
    db.execute("INSERT OR IGNORE INTO users VALUES (4,2,'diana','diana@globex.test','member')")

    db.execute("INSERT OR IGNORE INTO api_keys VALUES ('acme-admin-key-001',1)")
    db.execute("INSERT OR IGNORE INTO api_keys VALUES ('acme-member-key-001',2)")
    db.execute("INSERT OR IGNORE INTO api_keys VALUES ('globex-admin-key-001',3)")
    db.execute("INSERT OR IGNORE INTO api_keys VALUES ('globex-member-key-001',4)")

    for pid, tid, name, desc, budget in [
        (1, 1, 'Project Alpha', 'Alpha description', 50000.0),
        (2, 1, 'Project Beta', 'Beta description', 30000.0),
        (3, 2, 'Project Gamma', 'Gamma description', 75000.0),
        (4, 2, 'Project Delta', 'Delta description', 20000.0),
    ]:
        db.execute(
            "INSERT OR IGNORE INTO projects VALUES (?,?,?,?,?,?)",
            (pid, tid, name, desc, budget, now),
        )

    db.commit()
    if not shared:
        db.close()


if __name__ == '__main__':
    application = create_app()
    init_db(application)
    print("Vulnerable API running on http://localhost:5001")
    print("Try: curl -H 'X-API-Key: acme-admin-key-001' http://localhost:5001/api/projects/3")
    application.run(port=5001)
