'''
About  : Utility functions.
Author : Kevin Morley
Version: 1 (24-May-2023)
'''

# ------------------------------------------------------------------------------

import logging
import os
import time

from collections import OrderedDict

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Return a list of files within a parent folder.

def get_files(folder_parent):
    '''
    Params: folder_parent (string)
    Return: (list)
    '''
    files = []
    for file in os.listdir(folder_parent):
        f = os.path.join(folder_parent, file)
        if os.path.isfile(f):
            files.append(f)
        else:
            pass
            # log.debug(f'Skipping non-file: {f}')

    return files

# --------------------------------------------------------------------------
# Return a list of folders within a parent folder.

def get_folders(folder_parent):
    '''
    Params: folder_parent (string)
    Return: (list)
    '''
    folders = []
    for folder in os.listdir(folder_parent):
        f = os.path.join(folder_parent, folder)
        if os.path.isdir(f):
            folders.append(f)
        else:
            pass
            # log.debug(f'Skipping non-folder: {f}')

    return folders

# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------
# Class which tracks and logs elapsed time

class ElapsedTime:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self):
        '''
        Params: N/A
        Return: N/A
        '''
        self.start = None
        self.reset()
        
    # --------------------------------------------------------------------------
    # Write elapsed time to log.

    def log_elapsed_time(self):
        '''
        Params: N/A
        Return: N/A
        '''
        secs = time.perf_counter() - self.start
        log.info(f'Elapsed time: {(secs/60):,.1f} mins /  {int(secs):,} seconds')
    
    # --------------------------------------------------------------------------
    # Reset timer.

    def reset(self):
        '''
        Params: folder (string) - path to folder containing files to parse
        Return: (list of strings) - filenames to be parsed
        '''
        log.info('Timer start')
        self.start = time.perf_counter()

# ------------------------------------------------------------------------------
# Used by ConfigParser to allow keys with duplicate values

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)

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
    log.info('Beginning test [utils.py]...')
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