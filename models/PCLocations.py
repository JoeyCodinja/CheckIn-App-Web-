from Database import Database

class PCLocations():
    Humanities_Education = 'HUME'
    Mona_Information_Tech = 'MITS'
    Medical_Science = 'MEDS'
    Social_Sciences = 'SOCS'
    Science_Technology = 'SCIT'
    Unregistered = 'UREG'
    
    valid_locations = [Humanities_Education,
                       Mona_Information_Tech,
                       Medical_Science,
                       Social_Sciences,
                       Science_Technology]
    
    def __init__(self, uuid, location):
        self.uuid = uuid
        if location not in PCLocations.valid_locations: 
            raise  ValueError('This location isn\'t valid')
        self.location = location
        
    def get_identifier(self):
        return self.uuid
    
    def get_assigned_loc(self):
        return self.location 
        
    @staticmethod
    def from_db(database, key=None):
        pclocations = database.query('/pc_locations')
        
        if pclocations is not None:        
            if key is None:
                listing = []
                for location in pclocations:
                    for uuid in pclocations[location]:
                        listing.append(PCLocations(location, uuid))
                return listing
            else: 
                for location in pclocations:
                    for uuid in pclocations[location]:
                        if uuid == key:
                            return location
        else: 
            pclocations = []
            return pclocations
            
                    
                