import logging

import pydantic
from fastapi import FastAPI

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="dotty",
)


class Result(pydantic.BaseModel):
    payload: str


@app.get("/", response_model=list[Result])
async def index() -> list[Result]:
    """Render the index.html page at the root URL"""
    return [Result(payload="foo")]
