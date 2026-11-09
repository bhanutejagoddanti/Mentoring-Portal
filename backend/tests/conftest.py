import sys
from pathlib import Path
import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

@pytest.fixture(scope='session')
def client():
    import app as app_module
    flask_app = app_module.app
    flask_app.testing = True
    with flask_app.test_client() as c:
        yield c
