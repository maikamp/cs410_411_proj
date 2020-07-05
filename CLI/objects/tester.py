from .member import Member

class Tester(Member):

    def __init__(self):
        super(Tester, self).__init__()

    def helpScreen(self):

        self.clearScreen()

        print("\n          *******************************    ")
        print(  "          *  Testers can sign in, search*    ")
        print(  "          *  public or permissed        *    ")
        print(  "          *  artifacts, upload artifacts*    ")
        print(  "          *  update owned or allowed    *    ")
        print(  "          *  artifacts, and issue test  *    ")
        print(  "          *  commands.                  *    ")
        print(  "          *******************************    ")

        input(  "                   Continue...         ")


    def memberMenu(self, logo): 

        self.clearScreen()

        print(logo)
       
        print("")
        print("-------- A Cubed - Tester  Mode ---------", end = '\n\n')
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