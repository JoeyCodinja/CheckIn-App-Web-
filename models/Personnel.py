import abc 

class Personnel(object):
    def __init__(self, name, p_id, last_state=None):
        self.__name = name
        self.__p_id = p_id
        self.last_state = last_state or 0 
        
    def getPassId(self):
        return self.__p_id
        
    def getName(self):
        return self.__name
    
    @staticmethod
    @abc.abstractmethod
    def is_an(self):
        return
    
    @staticmethod
    @abc.abstractmethod
    def from_db():
        # Should be implemented by each sub class
        return
    
        
    