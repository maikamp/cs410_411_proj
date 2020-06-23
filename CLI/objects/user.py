import string 
from os import system, name 
from time import sleep 


class User(): 
    """ 
    A class used to represent the local machine and it's user; guests and members alike 
    
    ...

    Attributes 
    ---------- 
    id : int
        a procedurally generated identification number 
        
    output_path : str  
        the path to the directory holding exports and reports 
    quit : bool 
        menu switch signifying quit/logout 
    options : list 
        a list of functions any user can user 

    Methods 
    ------- 
    clearScreen() 
        Clears the terminal for more a efficient UX

    userMenu()
        Prints a menu with guest level abilities

    gatherRequest() 
        Gathers user instructions in menu 

    processRequest()
        Processes input and issues commands 

    checkStatus()
        Return this.quit     

    helpScreen() 
        Prints a short description of class abilities
    
    """ 

    def __init__(self):
        """ Initialize User class variables """ 

        # Elements that all members have
        self.id = 0

        # Extra elements to help with OOP shared by all members 
        self.output_path = './user/outs/'
        self.quit = False 
        self.options = ['Sign Up', 'Search', 'Help', 'Quit']

    # Getters and setter functions 
    def setId(self, id: str): 
        self.id = id
    
    def setQuit(self, quit: bool): 
        self.quit = quit

    def getId(self): 
        return (self.id)

    def getQuit(self): 
        return (self.quit)
    
    def signUp(self): 
        print ("Sign Up")
    
    def search(self): 
        print("Search")

    def processRequest(self, request): 
        req = ord(request) - 97

        if (req == 0):
            self.signUp()
        if (req == 1): 
            self.search() 
        if (req == 2):
            self.helpScreen()
        if (req == 3): 
            self.setQuit(True)

    def gatherRequest(self): 
        r = (input("Enter choice: "))
        print ("")
        
        ret = r.replace(" ", "").strip()
        return (ret) 

    def helpScreen(self):

        self.clearScreen()

        print("\n          *********************    ")
        print(  "          *  Guests can either*    ")
        print(  "          *  create accounts, *    ")
        print(  "          *  search artifacts,*    ")
        print(  "          *  or  manipulate   *    ")
        print(  "          *  public artifacts.*    ")
        print(  "          *********************    ")

        input(  "               Continue...         ")

    def clearScreen(self):
        if name == 'nt': 
            _ = system('cls') 
        else: 
            _ = system('clear') 

    def userMenu(self, logo): 

        self.clearScreen()

        print(logo)
        print("--------- A Cubed - Guest Mode ---------", end = '\n\n')
        print("\n        |*********************|    ")

        i = 0
        for o in self.options: 
            print("              " + chr(i + 97).upper() + " - " + str(o) )

            i += 1
        print("        |*********************|    ")


        print("\n----------------------------------------")

        request = self.gatherRequest()
        self.processRequest(request)
        