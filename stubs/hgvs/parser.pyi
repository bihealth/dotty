from hgvs.sequencevariant import SequenceVariant

class Parser:
    def parse(self, v: str) -> SequenceVariant: ...
    def parse_hgvs_variant(self, v: str) -> SequenceVariant: ...
