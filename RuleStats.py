'''
About  : Generate statistics relating to rule coverage. See main() entry point.
         This module is not part of the main script. Defaults to using the NHM
         species list but can use other formats by editing the SPEC_COL values.
Author : Kevin Morley
Version: 1 (14-Jun-2023)
'''

# ------------------------------------------------------------------------------

import csv
import logging
import pandas as pd
import progress.spinner as spinner
import threading
import time

# ------------------------------------------------------------------------------
# Write results to both screen and file 'stats.log'.

logging.basicConfig(level=logging.INFO, 
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s', 
            encoding = 'utf-8',
            handlers= [
                logging.FileHandler('./logs/stats.log', mode='w'), 
                logging.StreamHandler()
            ])
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Default file names for input/output
DEFAULT_FN_OUTPUT = '../Results/stats.csv'          # output file
DEFAULT_FN_SPECIES = '../Results/species_nhm.csv'   # input species file
DEFAULT_FN_RULES = '../Results/all_rules.csv'       # input rules file
# Column indices for species file
SPEC_COL_TVK = 2            # taxon key
SPEC_COL_RANK = 7           # rank
SPEC_COL_TVK_PREF = 16      # preferred taxon key
# Column indices for all_rules file
RUL_COL_TVK = 1             # taxon key
RUL_COL_RULESET = 2         # ruleset
ROL_COL_ORG = 3             # org

# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------
# Class which calculates and outputs stats relating to NBN rule coverage.

