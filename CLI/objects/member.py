import string
from .user import User

class Member(User): 
    """ 
    A class used to represent an authenticated user, or member    
    
    ...

    Attributes 
    ---------- 
    username : str
        a unique identifier attached to a members account, used for authentication purposes  
    email_address : str 
        the users email address, used for authentication purposes  
    password : str 
        the users password, used for authentication purposes 
    last_access_date : int 
        a formatted integer value used to represent the members last access date
    last_access_time : int 
        a formatted integer value used to represent the members last access time
        
    config_path : str  
        the path to the members config file; which holds authentication and access data 

    Methods 
    ------- 
    printMemberMenu()
        Prints
    
    """ 

    def __init__(self, *args):
        
        super(Member, self).__init__()

        # Elements that faculty members have but guests do not
        self.username = "" 
        self.email_address = "" 
        self.password = ""  
        self.last_access_date = 00000000
        self.last_access_time = 0000

        # Extra elements to help with OOP 
        self.config_path = "./user/config.txt" 

    def printMemberMenu(self): 
        LETTERS = {letter: str(index) for index, letter in enumerate(string.ascii_lowercase, start=1)}

        print("")
        print("-------- A Cubed - Member Mode ---------", end = '\n\n')
        
        i = 0
        for o in self.options: 
           
            print (chr(i + 97).upper() + ")", end=" ")
            print (o)
            i += 1

        print("\n--------------------------------------")