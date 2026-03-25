"""
Pytest configuration and shared fixtures for FastAPI tests.

Provides:
- TestClient for the FastAPI app
- Fresh activities data for test isolation
- Fixture to reset activities between tests
"""

import pytest
import sys
from pathlib import Path
from copy import deepcopy
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def fresh_activities():
    """
    Provides a deep copy of the activities database.
    This ensures each test has a clean slate and modifications
    don't affect other tests.
    """
    return deepcopy(activities)


@pytest.fixture
def client(fresh_activities, monkeypatch):
    """
    Provides a TestClient for the FastAPI app with isolated state.
    
    Uses monkeypatch to replace the global activities dict with a fresh copy
    for this test, ensuring test isolation and no state leakage between tests.
    """
    # Replace the global activities in the app module with our fresh copy
    monkeypatch.setattr("app.activities", fresh_activities)
    return TestClient(app)
