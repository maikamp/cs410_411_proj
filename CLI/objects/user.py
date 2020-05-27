class User(): 
    """ 
    Used to represent the local machine and it's userl; guests and members alike 
    
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

        # Elements that faculty members have but guests do not
        this.id = "";
        this.access_level = ""; 

        # Extra elements to help with OOP 
        this.output_path = './user/outs';


    # Getters and setter functions 
    def setId(self, id: str): 
        this.id = id; 

    def setAccessLevel(self, access_level: str): 
        this.access_level = access_level; 

    def getId(self): 
        return (self.id); 

    def getAccessLevel(self): 
        return (self.access_level); 

    