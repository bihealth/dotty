from hgvs.dataproviders.interface import Interface

class AbstractJSONDataProvider(Interface):
    pass

class LocalDataProvider(AbstractJSONDataProvider):
    pass

class JSONDataProvider(LocalDataProvider):
    pass
