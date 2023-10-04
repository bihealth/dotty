class HGVSError(Exception):
    pass

class HGVSDataNotAvailableError(HGVSError):
    pass

class HGVSParseError(HGVSError):
    pass