class RuleStats:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self, fn_species=DEFAULT_FN_SPECIES, fn_rules=DEFAULT_FN_RULES,
                    fn_output=DEFAULT_FN_OUTPUT):
        '''
        Params: fn_species (string) - species filename
                fn_rules (string) - rules filename
                fn_output (string) - output results file
        Return: N/A
        '''
        self.fn_species = fn_species
        self.fn_rules = fn_rules
        self.fn_output = fn_output
        self.rules = {}         # dict of rules read from CSV
        self.species = {}       # dict of species read from CSV
        
    # --------------------------------------------------------------------------
    # Analyse the data to produce the stats

    def analyse(self):
        '''
        Params: N/A
        Return: N/A
        '''
        log.info('Analysing species list...')
        # Calculate rule totals for each species
        for taxon in self.species:
            if taxon in self.rules:
                spec = self.species[taxon]
                spec['rules_total'] += len(self.rules[taxon])
                spec['rules_own'] += len(self.rules[taxon])
                # count types of rule
                for rule in self.rules[taxon]:
                    if rule[0] not in spec:
                        log.error(f'Unknown ruleset "{rule[0]}" for '
                                  f'taxon key {taxon}')
                        continue
                    spec[rule[0]] += 1
 
        # Add preferred taxon counts to totals
        for taxon in self.species:
            spec = self.species[taxon]
            if spec['taxon_key_preferred'] != taxon:
                if spec['taxon_key_preferred'] not in self.species:
                    log.error(f'Unknown taxon_key_preferred '
                       f'({spec["taxon_key_preferred"]}) for taxon key {taxon}')
                    continue
                
                spec_pref = self.species[spec['taxon_key_preferred']]
                spec_pref['rules_total'] += spec['rules_own']
                spec_pref['rules_preferred'] += spec['rules_own']

        # Initialise totals
        n_pref = 0          # no. of preferred taxons with rules
        n_nonpref = 0       # no. of non-preferred taxons with rules
        n_rules = 0         # total no. of rules
        n_orphan_rule = 0   # no. of rules without a matching species 
        # count of rule types
        n_types = {
            'additional': 0,
            'difficulty': 0,
            'flightperiod': 0,
            'period': 0,
            'range': 0,
            'region': 0,
            'seasonal': 0
        }
        # Calculate totals      
        for taxon_key in self.rules:
            for rule in self.rules[taxon_key]:
                n_rules += 1
                n_types[rule[0]] += 1
            
            if taxon_key not in self.species:
                log.info(f'Orphaned rule for taxon key {taxon_key}')
                n_orphan_rule += 1
                continue
            # Calculate no. of rules which apply to preferred taxons
            spec = self.species[taxon_key]
            if spec['taxon_key_preferred'] == taxon_key:
                n_pref += 1
            else:
                n_nonpref += 1
        
        # Output summary stats
        log.info('-'*50)
        log.info(f'No. of taxons in species file         : {len(self.species):,}')
        log.info(f'No. of rules                          : {n_rules:,}')
        log.info(f'No. of taxons with rules              : {len(self.rules):,}')
        log.info(f'No. of orphaned rules without taxons  : {n_orphan_rule:,}')
        log.info(f'No. of preferred taxons with rules    : {n_nonpref:,}')
        log.info(f'No. of non-preferred taxons with rules: {n_pref:,}')
        log.info(f'No. of [additional] rules             : {n_types["additional"]:,}')
        log.info(f'No. of [difficulty] rules             : {n_types["difficulty"]:,}')
        log.info(f'No. of [flightperiod] rules           : {n_types["flightperiod"]:,}')
        log.info(f'No. of [period] rules                 : {n_types["period"]:,}')
        log.info(f'No. of [range] rules                  : {n_types["range"]:,}')
        log.info(f'No. of [region] rules                 : {n_types["region"]:,}')
        log.info(f'No. of [seasonal] rules               : {n_types["seasonal"]:,}')
        
    # --------------------------------------------------------------------------
    # Process the data and produce the stats.

    def process(self):
        '''
        Params: N/A
        Return: N/A
        '''
        self.read_files()
        self.analyse()
        # Output results on new thread to allow spinner to work
        thread = threading.Thread(target=self.write_file)
        thread.start()
        with spinner.Spinner('Writing results...') as spin:
            while thread.is_alive():
                spin.next()
                time.sleep(0.1)
        thread.join()            
    
    # --------------------------------------------------------------------------
    # Read CSV files and populate rules and species dicts.

    def read_files(self):
        '''
        Params: N/A
        Return: N/A
        '''
        self.rules.clear()
        self.species.clear()
        log.info(f'Reading rules file: {self.fn_rules}')

        with open(self.fn_rules, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                taxon_key = row[RUL_COL_TVK].upper()
                ruleset = row[RUL_COL_RULESET]
                org = row[ROL_COL_ORG]
                self.rules.setdefault(taxon_key, []).append([ruleset, org])

        log.info(f'Reading species file: {self.fn_species}')
        with open(self.fn_species, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                taxon_key = row[SPEC_COL_TVK].upper()
                rank = row[SPEC_COL_RANK]
                taxon_key_preferred = row[SPEC_COL_TVK_PREF].upper()
                self.species[taxon_key] = {
                    'taxon_key_preferred': taxon_key_preferred,
                    'rank': rank,
                    'rules_total': 0,
                    'rules_own': 0,
                    'rules_preferred': 0,
                    'additional': 0,
                    'difficulty': 0,
                    'flightperiod': 0,
                    'period': 0,
                    'range': 0,
                    'region': 0,
                    'seasonal': 0
                }

    # --------------------------------------------------------------------------
    # Write results to CSV.

    def write_file(self):
        '''
        Params: N/A
        Return: N/A
        '''
        fn = self.fn_output
        log.info('-'*50)
        log.info(f'Writing file: {fn}')
        df = pd.DataFrame(self.species)
        dft = df.transpose()
        dft.index.name = 'taxon_key'
        dft.to_csv(fn, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

# ------------------------------------------------------------------------------
# Script entry point
# ------------------------------------------------------------------------------

def main():
    '''
    Params: N/A
    Return: N/A
    '''
    log.info('='*50)
    log.info('Beginning generation of statistics...')
    rs = RuleStats()
    rs.process()
    log.info(f'Finished.')

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# ------------------------------------------------------------------------------
       
'''
End
'''