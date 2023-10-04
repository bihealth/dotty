from hgvs.dataproviders.interface import Interface
from hgvs.posedit import PosEdit
from hgvs.sequencevariant import SequenceVariant

def _as_interbase(posedit: PosEdit) -> tuple[int, int]: ...

class Babelfish:
    ac_to_chr_name_map: dict[str, str]
    def __init__(self, hdp: Interface, assembly_name: str): ...
    def hgvs_to_vcf(self, var_g: SequenceVariant) -> tuple[str, int, str, str, str]: ...
