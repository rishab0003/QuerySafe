from fastapi.testclient import TestClient
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import create_app  # noqa: E402
from scripts.init_demo_db import init_db


def test_demo_endpoints(tmp_path):
    # create a demo db in a temp directory
    db_file = tmp_path / 'demo.sqlite'
    init_db(str(db_file))

    # copy the demo sqlite to backend/demo/demo.sqlite location so routes find it
    target_dir = Path(__file__).resolve().parents[1] / 'demo'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_db = target_dir / 'demo.sqlite'
    if target_db.exists():
        target_db.unlink()
    target_db.write_bytes(db_file.read_bytes())

    app = create_app()
    client = TestClient(app)

    r = client.get('/demo/employees')
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert any(e['approval_status'] == 'approved' for e in r.json())

    r2 = client.get('/demo/signups')
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data, list)
    assert len(data) == 7
