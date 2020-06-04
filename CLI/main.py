
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

def quit(): 
    pass

def signIn(member): 
    print("Sign in")
def signUp(guest): 
    print("sign up")

def processRequest(guest, request): 
    if (request == "A"): 
        return "A"
    elif (request == "B"): 
        return "B"
    elif (request == "C"): 
        return "C"

def gatherRequest(): 
    return input("Choose the desired action: ")

def memberMenu(): 
    print("")
    print("-------- A Cubed - Member Mode --------")
    print("A)   Sign in")
    print("B)   Search")
    print("C)   Quit")
    print("---------------------------------------")

def guestMenu(): 
    print("")
    print("-------- A Cubed - Guest Mode --------")
    print("A)   Sign up")
    print("B)   Search")
    print("C)   Quit")
    print("--------------------------------------")
    
def memberMode(): 
    member = User() 

    while True: 
        memberMenu()

        request = gatherRequest()
        process = processRequest(member, request)

        if (process == 'C'): 
            break 
        elif (process == 'A'): 
            signIn(member)

def guestMode(): 
    guest = User() 

    while True: 
        guestMenu() 
        request = gatherRequest()
        process = processRequest(guest, request)

        if (process == 'C'): 
            break 
        elif (process == 'A'): 
            signUp(guest)


def initParser(): 
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='A3 Command line interface',
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
                            help='Activate Member mode')

    return parser 
    


def main(): 

    parser = initParser()
    args, unknown = parser.parse_known_args() 

    if args.g: 
        guestMode()
    if args.m:
        memberMode()

if __name__ == "__main__":
    main()