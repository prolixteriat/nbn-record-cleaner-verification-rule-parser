'''
About  : Write results to file.
Author : Kevin Morley
Version: 2 (14-Jun-2023)
'''

# ------------------------------------------------------------------------------

import csv
import logging
import pandas as pd
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
        self.consol = {}    # single, consolidated ruleset dictionary

    # --------------------------------------------------------------------------
    # Return the consol rule record corresponding to a given taxon_key.

    def get_consol_record(self, taxon_key):
        # Check whether rule record exists already. If not, create a new one.
        if taxon_key in self.consol:
            rv = self.consol[taxon_key]
        else:
            rv = {
                'id': len(self.consol) + 1,
                'ruleset': '',
                'organisation': '',
                'message': '',
                'information': '',
                'difficulty_key': '',
                'start_date': '',
                'end_date': '',
                'stage': '',
                '10km_GB': '',
                '10km_Ireland': '',
                '10km_CI': ''
            }
            self.consol[taxon_key] = rv
        
        return rv

    # --------------------------------------------------------------------------
    # Populate the consol dict.

    def populate_consol(self):
        # -----------------------------------------------
        def populate_common(record, ruleset, rule):
            record['ruleset'] = ruleset
            record['organisation'] = rule['organisation']
            record['message'] = rule['message']
        # -----------------------------------------------            
        log.info('Creating consolidated ruleset...')
        self.consol.clear()
        # additionals
        for rule in self.parser.additionals:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'additional', rule)
            record['information'] = rule['information']
        # difficulties
        for rule in self.parser.difficulties:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'difficulty', rule)
            record['difficulty_key'] = rule['difficulty_key']
        # flightperiods
        for rule in self.parser.flights:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'flightperiod', rule)
            record['start_date'] = rule['start_date']            
            record['end_date'] = rule['end_date']            
            record['stage'] = rule['stage']            
        # periods
        for rule in self.parser.periods:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'period', rule)
            record['start_date'] = rule['start_date']            
            record['end_date'] = rule['end_date']            
        # ranges
        for rule in self.parser.ranges:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'range', rule)
            record['10km_GB'] = rule['10km_GB']            
            record['10km_Ireland'] = rule['10km_Ireland']            
            record['10km_CI'] = rule['10km_CI'] 
        # regions
        for rule in self.parser.regions:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'region', rule)
            record['10km_GB'] = rule['10km_GB']            
            record['10km_Ireland'] = rule['10km_Ireland']            
            record['10km_CI'] = rule['10km_CI'] 
        # seasonals
        for rule in self.parser.seasonals:
            record = self.get_consol_record(rule['taxon_key'])
            populate_common(record, 'seasonal', rule)
            record['start_date'] = rule['start_date']            
            record['end_date'] = rule['end_date']            
            record['stage'] = rule['stage']                                                 

    # --------------------------------------------------------------------------
    # Write results to output channels.

    def write(self):
        '''
        Params: N/A 
        Return: N/A
        '''
        log.info('-'*50)
        self.populate_consol()
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

        self.write_file('species_nbn.csv', self.parser.species,
            ['taxon_key', 'preferred_tvk', 'name', 'authority', 'group', 
             'name_type', 'well_formed', 'msg_id'])

        self.write_consol('all_rules.csv')

    # ----------------------------------------------------------------------
    # Write the consol dict to  CSV file

    def write_consol(self, fn_txt):
        '''
        Params: fn_txt (string) - name of file to write
        Return: N/A
        '''        
        fn = os.path.join(self.folder_output, fn_txt)
        log.debug(f'Writing file: {fn}')
        df = pd.DataFrame(self.consol)
        dft = df.transpose()
        dft.index.name = 'taxon_key'
        dft.to_csv(fn, encoding='utf-8', 
                    quoting=csv.QUOTE_NONNUMERIC)

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