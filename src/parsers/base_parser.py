class BaseParser():
    def __init__(self, name:str, domains:list):
        # """Sets domains supported by parser
        #     @param domains: Supported domains (list)
        # """
        if not isinstance(name, str):
            raise TypeError("name type should be str")
        self.name = name

        if not isinstance(domains, list):
            raise TypeError("domains type should be list")
        self.domains = domains
    
    def __str__(self):
        return f"{self.name}: {self.domains}"
    
    def __repr__(self):
        return self.__str__()
    
    async def search(self, query:str)->dict:
        raise(NotImplementedError(f'Implement search in {self.__class__.__name__}'))

    async def process_url(self, url:str)->list:
        raise(NotImplementedError(f'Implement process_url in {self.__class__.__name__}'))

    async def get_song(self, song_info:dict)->dict:
        raise(NotImplementedError(f'Implement get_song in {self.__class__.__name__}'))
