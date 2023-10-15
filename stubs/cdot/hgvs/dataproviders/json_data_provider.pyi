import typing

from hgvs.dataproviders.interface import Interface

class AbstractJSONDataProvider(Interface):
    pass

class LocalDataProvider(AbstractJSONDataProvider):
    pass

class JSONDataProvider(LocalDataProvider):
    transcripts: dict[str, typing.Any]
    def _get_transcript(self, tx_id: str) -> dict[str, typing.Any]: ...
