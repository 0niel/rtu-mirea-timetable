import warnings

import pytest
from fastapi.testclient import TestClient

from app.config import config
from app.database import get_db_facade
from app.main import app
from tests.mock.db import MockDBFacade


@pytest.fixture
def db_facade():
    return MockDBFacade()


@pytest.fixture
def patch_settings():
    config.DEBUG = True
    warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture
def client(db_facade, patch_settings):
    test_client = TestClient(app)
    app.dependency_overrides[get_db_facade] = lambda: db_facade

    return test_client
