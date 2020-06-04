
from objects.user import User

class Member(): 
    def __init__(self, User):
        
        # Elements that faculty members have but guests do not
        self.username = "" 
        self.email_address = "" 
        self.password = ""  
        self.last_access_date = 00000000
        self.last_access_time = 0000

        # Extra elements to help with OOP 
        self.config_path = "./user/config.txt" 