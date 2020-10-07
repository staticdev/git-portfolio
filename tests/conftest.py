"""Package-wide test fixtures."""
import _pytest.config


def pytest_configure(config: _pytest.config.Config) -> None:
    """Pytest configuration hook."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
