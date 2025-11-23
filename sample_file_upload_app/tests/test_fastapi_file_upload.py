'''Always test:
✔ Happy path
✔ Edge cases
✔ Invalid input
✔ Error behavior
✔ Performance-sensitive logic (lightly)
'''

# test_uploads.py
import io
from fastapi.testclient import TestClient
from app import app, UPLOAD_DIR
from pathlib import Path

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_single_upload(tmp_path):
    # create a small test file bytes
    file_bytes = b"hello world"
    files = {"file": ("hello.txt", io.BytesIO(file_bytes), "text/plain")}
    r = client.post("/upload/single", files=files)
    assert r.status_code == 200
    assert "stored_as" in r.json()
    p = Path(UPLOAD_DIR) / stored_as
    assert p.exists()
    assert p.read_bytes() == file_bytes
    p.unlink()

def test_multiple_upload(tmp_path):
    files = [
        ("files", ("a.txt", io.BytesIO(b"a"), "text/plain")),
        ("files", ("b.txt", io.BytesIO(b"b"), "text/plain")),
    ]
    r = client.post("/upload/multiple", files=files)
    assert r.status_code == 200
    uploaded = r.json()["uploaded"]
    assert len(uploaded) == 2
    # cleanup
    for info in uploaded:
        p = Path(UPLOAD_DIR) / info["stored_as"]
        if p.exists():
            p.unlink()
