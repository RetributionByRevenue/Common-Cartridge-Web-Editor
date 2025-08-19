class UserState:
    def __init__(self, username: str):
        self._username = username
        self._message = "Ready"
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def message(self) -> str:
        return self._message
    
    @message.setter
    def message(self, value: str):
        self._message = value


