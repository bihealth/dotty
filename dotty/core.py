import enum
import logging
import pathlib
import time
from datetime import timedelta

import hgvs.parser
from cdot.hgvs.dataproviders import JSONDataProvider
from hgvs.assemblymapper import AssemblyMapper
from hgvs.dataproviders.seqfetcher import SeqFetcher
from hgvs.exceptions import HGVSDataNotAvailableError

#: Logger used in this module.
_logger = logging.getLogger(__name__)


class Assembly(enum.Enum):
    """Enumeration for supported assemblies."""

    #: GRCh37 assembly.
    GRCH37 = "GRCh37"
    #: GRCh38 assembly.
    GRCH38 = "GRCh38"


class NullSeqFetcher(SeqFetcher):
    """A null sequence fetcher that always returns None."""

    def __init__(self):
        _logger.info("(Not) fetching sequences with NullSeqFetcher")

    def fetch_seq(self, ac, start_i=None, end_i=None):  # pragma: no cover
        _ = ac, start_i, end_i
        raise HGVSDataNotAvailableError("dotty cannot fetch sequences")


class Driver:
    """Provides references to the data files."""

    #: The file names to load for each assembly.
    assembly_file_names = {
        Assembly.GRCH37: (
            "cdot-0.2.21.ensembl.grch37.json.gz",
            "cdot-0.2.21.refseq.grch37.json.gz",
        ),
        Assembly.GRCH38: (
            "cdot-0.2.21.ensembl.grch38.json.gz",
            "cdot-0.2.21.refseq.grch38.json.gz",
        ),
    }

    def __init__(self, cdot_dir: str):
        #: Path to the cdot files.
        self.cdot_dir = pathlib.Path(cdot_dir)
        #: JSON data provider.
        self.data_providers: dict[Assembly, JSONDataProvider] = {}
        #: The assembly mapper to use for each genome.
        self.assembly_mappers: dict[Assembly, AssemblyMapper] = {}
        #: The HGVS parser.
        self.parser = hgvs.parser.Parser()

    def load(self):
        """Loads the data from the files."""
        _logger.info("Loading data from %s: %s ...", self.cdot_dir, self.assembly_file_names)
        start_time = time.time()
        self.data_providers = {
            assembly: JSONDataProvider(
                [str(self.cdot_dir / fname) for fname in assembly_file_names],
                seqfetcher=NullSeqFetcher(),
            )
            for assembly, assembly_file_names in self.assembly_file_names.items()
        }
        self.assembly_mappers = {
            assembly: AssemblyMapper(
                self.data_providers[assembly],
                assembly_name=assembly.value,
                alt_aln_method="splign",
                normalize=False,
                replace_reference=False,
                prevalidation_level=None,
            )
            for assembly in self.assembly_file_names
        }
        elapsed = timedelta(seconds=time.time() - start_time)
        _logger.info("... loaded in %s", elapsed)
