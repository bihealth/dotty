import pytest
from hgvs.exceptions import HGVSDataNotAvailableError

from dotty.core import Assembly, Driver


def test_driver_c_to_g(
    settings_no_seqrepo: None, mock_seqrepo_fetching: None, dotty_driver: Driver
):
    var_c = dotty_driver.parser.parse("NM_007294.3:c.5588A>G")
    result = {
        assembly.value: str(dotty_driver.assembly_mappers[assembly].c_to_g(var_c))
        for assembly in Assembly
    }
    expected = {
        "GRCh37": "NC_000017.10:g.41197699T>C",
        "GRCh38": "NC_000017.11:g.43045682T>C",
    }
    assert result == expected


def test_driver_n_to_g(
    settings_no_seqrepo: None, mock_seqrepo_fetching: None, dotty_driver: Driver
):
    var_n = dotty_driver.parser.parse("NR_027676.2:n.5765A>G")
    result = {
        assembly.value: str(dotty_driver.assembly_mappers[assembly].n_to_g(var_n))
        for assembly in Assembly
    }
    expected = {
        "GRCh37": "NC_000017.10:g.41197699T>C",
        "GRCh38": "NC_000017.11:g.43045682T>C",
    }
    assert result == expected


def test_driver_t_to_g_with_var_c(
    settings_no_seqrepo: None, mock_seqrepo_fetching: None, dotty_driver: Driver
):
    var_c = dotty_driver.parser.parse("NM_007294.3:c.5588A>G")
    result = {
        assembly.value: str(dotty_driver.assembly_mappers[assembly].c_to_g(var_c))
        for assembly in Assembly
    }
    expected = {
        "GRCh37": "NC_000017.10:g.41197699T>C",
        "GRCh38": "NC_000017.11:g.43045682T>C",
    }
    assert result == expected


def test_driver_t_to_g_with_var_n(
    settings_no_seqrepo: None, mock_seqrepo_fetching: None, dotty_driver: Driver
):
    var_n = dotty_driver.parser.parse("NR_027676.2:n.5765A>G")
    result = {
        assembly.value: str(dotty_driver.assembly_mappers[assembly].n_to_g(var_n))
        for assembly in Assembly
    }
    expected = {
        "GRCh37": "NC_000017.10:g.41197699T>C",
        "GRCh38": "NC_000017.11:g.43045682T>C",
    }
    assert result == expected
