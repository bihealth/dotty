import logging
import typing
from contextlib import asynccontextmanager

import bioutils.assemblies
import hgvs.exceptions
import pydantic
from fastapi import FastAPI, HTTPException

from dotty.config import settings
from dotty.core import Assembly, Driver

logging.basicConfig(level=logging.DEBUG)

_logger = logging.getLogger(__name__)

#: The global Driver instance.
driver: Driver = None  # type: ignore[assignment]
#: Map from HGNC ID to transcripts.
hgnc_to_transcripts: dict[str, list[typing.Any]] = {}
#: Map from Assembly to map from hgnc_id to transcripts.
assembly_to_hgnc_to_transcripts: dict[Assembly, dict[str, list[typing.Any]]] = {}

#: Contig names per assembly.
contig_names: dict[Assembly, set[str]] = {
    assembly: set(
        sr["refseq_ac"] for sr in bioutils.assemblies.get_assembly(assembly.value)["sequences"]
    )
    for assembly in Assembly
}


@asynccontextmanager
async def lifespan(app: FastAPI):   # pragma: no cover
    global driver
    _ = app
    driver = Driver(cdot_dir=settings.DATA_DIR)
    driver.load()
    _logger.info("driver loaded")
    for assembly in Assembly:
        for transcript in driver.data_providers[assembly].transcripts.keys():
            if (
                assembly.value
                not in driver.data_providers[assembly]
                ._get_transcript(transcript)["genome_builds"]
                .keys()  # genome build is not in the transcript data
                or "hgnc" not in driver.data_providers[assembly]._get_transcript(transcript)
                or "cds_start"
                not in driver.data_providers[assembly]
                ._get_transcript(transcript)["genome_builds"][assembly.value]
                .keys()
                or "cds_end"
                not in driver.data_providers[assembly]
                ._get_transcript(transcript)["genome_builds"][assembly.value]
                .keys()
                or "exons"
                not in driver.data_providers[assembly]
                ._get_transcript(transcript)["genome_builds"][assembly.value]
                .keys()
            ):
                _logger.warning(
                    f"Skipping transcript {transcript} as it does not have all required data"
                )
                continue
            hgnc_id = f"HGNC:{driver.data_providers[assembly]._get_transcript(transcript)['hgnc']}"
            hgnc_to_transcripts.setdefault(hgnc_id, []).append(
                driver.data_providers[assembly]._get_transcript(transcript)
            )
        assembly_to_hgnc_to_transcripts[assembly] = hgnc_to_transcripts
    _logger.info("map built")
    yield


app = FastAPI(
    title="dotty",
    lifespan=lifespan,
)


class Spdi(pydantic.BaseModel):
    """SPDI representation of a variant."""

    #: Assembly name.
    assembly: str
    #: Reference sequence ID.
    contig: str
    #: 1-based position.
    pos: int
    #: Reference allele / deleted sequence.
    reference_deleted: str
    #: Alternate allele / inserted sequence.
    alternate_inserted: str


class Result(pydantic.BaseModel):
    """The result of the query."""

    #: The actual payload / SPDI representation of the variant.
    spdi: Spdi


class ExonAlignment(pydantic.BaseModel):
    """Alignment of an exon to an assembly."""

    #: Exon start in reference.
    ref_start: int
    #: Exon end in reference.
    ref_end: int
    #: Exon number.
    exon_no: int
    #: Exon start in transcript.
    tx_start: int
    #: Exon end in transcript.
    tx_end: int
    #: The gapped alignment description.
    alignment: str | None

    @staticmethod
    def _from_list(lst: list[typing.Any]) -> "ExonAlignment":
        """Create an ``ExonAlignment`` from a list."""
        return ExonAlignment(
            ref_start=lst[0],
            ref_end=lst[1],
            exon_no=lst[2],
            tx_start=lst[3],
            tx_end=lst[4],
            alignment=lst[5],
        )


