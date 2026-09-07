import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/tenant-security/SKILL.md'
text = SKILL.read_text(encoding='utf-8')

# Frontmatter checks
assert text.startswith('---\nname: tenant-security\n'), 'Missing/mismatched frontmatter name'
assert len(text.splitlines()) < 500, 'Keep entry point under 500 lines'
assert len(list((ROOT / 'skills').rglob('SKILL.md'))) == 1, 'Exactly one skill expected'

# Required files
for rel in ['README.md', 'LICENSE', 'SECURITY.md', 'CONTRIBUTING.md', 'docs/README.id.md',
            'fixtures/vulnerable-api/app.py', 'fixtures/secure-api/app.py',
            'fixtures/expected/vulnerable-findings.json', 'fixtures/expected/secure-findings.json']:
    assert (ROOT / rel).is_file(), f'Missing: {rel}'

# Markdown link validation
for doc in ROOT.rglob('*.md'):
    if '.git' in doc.parts:
        continue
    for target in re.findall(r'\]\(([^\s)]+)\)', doc.read_text(encoding='utf-8')):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        assert (doc.parent / unquote(parsed.path)).exists(), f'Broken link in {doc}: {target}'

# Eval cases
cases = json.loads((ROOT / 'evals/cases.json').read_text(encoding='utf-8'))
assert len(cases) == 8 and len({c['id'] for c in cases}) == 8
assert all(c['expect'] and c['fail'] for c in cases)

# Content checks
assert 'version: "1.0.0"' in text
assert 'response content' in text.lower() or 'response body' in text.lower()
assert 'database state' in text.lower()
assert '## Security Considerations' in text

print('All validation checks passed.')
