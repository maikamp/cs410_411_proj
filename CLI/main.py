import argparse

def initParser(): 
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
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
    


def main(): 

    parse = initParser()

if __name__ == "__main__":
    main()