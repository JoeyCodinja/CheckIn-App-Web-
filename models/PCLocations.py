from Database import Database

from pprint import pprint

class PCLocations():
    Humanities_Education = 'HUME'
    Mona_Information_Tech = 'MITS'
    Medical_Science = 'MEDS'
    Social_Sciences = 'SOCS'
    Science_Technology = 'SCIT'
    Unregistered = 'UDEF'
    
    valid_locations = {Humanities_Education: "Faculty of Humanities and Education" ,
                       Mona_Information_Tech: "Mona Information Technology Services",
                       Medical_Science: "Faculty of Medical Sciences",
                       Social_Sciences: "Faculty of Social Sciences",
                       Science_Technology: "Faculty of Science & Technology"}
    
    def __init__(self, uuid, location):
        self.uuid = uuid
        location_unregistered = location != PCLocations.Unregistered
        valid_location = location not in PCLocations.valid_locations
        
        if valid_location and location_unregistered: 
            raise  ValueError('This location isn\'t valid')
        self.location = location
        
    def get_identifier(self):
        return self.uuid
    
    def get_assigned_loc(self):
        return self.location 
        
    @staticmethod
    def from_db(database, key=None):
        pclocations = database.query('/pc_locations')
        
        pprint("PC Locations: " + str(pclocations))
        
        if pclocations is not None:        
            if key is None:
                listing = []
                for location in pclocations:
                    for uuid in pclocations[location]:
                        pprint("location: " + str(location))
                        listing.append(PCLocations(uuid, location))
                return listing
            else: 
                for location in pclocations:
                    for uuid in pclocations[location]:
                        if uuid == key:
                            return location
        else: 
            pclocations = []
            return pclocations
            
                    
                