'''
About  : Write results to file.
Author : Kevin Morley
Version: 1 (24-May-2023)
'''

# ------------------------------------------------------------------------------

import csv
import logging
import os

from RuleParser import RuleParser

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Class which orchestrates the output of processed rule data.

class RuleOutput:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self, parser, folder_output):
        '''
        Params: parser (RuleParser) - object containing processed rule data
                folder_output (string) - path to output folder
        Return: N/A
        '''
        self.folder_output = os.path.abspath(folder_output)
        self.parser = parser

    # --------------------------------------------------------------------------
    # Write results to output channels.

    def write(self):
        '''
        Params: N/A 
        Return: N/A
        '''
        log.info('-'*50)
        log.info(f'Writing files to folder: {self.folder_output}')
        self.write_file('additionals.csv', self.parser.additionals,
            ['taxon_key', 'organisation', 'message', 'information'])

        self.write_file('difficulties.csv', self.parser.difficulties,
            ['taxon_key', 'organisation', 'message', 'difficulty_key'])
                
        self.write_file('flightperiods.csv', self.parser.flights,
            ['taxon_key', 'organisation', 'message', 'start_date', 'end_date',
             'stage'])

        self.write_file('periods.csv', self.parser.periods,
            ['taxon_key', 'organisation', 'message', 'start_date', 'end_date'])
        
        self.write_file('ranges.csv', self.parser.ranges,
            ['taxon_key', 'organisation', 'message', '10km_GB', '10km_Ireland', 
             '10km_CI'])
        
        self.write_file('regions.csv', self.parser.regions,
            ['taxon_key', 'organisation', 'message', '10km_GB', '10km_Ireland', 
             '10km_CI'])
        
        self.write_file('seasonals.csv', self.parser.seasonals,
            ['taxon_key', 'organisation', 'message', 'start_date', 'end_date', 
             'stage'])

        self.write_file('species.csv', self.parser.species,
            ['taxon_key', 'preferred_tvk', 'name', 'authority', 'group', 
             'name_type', 'well_formed', 'msg_id'])

    # ----------------------------------------------------------------------
    # Write a single CSV file

    def write_file(self, fn_txt, data, fields):
        '''
        Params: fn_txt (string) - name of file to write
                data (list) - data to be written
                fields (list) - column headers
        Return: N/A
        '''        
        fn = os.path.join(self.folder_output, fn_txt)
        log.debug(f'Writing file: {fn}')
        with open(fn, 'w', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, lineterminator='\r',
                                    quoting=csv.QUOTE_NONNUMERIC,
                                    fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)   

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
    log.info('Beginning test [RuleOutput.py]...')
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