class TanscriptAlignment(pydantic.BaseModel):
    """Alignment of a `Transcript` to an assembly."""

    #: Assembly of alignment.
    assembly: str
    #: Alignment contig.
    contig: str
    #: CDS start.
    cds_start: int
    #: CDS end.
    cds_end: int
    #: Exons, first two entries are start/end positions on the chromosome.
    exons: list[ExonAlignment]

    @staticmethod
    def _from_dict(assembly, dct: dict[str, typing.Any]) -> "TanscriptAlignment":
        """Create a ``TanscriptAlignment`` from a dictionary."""
        return TanscriptAlignment(
            assembly=assembly,
            contig=dct["contig"],
            cds_start=dct["cds_start"],
            cds_end=dct["cds_end"],
            exons=[ExonAlignment._from_list(lst) for lst in dct["exons"]],
        )


class Transcript(pydantic.BaseModel):
    """Transcript model."""

    #: Transcript ID.
    id: str
    #: Gene HGNC ID.
    hgnc_id: str
    #: Gene HGNC symbol.
    hgnc_symbol: str
    #: Alignments of the transcripts.
    alignments: list[TanscriptAlignment]

    @staticmethod
    def _from_dict(assembly: str, dct: dict[str, typing.Any]) -> "Transcript":
        """Create a ``Transcript`` from a dictionary."""
        return Transcript(
            id=dct["id"],
            hgnc_id=f"HGNC:{dct['hgnc']}",
            hgnc_symbol=dct["gene_name"],
            alignments=[TanscriptAlignment._from_dict(assembly, dct["genome_builds"][assembly])]
            if assembly in dct["genome_builds"]
            else [],
        )


class TranscriptResult(pydantic.BaseModel):
    """The result of the query for searching for transcripts."""

    #: The actual payload / list of transcripts.
    transcripts: list[Transcript]


@app.get("/api/v1/to-spdi", response_model=Result)
async def to_spdi(q: str, assembly: Assembly = Assembly.GRCH38) -> Result:
    """Resolve the given HGVS variant to SPDI representation."""
    try:
        parsed_var = driver.parser.parse(q)
    except hgvs.exceptions.HGVSParseError:
        raise HTTPException(status_code=400, detail="Invalid HGVS description")

    if parsed_var.type == "c":
        var_g = driver.assembly_mappers[assembly].c_to_g(parsed_var)
    elif parsed_var.type == "n":
        var_g = driver.assembly_mappers[assembly].n_to_g(parsed_var)
    elif parsed_var.type == "g":
        var_g = parsed_var
        if var_g.ac in contig_names[Assembly.GRCH37]:
            assembly = Assembly.GRCH37
    else:  # pragma: no cover
        raise HTTPException(status_code=400, detail="Invalid variant type")

    contig, pos, reference, alternative, type_ = driver.babelfishes[assembly].hgvs_to_vcf(var_g)

    return Result(
        spdi=Spdi(
            assembly=assembly.value,
            contig=contig,
            pos=pos,
            reference_deleted=reference,
            alternate_inserted=alternative,
        )
    )


@app.get("/api/v1/find-transcripts", response_model=TranscriptResult)
async def find_transcripts(hgnc_id: str, assembly: Assembly = Assembly.GRCH38) -> TranscriptResult:
    """Find transcripts for the given HGNC ID."""
    result = []
    transctipts = assembly_to_hgnc_to_transcripts[assembly].get(hgnc_id, [])
    if not transctipts:
        raise HTTPException(status_code=404, detail="No transcripts found")
    else:
        for t in transctipts:
            if (
                assembly.value not in t["genome_builds"]
                or "cds_start" not in t["genome_builds"][assembly.value]
                or "cds_end" not in t["genome_builds"][assembly.value]
                or "exons" not in t["genome_builds"][assembly.value]
            ):
                continue

            result.append(Transcript._from_dict(assembly.value, t))
        return TranscriptResult(transcripts=result)
