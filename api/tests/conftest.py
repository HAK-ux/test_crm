import os
import pytest
from rest_framework.test import APIClient

os.environ["PYTEST_RUNNING"] = "1"

@pytest.fixture
def api_client():
    return APIClient()