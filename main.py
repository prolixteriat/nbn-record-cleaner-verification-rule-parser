'''
About  : NBN Record Cleaner rule processors main program file. 
         See main() function.
Author : Kevin Morley
Version: 1 (24-May-2023)
'''

# ------------------------------------------------------------------------------

import getopt
import logging
import sys
import traceback

from RuleController import RuleController   # KPM

# ------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, 
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s', 
            encoding = 'utf-8',
            handlers= [
                logging.FileHandler('./logs/debug.log', mode='w'), 
                logging.StreamHandler()
            ])
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
# Main program entry point. Instantiate controller object and call methods.

def main(argv):
    '''
    Params: argv (list) - command line arguments
    Return: N/A
    '''
     
    help = 'main.py --input <input path> --output <output path>'
    try:
        opts, args = getopt.getopt(argv,'hi:o:',['input=','output='])
    except getopt.GetoptError:
        print(f'Incorrect command line option: {argv}')
        print (f'Correct options are: "{help}"')
        sys.exit(2)
    
    # Process command line options
    folder = None
    for opt, arg in opts:
        if opt == '-h':
            print('help')
            sys.exit()
        elif opt in ('-i', '--input'):
            folder_in = arg
        elif opt in ('-o', '--output'):
            folder_out = arg
        else:
            print(f'Unknown option: {opt}')
            sys.exit(2)
    
    # Execute the processing
    log.info('='*50)
    try:
        rc = RuleController(folder_in, folder_out)
        rc.process()
    except Exception as ex:
        log.error(ex)
        traceback.print_exception(*sys.exc_info())
    
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv[1:])

# ------------------------------------------------------------------------------
       
'''
End
'''