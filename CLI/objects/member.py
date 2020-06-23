import string
from getpass import getpass 

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
    memberMenu()
        Prints a menu with member level abilities
    
    signIn()
        Initiates the sign in process

    signInMenu()
        Prints the available sign in options

     
    
    """ 

    def __init__(self):
        """ Initialize Member class variables """
        
        super(Member, self).__init__()

        # Elements that faculty members have but guests do not
        self.username = "" 
        self.email_address = "" 
        self.password = ""  
        self.last_access_date = 00000000
        self.last_access_time = 0000

        # Extra elements to help with OOP 
        self.config_path = "./user/config.txt" 
        self.options = ['Sign In', 'Search', 'Help', 'Quit']


    def setUsername(self, u): 
        self.username = u 

    def getUsername(self): 
        return self.username

    def configSignIn(self): 
        print()

    def rawSignIn(self): 
        try: 
            self.username = input("Enter your username: ")
            self.password = getpass()
        except Exception as ex: 
            print(ex)
        
    def signInMenu(self): 

        self.clearScreen()

        print("-------- A Cubed - Member Sign In ---------", end = '\n\n')
       
        print('A) Config')
        print('B) Raw Input')

        print("\n-------------------------------------------")

        request = self.gatherRequest()
        process = self.processRequest(request)

        if (process == 'A' or process == 'a'): 
            self.configSignIn()
        elif (process == 'B' or process == 'b'): 
            self.rawSignIn()  
        

    def signIn(self): 
        self.signInMenu() 

        
    def helpScreen(self):

        self.clearScreen()

        print("\n          ***************************    ")
        print(  "          *  Members can sign in,   *    ")
        print(  "          *  search public or       *    ")
        print(  "          *  permissed artifacts,   *    ")
        print(  "          *  upload artifacts, or   *    ")
        print(  "          *  update owned or allowed*    ")
        print(  "          *  artifacts.             *    ")
        print(  "          ***************************    ")

        input(  "                   Continue...         ")


    def memberMenu(self, logo): 

        self.clearScreen()

        print(logo)
       
        print("")
        print("-------- A Cubed - Member Mode ---------", end = '\n\n')
        print("\n        |*********************|    ")

        i = 0
        for o in self.options: 
            print("              " + chr(i + 97).upper() + " - " + str(o) )

            i += 1
        print("        |*********************|    ")


        print("\n----------------------------------------")

        request = self.gatherRequest()
        process = self.processRequest(request)

        if (process == 'A' or process == 'a'): 
            self.signIn()
        elif (process == 'B' or process == 'b'): 
            print() 
        elif (process == 'C' or process == 'c'): 
            self.quit = True 