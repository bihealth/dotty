import pytest

from dotty.core import Driver


@pytest.fixture(scope="session")
def dotty_driver():
    driver = Driver("tests/data")
    driver.load()
    yield driver
