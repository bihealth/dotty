import enum
import logging
import os
import pathlib
import time
from datetime import timedelta
from unittest import mock

import bioutils.assemblies
import hgvs.parser
from bioutils.sequences import reverse_complement
from cdot.hgvs.dataproviders import JSONDataProvider
from hgvs.assemblymapper import AssemblyMapper
from hgvs.dataproviders.interface import Interface
from hgvs.extras import babelfish
from hgvs.sequencevariant import SequenceVariant

from dotty.config import settings

#: Logger used in this module.
_logger = logging.getLogger(__name__)


class Babelfish(babelfish.Babelfish):
    """Custom Babelfish that also knows about GRCh37 and properly handles SNVs."""

    def __init__(self, hdp: Interface, assembly_name: str):
        super().__init__(hdp, assembly_name)
        for assembly_name in ("GRCh37", "GRCh38"):
            for sr in bioutils.assemblies.get_assembly(assembly_name)["sequences"]:
                self.ac_to_chr_name_map[sr["refseq_ac"]] = sr["name"]

    def hgvs_to_vcf(self, var_g: SequenceVariant) -> tuple[str, int, str, str, str]:
        if var_g.type != "g":
            raise RuntimeError("Expected g. variant, got {var_g}".format(var_g=var_g))

        vleft = self.hn.normalize(var_g)

        (start_i, end_i) = babelfish._as_interbase(vleft.posedit)

        chrom = self.ac_to_chr_name_map[vleft.ac]

        typ = vleft.posedit.edit.type

        if typ == "dup":
            start_i -= 1
            alt = self.hdp.seqfetcher.fetch_seq(vleft.ac, start_i, end_i)
            ref = alt[0]
        elif typ == "inv":
            ref = vleft.posedit.edit.ref
            alt = reverse_complement(ref)
        else:
            alt = vleft.posedit.edit.alt or ""

            if typ in ("del", "ins"):  # Left anchored
                start_i -= 1
                ref = self.hdp.seqfetcher.fetch_seq(vleft.ac, start_i, end_i)
                alt = ref[0] + alt
            else:
                ref = vleft.posedit.edit.ref
                if ref == alt:
                    alt = "."
        return chrom, start_i + 1, ref, alt, typ


class Assembly(enum.Enum):
    """Enumeration for supported assemblies."""

    #: GRCh37 assembly.
    GRCH37 = "GRCh37"
    #: GRCh38 assembly.
    GRCH38 = "GRCh38"


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
        #: One Babelfish for each assembly.
        self.babelfishes: dict[Assembly, Babelfish] = {}
        #: The HGVS parser.
        self.parser = hgvs.parser.Parser()

    def load(self):
        """Loads the data from the files."""
        _logger.info("Loading data from %s: %s ...", self.cdot_dir, self.assembly_file_names)
        start_time = time.time()

        # We temporarily override the HGVS_SEQREPO_DIR environment variable for construction
        # of hgvs / cdot objects.
        with mock.patch.dict(os.environ, {"HGVS_SEQREPO_DIR": str(self.cdot_dir / "seqrepo")}):
            self.data_providers = {
                assembly: JSONDataProvider(
                    [str(self.cdot_dir / fname) for fname in assembly_file_names],
                )
                for assembly, assembly_file_names in self.assembly_file_names.items()
            }
            self.assembly_mappers = {
                assembly: AssemblyMapper(
                    self.data_providers[assembly],
                    assembly_name=assembly.value,
                    alt_aln_method="splign",
                    normalize=settings.HAVE_SEQREPO,
                    replace_reference=settings.HAVE_SEQREPO,
                    prevalidation_level=None,
                )
                for assembly in Assembly
            }
            self.babelfishes = {
                assembly: Babelfish(hdp=self.data_providers[assembly], assembly_name=assembly.value)
                for assembly in Assembly
            }
        elapsed = timedelta(seconds=time.time() - start_time)
        _logger.info("... loaded in %s", elapsed)
