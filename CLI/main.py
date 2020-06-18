
import argparse
from objects.user import User
from objects.member import Member

def readConfig(user, file): 
    print(len(file.readlines()))
    with open(user.config_path, "r") as f: 
        user.id = f.readlines()[0]
        user.access_level = f.readlines()[1]
        user.last_access_date = f.readlines()[2]
        user.last_access_time = f.readlines()[3]
      
def makeConfig(user): 
    try: 
        f = open(user.config_path)
        return f 
    except Exception as ex: 
        print(ex)

def checkConfig(user, file): 
    try: 
        file = open(user.config_path, "w+")
        return True 
    except Exception as ex: 
        print(ex)
        return False

def search(): 
    print("Search Coming Soon")

def signUp(guest): 
    print("sign Up Coming Soon")

def processRequest(request): 
    r = request.replace(" ", "")
    return r 

def gatherRequest(): 
    return input("Enter choice: ")

def infoMode(): 
    print ("")

def memberMode(): 
    member = Member() 

    while True: 
        member.printMemberMenu()
        if (member.checkStatus() is True): 
            break

def guestMode(): 
    guest = User() 

    while True: 
        guest.printUserMenu() 
        request = gatherRequest()
        process = processRequest(request)

        if (process == 'C' or process == 'c'): 
            break
        elif (process == 'A' or process == 'a'): 
            signUp(guest)
        elif (process == 'B' or process == 'b'): 
            search() 

logo = (''' 
                 _______       ____
               /         \       __}
              /           \    ____}
             /      _      \   
            /      / \      \ 
           /      /___\      \ 
          /       _____       \ 
         /      /       \      \ 
        /      /         \      \ 
       /_____ /           \ _____\ 
       
''')

def infoMode(): 
    print (logo)
    print ("    A Cubed - A3    ")
    print (" ------------------ ")

def initParser(): 
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description= logo + 'A3 Command line interface',
            epilog='For more help, type main.py -h')
    
    '''
    Specify different interface modes
    - Guests 
    - Members 
    - Info 
    '''
    mode_group = parser.add_mutually_exclusive_group(required=True)
    
    # Guest Mode 
    mode_group.add_argument('--g', help='Activate guest mode.',
                            action='store_true')
    
    # Member Mode
    mode_group.add_argument('--m', action='store_true',
                            help='Activate Member mode.')

    # Info Mode
    mode_group.add_argument('--i', action='store_true',
                            help='Display system information.')

    return parser 
    
def main(): 

    parser = initParser()
    args, unknown = parser.parse_known_args() 

    if args.g: 
        guestMode()
    if args.m:
        memberMode()
    if args.i: 
        infoMode() 

if __name__ == "__main__":
    main()