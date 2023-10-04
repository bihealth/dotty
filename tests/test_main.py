from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from dotty import main as dotty_main
from dotty.core import Assembly


def _setup_mock_driver(var_type: str, parsed_var_ac: str) -> Mock:
    parsed_var = Mock()
    parsed_var.type = var_type
    parsed_var.ac = parsed_var_ac

    g_var = Mock()

    grch38_am = Mock()
    grch38_am.c_to_g = Mock()
    grch38_am.c_to_g.return_value = g_var

    grch37_bf = Mock()
    grch37_bf.hgvs_to_vcf = Mock()
    grch37_bf.hgvs_to_vcf.return_value = ("chr1", 100, "A", "C", "g")

    grch38_bf = Mock()
    grch38_bf.hgvs_to_vcf = Mock()
    grch38_bf.hgvs_to_vcf.return_value = ("chr1", 100, "A", "C", "g")

    mock_driver = Mock()
    mock_driver.assembly_mappers = {
        Assembly.GRCH38: grch38_am,
    }
    mock_driver.babelfishes = {
        Assembly.GRCH37: grch37_bf,
        Assembly.GRCH38: grch38_bf,
    }
    mock_driver.parser = Mock()
    mock_driver.parser.parse = Mock()
    mock_driver.parser.parse.return_value = parsed_var

    return mock_driver


def test_to_spdi_c(test_client: TestClient, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(dotty_main, "driver", _setup_mock_driver("c", "NC_000017.10"))
    response = test_client.get("/api/v1/to-spdi?q=NM_000059.3:c.274G>A")
    assert response.status_code == 200
    expected = {
        "spdi": {
            "alternate_inserted": "C",
            "contig": "chr1",
            "pos": 100,
            "reference_deleted": "A",
            "assembly": "GRCh38",
        }
    }
    assert response.json() == expected


def test_to_spdi_n(test_client: TestClient, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(dotty_main, "driver", _setup_mock_driver("n", "NC_000017.10"))
    response = test_client.get("/api/v1/to-spdi?q=NM_000059.3:n.274G>A")
    assert response.status_code == 200
    expected = {
        "spdi": {
            "alternate_inserted": "C",
            "contig": "chr1",
            "pos": 100,
            "reference_deleted": "A",
            "assembly": "GRCh38",
        }
    }
    assert response.json() == expected


def test_to_spdi_g_37(test_client: TestClient, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(dotty_main, "driver", _setup_mock_driver("g", "NC_000017.10"))
    response = test_client.get("/api/v1/to-spdi?q=NC_000017.10:g.41197699T>C")
    assert response.status_code == 200
    expected = {
        "spdi": {
            "alternate_inserted": "C",
            "contig": "chr1",
            "pos": 100,
            "reference_deleted": "A",
            "assembly": "GRCh37",
        }
    }
    assert response.json() == expected


def test_to_spdi_g_38(test_client: TestClient, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(dotty_main, "driver", _setup_mock_driver("g", "NC_000017.11"))
    response = test_client.get("/api/v1/to-spdi?q=NC_000017.11:g.43045682T>C")
    assert response.status_code == 200
    expected = {
        "spdi": {
            "alternate_inserted": "C",
            "contig": "chr1",
            "pos": 100,
            "reference_deleted": "A",
            "assembly": "GRCh38",
        }
    }
    assert response.json() == expected
