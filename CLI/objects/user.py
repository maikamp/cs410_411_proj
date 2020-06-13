class User(): 
    """ 
    A class used to represent the local machine and it's user; guests and members alike 
    
    ...

    Attributes 
    ---------- 
    id : str
        a procedurally generated identification number 
    access_level : str 
        a value signifying users permission levels 
    
    output_path : str  
        the path to the directory holding exports and reports 

    Methods 
    ------- 
    
    """ 

    def __init__(self):
        """ Initialize class variables """ 

        # Elements that all members have
        self.id = ""

        # Extra elements to help with OOP shared by all members 
        self.output_path = './user/outs'

    # Getters and setter functions 
    def setId(self, id: str): 
        self.id = id

    def setAccessLevel(self, access_level: str): 
        self.access_level = access_level;

    def getId(self): 
        return (self.id)

    def getAccessLevel(self): 
        return (self.access_level)


    

    