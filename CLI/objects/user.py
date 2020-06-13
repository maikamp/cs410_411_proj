import string 

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
    options : list 
        a list of functions any user can user 

    Methods 
    ------- 
    printUserMenu()
        Prints
    
    """ 

    def __init__(self):
        """ Initialize class variables """ 

        # Elements that all members have
        self.id = 0

        # Extra elements to help with OOP shared by all members 
        self.output_path = './user/outs/'
        self.options = ['Sign In', 'Search', 'Quit']

    # Getters and setter functions 
    def setId(self, id: str): 
        self.id = id

    def setAccessLevel(self, access_level: str): 
        self.access_level = access_level;

    def getId(self): 
        return (self.id)

    def getAccessLevel(self): 
        return (self.access_level)

    def printUserMenu(self): 
        LETTERS = {letter: str(index) for index, letter in enumerate(string.ascii_lowercase, start=1)}

        print("")
        print("-------- A Cubed - Guest Mode --------", end = '\n\n')
        
        i = 0
        for o in self.options: 
           
            print (chr(i + 97).upper() + ")", end=" ")
            print (o)
            i += 1

        print("\n--------------------------------------")
    
        

        