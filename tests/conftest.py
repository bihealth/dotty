import pytest
from _pytest.monkeypatch import MonkeyPatch
from cdot.hgvs.dataproviders.json_data_provider import AbstractJSONDataProvider
from hgvs.dataproviders.seqfetcher import SeqFetcher

from dotty.config import settings
from dotty.core import Driver


@pytest.fixture(scope="session")
def dotty_driver():
    driver = Driver("tests/data")
    driver.load()
    yield driver


@pytest.fixture
def settings_no_seqrepo(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "HAVE_SEQREPO", False)


@pytest.fixture
def mock_seqrepo_fetching(monkeypatch: MonkeyPatch) -> None:
    """Mock out the sequence fetching as we do not want to have any data in tests/data/seqrepo.
    """
    monkeypatch.setattr(AbstractJSONDataProvider, "get_seq", lambda *args: "NN")
    monkeypatch.setattr(SeqFetcher, "fetch_seq", lambda *args: "NN")
