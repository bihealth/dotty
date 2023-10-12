import logging
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

#: Contig names per assembly.
contig_names: dict[Assembly, set[str]] = {
    assembly: set(
        sr["refseq_ac"] for sr in bioutils.assemblies.get_assembly(assembly.value)["sequences"]
    )
    for assembly in Assembly
}


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    global driver
    _ = app
    driver = Driver(cdot_dir=settings.DATA_DIR)
    driver.load()
    _logger.info("driver loaded")
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


class Transcript(pydantic.BaseModel):
    """Transcript model."""

    #: Transcript refseq ID.
    transcript_id: str
    #: Transcript version.
    transcript_version: str
    #: Gene hgnc ID.
    gene_id: str
    #: Gene name.
    gene_name: str
    #: Contig.
    contig: str
    #: CDS start.
    cds_start: int
    #: CDS end.
    cds_end: int
    #: Exons.
    exons: list[dict[str, int]]


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
async def find_transcripts(
    refseq_ids: str, assembly: Assembly = Assembly.GRCH38
) -> TranscriptResult:
    """Find transcripts for the given RefSeq ID in given Assembly."""
    transcripts_result = []
    transcripts_list = [
        transcript
        for transcript in driver.data_providers[assembly].transcripts.keys()
        if transcript.split(".")[0] in refseq_ids.split(",")
    ]

    for transcript in transcripts_list:
        transcript_info = driver.data_providers[assembly]._get_transcript(transcript)
        transcripts_result.append(
            Transcript(
                transcript_id=transcript.split(".")[0],
                transcript_version=transcript.split(".")[1],
                gene_id="HGNC:" + transcript_info["hgnc"],
                gene_name=transcript_info["gene_name"],
                contig=transcript_info["genome_builds"][assembly.value]["contig"],
                cds_start=transcript_info["genome_builds"][assembly.value]["cds_start"],
                cds_end=transcript_info["genome_builds"][assembly.value]["cds_end"],
                exons=[
                    {"start": min(exon[0], exon[1]), "end": max(exon[0], exon[1])}
                    for exon in transcript_info["genome_builds"][assembly.value]["exons"]
                ],
            )
        )
    return TranscriptResult(transcripts=transcripts_result)
