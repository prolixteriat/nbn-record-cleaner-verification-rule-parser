'''
About  : Implements the RuleController class which orchestrates the data 
         input, parsing and output processes.
Author : Kevin Morley
Version: 1 (24-May-2023)
'''

# ------------------------------------------------------------------------------

import logging
import os
import progress.spinner as spinner
import threading
import time

from RuleParser import RuleParser           # KPM
from RuleOutput import RuleOutput           # KPM
from utils import get_folders, ElapsedTime  # KPM

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Class which orchestrates the data input, parsing and output processes.

class RuleController:

    # List of top-level rule folders to ignore
    SKIP_FOLDERS = ['National Biodiversity Network Trust', 
                    'Personal', 
                    'SystemRules'] 

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self, folder_in, folder_out='..\Results'):
        '''
        Params: folder_in (string) - path to NBN rule folder
                folder_out (string) - path to output folder
        Return: N/A
        '''
        self.folder_in = folder_in
        self.folder_out = folder_out
        self.parser = RuleParser()
        self.output = RuleOutput(self.parser, folder_out)

    # --------------------------------------------------------------------------
    # Process all files in the input folder.

    def process(self):
        '''
        Params: N/A
        Return: N/A
        '''
        et = ElapsedTime()
        ok = True
        # Read species list
        log.info('-'*50)
        fn = os.path.join(self.folder_in, 'MasterSpeciesList.txt')
        if self.parser.read_specieslist(fn) == False:
            ok = False
        # Read rules
        folders = get_folders(self.folder_in)
        for ix, folder in enumerate(folders):
            log.info('-'*50)
            log.info(f'Processing folder {ix+1} of {len(folders)}')
            f = os.path.split(folder)[1]
            if f in self.SKIP_FOLDERS:
                log.info(f'Skipping folder: {f}')            
            else:
                if self.parser.read_rules(folder) == False:
                    ok = False
                    log.warning('*** Error occurred while processing files')

        # Output results on new thread to allow spinner to work
        thread = threading.Thread(target=self.output.write)
        thread.start()
        with spinner.Spinner('Writing results...') as spin:
            while thread.is_alive():
                spin.next()
                time.sleep(0.1)
        thread.join()            
        
        log.info('='*50)
        et.log_elapsed_time()
        if self.parser.skips > 0:
            log.info(f'Note that {self.parser.skips} files contain sections '
                     'that have been skipped. See the "skip.log" file for '
                     'further details.')
        if ok:
            log.info('Finished. No errors occurred.')
        else:
            log.info('Finished. One or more errors occurred.')
        
# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
# Run module-specific tests.

def do_test():
    '''
    Params: N/A
    Return: (bool) Returns True if tests succesful, else False
    '''
    log.info('-'*50)
    log.info('Beginning test [RuleController.py]...')
    rv = True
    log.info(f'Finished test. Test passed: {rv}')
    return rv

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s')
    do_test()

# ------------------------------------------------------------------------------
       
'''
End
'''