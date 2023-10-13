import json
import typing
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


def _setup_mock_transcript_data() -> typing.Dict[Assembly, typing.Any]:
    hgnc_to_transcripts_grch37: dict[str, list[typing.Any]] = {}
    assembly_to_hgnc_to_transcripts_grch37: dict[Assembly, dict[str, list[typing.Any]]] = {}

    transcript_info_grch37 = json.load(open("tests/data/cdot-0.2.21.refseq.grch37.json", "r"))
    for transcript in transcript_info_grch37["transcripts"].values():
        hgnc_id = f"HGNC:{transcript['hgnc']}"
        hgnc_to_transcripts_grch37.setdefault(hgnc_id, []).append(transcript)
    assembly_to_hgnc_to_transcripts_grch37[Assembly.GRCH37] = hgnc_to_transcripts_grch37

    hgnc_to_transcripts_grch38: dict[str, list[typing.Any]] = {}
    assembly_to_hgnc_to_transcripts_grch38: dict[Assembly, dict[str, list[typing.Any]]] = {}

    transcript_info_grch38 = json.load(open("tests/data/cdot-0.2.21.refseq.grch38.json", "r"))
    for transcript in transcript_info_grch38["transcripts"].values():
        hgnc_id = f"HGNC:{transcript['hgnc']}"
        hgnc_to_transcripts_grch38.setdefault(hgnc_id, []).append(transcript)
    assembly_to_hgnc_to_transcripts_grch38[Assembly.GRCH38] = hgnc_to_transcripts_grch38

    assembly_to_hgnc_to_transcripts = {
        **assembly_to_hgnc_to_transcripts_grch37,
        **assembly_to_hgnc_to_transcripts_grch38,
    }

    return assembly_to_hgnc_to_transcripts


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


def test_find_transctipts_grch37(test_client: TestClient, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(dotty_main, "driver", _setup_mock_driver("g", "NC_000017.11"))
    monkeypatch.setattr(
        dotty_main, "assembly_to_hgnc_to_transcripts", _setup_mock_transcript_data()
    )
    response = test_client.get("/api/v1/find-transcripts?hgnc_id=HGNC:1100&assembly=GRCh37")
    assert response.status_code == 200

    expected: dict[str, list] = {"transcripts": []}

    # Load the transcript data from the test data
    transcript_info_grch37 = json.load(open("tests/data/cdot-0.2.21.refseq.grch37.json", "r"))
    for transcript in transcript_info_grch37["transcripts"].values():
        if transcript["hgnc"] == "1100":
            if (
                transcript["genome_builds"].get("GRCh37", None) is None
                or transcript["genome_builds"]["GRCh37"].get("cds_start", None) is None
                or transcript["genome_builds"]["GRCh37"].get("cds_end", None) is None
                or transcript["genome_builds"]["GRCh37"].get("exons", None) is None
            ):
                continue
            expected["transcripts"].append(
                {
                    "transcript_id": transcript["id"].split(".")[0],
                    "transcript_version": transcript["id"].split(".")[1],
                    "gene_id": f"HGNC:{transcript['hgnc']}",
                    "gene_name": transcript["gene_name"],
                    "contig": transcript["genome_builds"]["GRCh37"]["contig"],
                    "cds_start": transcript["genome_builds"]["GRCh37"]["cds_start"],
                    "cds_end": transcript["genome_builds"]["GRCh37"]["cds_end"],
                    "exons": [
                        {"start": exon[0], "end": exon[1]}
                        for exon in transcript["genome_builds"]["GRCh37"]["exons"]
                    ],
                }
            )

    assert response.json() == expected


def test_find_transcripts_grch38(test_client: TestClient, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(dotty_main, "driver", _setup_mock_driver("g", "NC_000017.11"))
    monkeypatch.setattr(
        dotty_main, "assembly_to_hgnc_to_transcripts", _setup_mock_transcript_data()
    )
    response = test_client.get("/api/v1/find-transcripts?hgnc_id=HGNC:1100&assembly=GRCh38")
    assert response.status_code == 200

    expected: dict[str, list] = {"transcripts": []}

    # Load the transcript data from the test data
    transcript_info_grch37 = json.load(open("tests/data/cdot-0.2.21.refseq.grch38.json", "r"))
    for transcript in transcript_info_grch37["transcripts"].values():
        if transcript["hgnc"] == "1100":
            if (
                transcript["genome_builds"].get("GRCh38", None) is None
                or transcript["genome_builds"]["GRCh38"].get("cds_start", None) is None
                or transcript["genome_builds"]["GRCh38"].get("cds_end", None) is None
                or transcript["genome_builds"]["GRCh38"].get("exons", None) is None
            ):
                continue
            expected["transcripts"].append(
                {
                    "transcript_id": transcript["id"].split(".")[0],
                    "transcript_version": transcript["id"].split(".")[1],
                    "gene_id": f"HGNC:{transcript['hgnc']}",
                    "gene_name": transcript["gene_name"],
                    "contig": transcript["genome_builds"]["GRCh38"]["contig"],
                    "cds_start": transcript["genome_builds"]["GRCh38"]["cds_start"],
                    "cds_end": transcript["genome_builds"]["GRCh38"]["cds_end"],
                    "exons": [
                        {"start": exon[0], "end": exon[1]}
                        for exon in transcript["genome_builds"]["GRCh38"]["exons"]
                    ],
                }
            )

    assert response.json() == expected
