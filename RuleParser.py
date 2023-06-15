'''
About  : Implements the RuleParser class which performs the data input and
         parsing processes for a single organisation rule set.
Author : Kevin Morley
Verion : 2 (15-Jun-2023)
'''

# ------------------------------------------------------------------------------

import logging
import os

from configparser import ConfigParser
from glob import glob
from progress.bar import Bar
from utils import get_files, get_folders, MultiOrderedDict      # KPM

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)
skip_log = logging.getLogger('skip')
skip_log.propagate = False
skip_log.addHandler(logging.FileHandler('./logs/skip.log', mode='w'))

# ------------------------------------------------------------------------------
# Class which orchestrates the data input, parsing and output processes.

class RuleParser:

    ERROR = '<ERROR>'  # Error flag

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self):
        '''
        Params: N/A
        Return: N/A
        '''
        # Initialise lists used to contain processed rules
        self.additionals = []
        self.difficulties = []
        self.flights = []
        self.periods = []
        self.ranges = []
        self.regions = []
        self.seasonals = []
        self.species = []

        self.skips = 0

    # --------------------------------------------------------------------------
    # Check whether any sections will not not processed for a given ruleset.

    def check_sections(this, config, file, sections):
        '''
        Params: config (ConfigParser) - object containing ruleset
                file (string) - path to file containing rule
                sections (list) - list of sections which will be processed
        Return: N/A
        '''
        skip_sections = []
        for s in config.sections():
            if s not in sections:
                this.skips += 1
                skip_sections.append(s)

        if len(skip_sections) > 0:
            skipped = '; '.join(skip_sections)
            skip_log.info(f'[{skipped}] - {file}')

    # --------------------------------------------------------------------------
    # Returns a configured ConfigParser object. Varies to account for the 
    # vagueries of the NBN rule file structures.

    def get_configparser(self, allow_duplicates=False):
        '''
        Params: allow_duplicates (bool) - allow duplicate keys if True
        Return: (ConfigParser) - object used to read rule files
        '''
        if allow_duplicates:
            rv = ConfigParser(strict=False, dict_type=MultiOrderedDict)
        else:
            rv = ConfigParser(strict=False, allow_no_value=True, 
                              delimiters=('=', ','))

        return rv
    
    # --------------------------------------------------------------------------
    # Process 'additional' rules within a single folder.

    def process_additional(self, org, folder):
        '''
        Params: org (string) - name of organisation
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered 
        '''
        rv = True
        files = get_files(folder)
        if len(files) == 0:
            log.warning(f'No files found in folder "{folder}"')
            return False
        
        with Bar('Processing additional rules...', max=len(files)) as bar:
            for f in files:
                bar.next()
                config = self.get_configparser()
                config.read(f)
                sections = ['EndMetadata', 'Metadata', 'INI', 'Data']
                self.check_sections(config, f, sections)
                # [Metadata]
                if config.has_section('Metadata'):
                    m_data = config['Metadata']
                    tt = m_data.get('TestType', self.ERROR)
                    if tt != 'AncillarySpecies':
                        log.error(f'Unknown TestType in file "{f}"')
                        rv = False
                    error_msg = m_data.get('ErrorMsg', self.ERROR)
                    if error_msg == self.ERROR:
                        log.error(f'No ErrorMsg in additional file "{f}"')
                        rv = False
                else:
                    log.error(f'File "{f}" does not contain [Metadata]')
                    rv = False
                # [INI]
                if config.has_section('INI'):
                    i_data = config['INI']
                    # [Data]
                    if config.has_section('Data'):
                        for k, v in config.items('Data'):
                            additional = {
                                    'taxon_key': k,
                                    'organisation': org,
                                    'message': error_msg,
                                    'information': i_data.get(v, self.ERROR)}
                            self.additionals.append(additional)
                    else:
                        log.error(f'File "{f}" does not contain [Data]')
                        rv = False

                else:
                    log.error(f'File "{f}" does not contain [INI]')
                    rv = False
                
                del config

        return rv
    
    # --------------------------------------------------------------------------
    # Process 'difficulty' rules within a single folder.

    def process_difficulty(self, org, folder):
        '''
        Params: org (string) - name of organisation
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered 
        '''
        rv = True
        files = get_files(folder)
        if len(files) == 0:
            # Check for nested folders in exceptional cases
            files = glob(folder+'/**/*.*', recursive=True) 
            if len(files) == 0:
                log.warning(f'No files found in folder "{folder}"')
                return False

        with Bar('Processing difficulty rules...', max=len(files)) as bar:
            for f in files:
                bar.next()
                config = self.get_configparser()
                config.read(f)
                sections = ['EndMetadata', 'Metadata', 'INI', 'Data']
                self.check_sections(config, f, sections)
                # [Metadata]
                if config.has_section('Metadata'):
                    m_data = config['Metadata']
                    tt = m_data.get('TestType', '')
                    if tt != 'IdentificationDifficulty':
                        log.error(f'Unknown TestType in file "{f}"')
                        rv = False
                else:
                    log.error(f'File "{f}" does not contain [MetaData]')
                    rv = False
                # [INI]
                if config.has_section('INI'):
                    i_data = config['INI']
                    # [Data]
                    if config.has_section('Data'):
                        for k, v in config.items('Data'):
                            diff = {'taxon_key': k,
                                    'organisation': org,
                                    'message': i_data.get(v, self.ERROR),
                                    'difficulty_key': v}
                            self.difficulties.append(diff)
                    else:
                        log.error(f'File "{f}" does not contain [Data]')
                        rv = False
                else:
                    log.error(f'File "{f}" does not contain [INI]')
                    rv = False
                
                del config

        return rv
    
    # --------------------------------------------------------------------------
    # Process 'flightperiod' rules within a single folder.

    def process_flightperiod(self, org, folder):
        '''
        Params: org (string) - name of organisation
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered
        '''
        rv = True
        files = get_files(folder)
        if len(files) == 0:
            log.warning(f'No files found in folder "{folder}"')
            return False
        
        with Bar('Processing flightperiod rules...', max=len(files)) as bar:
            for f in files:
                bar.next()
                config = self.get_configparser(allow_duplicates=True)
                config.read(f)
                sections = ['EndMetadata', 'Metadata', 'Data']
                self.check_sections(config, f, sections)
                # [Metadata]
                if config.has_section('Metadata'):
                    m_data = config['Metadata']
                    tt = m_data.get('TestType', self.ERROR)
                    if tt != 'PeriodWithinYear':
                        log.error(f'Unknown TestType in file "{f}"')
                        rv = False
                    tvk = m_data.get('Tvk', self.ERROR)
                    error_msg = m_data.get('ErrorMsg', self.ERROR)
                    start_date = m_data.get('StartDate', self.ERROR)
                    end_date = m_data.get('EndDate', self.ERROR)
                    if (error_msg == self.ERROR or tvk == self.ERROR or 
                        start_date == self.ERROR or end_date == self.ERROR):
                        log.error(f'Incorrectly formatted file (1): "{f}"')
                        rv = False
                
                    flight = {'taxon_key': tvk,
                              'organisation': org,
                              'message': error_msg,
                              'start_date': start_date,
                              'end_date': end_date,
                              'stage': ''}
                    self.flights.append(flight)                
                    # [Data]
                    if (config.has_section('Data') and 
                        len(config.items('Data')) > 0):
                        # Additional stage-specific start/end dates
                        d_data = config['Data']
                        stage = (d_data.get('Stage', self.ERROR).
                                 replace('\n\n', '\n').splitlines())
                        s_d = (d_data.get('StartDate', self.ERROR).
                               replace('\n\n', '\n').splitlines())
                        e_d = (d_data.get('EndDate', self.ERROR).
                               replace('\n\n', '\n').splitlines())
                        if (self.ERROR in stage or self.ERROR in s_d or 
                            self.ERROR in e_d):
                            log.error(f'Incorrectly formatted file (2): "{f}"')
                            return False
                        
                        for i in range(len(stage)):
                            flight = {'taxon_key': tvk,
                                      'organisation': org,
                                      'message': error_msg,
                                      'start_date': s_d[i],
                                      'end_date': e_d[i],
                                      'stage': stage[i]}
                            self.flights.append(flight)                  
                else:
                    log.error(f'File "{f}" does not contain [Metadata]')
                    rv = False

                del config

        return rv

    # --------------------------------------------------------------------------
    # Process 'period' rules within a single folder.

    def process_period(self, org, folder):
        '''
        Params: org (string) - name of organisation 
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered
        '''
        rv = self.process_period_generic(org, folder, 'period', self.periods)
        return rv

# --------------------------------------------------------------------------
    # Process genric period rules within a single folder.

    def process_period_generic(self, org, folder, test_type, rules):
        '''
        Params: org (string) - organisation name
                folder (string) - path to folder containing rules
                test_type (string) - name of test type
                rules (list) - list to which to add rules
        Return: (bool) - returns True if no errors encountered
        '''
        rv = True
        files = get_files(folder)
        if len(files) == 0:
            log.warning(f'No files found in folder "{folder}"')
            return False
        
        with Bar('Processing period rules...', max=len(files)) as bar:
            for f in files:
                bar.next()
                config = self.get_configparser(allow_duplicates=True)
                config.read(f)            
                sections = ['EndMetadata', 'Metadata', 'Data']
                self.check_sections(config, f, sections)
                # [Metadata]
                if config.has_section('Metadata'):
                    m_data = config['Metadata']
                    tt = m_data.get('TestType', self.ERROR)
                    if tt.lower() != test_type.lower():
                        log.error(f'Unknown TestType in file: "{f}"')
                        return False

                    error_msg = m_data.get('ErrorMsg', self.ERROR)
                    tvk = m_data.get('Tvk', self.ERROR)
                    error_msg = m_data.get('ErrorMsg', self.ERROR)
                    start_date = m_data.get('StartDate', self.ERROR)
                    end_date = m_data.get('EndDate', self.ERROR)
                    if (error_msg == self.ERROR or tvk == self.ERROR or 
                        start_date == self.ERROR or end_date == self.ERROR):
                        log.error(f'Incorrectly formatted file (1): "{f}"')
                        return False
                    
                    period = {'taxon_key': tvk,
                              'organisation': org,
                              'message': error_msg,
                              'start_date': start_date,
                              'end_date': end_date}
                    
                    # Add additional key for specific test type
                    if test_type == 'PeriodWithinYear':
                        period['stage'] = ''

                    rules.append(period)                    
                    # [Data]
                    if (config.has_section('Data') and 
                        len(config.items('Data')) > 0):
                        # Additional stage-specific start/end dates
                        d_data = config['Data']
                        stage = (d_data.get('Stage', self.ERROR).
                                 replace('\n\n', '\n').splitlines())
                        s_d = (d_data.get('StartDate', self.ERROR).
                               replace('\n\n', '\n').splitlines())
                        e_d = (d_data.get('EndDate', self.ERROR).
                               replace('\n\n', '\n').splitlines())
                        if (self.ERROR in stage or self.ERROR in s_d or 
                            self.ERROR in e_d):
                            log.error(f'Incorrectly formatted file (2): "{f}"')
                            return False
                        
                        for i in range(len(stage)):
                            period = {'taxon_key': tvk,
                                      'organisation': org,
                                      'message': error_msg,
                                      'start_date': s_d[i],
                                      'end_date': e_d[i],
                                      'stage': stage[i]}
                            rules.append(period)                            
                            
                else:
                    log.error(f'File "{f}" does not contain [MetaData]')
                    rv = False
                
                del config

        return rv
    
    # --------------------------------------------------------------------------
    # Process genric polygon rules within a single folder.

    def process_polygon_generic(self, org, folder, rules):
        '''
        Params: org (string) - name of organisation
                folder (string) - path to folder containing rules
                rules (list) - list to which results are written
        Return: (string) - gridrefs 
        '''
        # --------------------------------------------
        def process_country(config, country_section):
            gr = ''
            if config.has_section(country_section):
                for k, v in config.items(country_section):
                    gr = gr + k + ';'

            return gr            

        #---------------------------------------------
        rv = True
        files = get_files(folder)
        if len(files) == 0:
            log.warning(f'No files found in folder "{folder}"')
            return False
        
        with Bar('Processing region rules...', max=len(files)) as bar:
            for f in files:
                bar.next()
                config = self.get_configparser()
                config.read(f)
                sections = ['EndMetadata', 'Metadata', '10km_GB', 
                            '10km_Ireland', '10km_CI']
                self.check_sections(config, f, sections)
                # [Metadata]
                if config.has_section('Metadata'):
                    m_data = config['Metadata']
                    tt = m_data.get('TestType', self.ERROR)
                    if tt != 'WithoutPolygon':
                        log.error(f'Unknown TestType in file "{f}"')
                        rv = False
                    tvk = m_data.get('DataRecordId', self.ERROR)
                    error_msg = m_data.get('ErrorMsg', self.ERROR)
                    if tvk == self.ERROR or error_msg == self.ERROR:
                        log.error(f'Incorrectly formatted file "{f}"')
                        rv = False
                else:
                    log.error(f'File "{f}" does not contain [Metadata]')
                    rv = False
                
                gb = process_country(config, '10km_GB')
                ir = process_country(config, '10km_Ireland')
                ci = process_country(config, '10km_CI')
                region = {'taxon_key': tvk,
                          'organisation': org,
                          'message': error_msg,
                          '10km_GB': gb,
                          '10km_Ireland': ir,
                          '10km_CI': ci}                 
                rules.append(region)
                                
                del config

        return rv
    
    # --------------------------------------------------------------------------
    # Process 'range' rules within a single folder.

    def process_range(self, org, folder):
        '''
        Params: org (string) - name of organisation
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered
        '''
        rv = self.process_polygon_generic(org, folder, self.ranges)
        return rv

    # --------------------------------------------------------------------------
    # Process 'seasonalperiod' rules within a single folder.

    def process_seasonalperiod(self, org, folder):
        '''
        Params: org (string) - name of organisation 
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered
        '''
        rv = self.process_period_generic(org, folder, 'PeriodWithinYear', 
                                         self.seasonals)
        return rv

    # --------------------------------------------------------------------------
    # Process 'tenkm' rules within a single folder.

    def process_tenkm(self, org, folder):
        '''
        Params: org (string) - name of organisation
                folder (string) - path to folder containing rules
        Return: (bool) - returns True if no errors encountered 
        '''
        rv = self.process_polygon_generic(org, folder, self.regions)
        return rv

    # --------------------------------------------------------------------------
    # Read the contents of a given top-level rule folder.

    def read_rules(self, folder_root):
        '''
        Params: folder_root (string) - path to single organisation's rules
        Return: (bool) - returns True if no errors encountered
        '''
        log.info(f'Reading folder: {folder_root}')
        ok = True
        folders = get_folders(folder_root)
        if len(folders) == 0:
            log.warning(f'No folders found in folder "{folder_root}"')
            return False

        for folder in folders:
            rv = True
            org = os.path.split(folder_root)[1]
            if '_idifficulty' in folder.lower():
                rv = self.process_difficulty(org, folder)
            else:
                groups = get_folders(folder)
                for group in groups:
                    rules = get_folders(group)
                    if len(rules) == 0:
                        # Handle non-standard BSBI folder structure
                        r = os.path.split(group)[1].lower()
                        if 'period' in r:
                            rv = self.process_period(org, group)
                        elif 'range' in r:
                            rv = self.process_range(org, group)
                        else:
                            log.error(f'Unknown rule folder type: {group}')
                            rv = False
                    else:
                        # Handle all other folder structures
                        for rule in rules:
                            r = os.path.split(rule)[1].lower()
                            if r == 'additional':
                                rv = self.process_additional(org, rule)
                            elif r == 'flightperiod':
                                rv = self.process_flightperiod(org, rule)
                            elif r == 'period':
                                rv = self.process_period(org, rule)
                            elif r == 'range':
                                rv = self.process_range(org, rule)
                            elif r == 'seasonalperiod':
                                rv = self.process_seasonalperiod(org, rule)
                            elif r == 'tenkm':
                                rv = self.process_tenkm(org, rule)
                            else:
                                log.error(f'Unknown rule folder type: {rule}')
                                rv = False
            
            if rv == False:
                ok = False

        return ok

    # --------------------------------------------------------------------------
    # Read the contents of a given top-level rule folder.

    def read_specieslist(self, file_path):

        rv = True
        log.info(f'Reading species file: {file_path}')
        if os.path.isfile(file_path) == False:
            log.error(f'Species list file does not exist: {file_path}')
            return False
        
        with open(file_path) as file:
            species = file.readlines()

        header = True
        for line in species:
            if line[0] == "'":
                continue
            if header:
                header = False
                continue
            fields = line.strip('\n').split('#')
            if len(fields) == 8:
                spec = {'taxon_key': fields[0],
                        'preferred_tvk': fields[1],
                        'name': fields[2],
                        'authority': fields[3],
                        'group': fields[4],
                        'name_type': fields[5],
                        'well_formed': fields[6],
                        'msg_id': fields[7]
                        }
                self.species.append(spec)
            else:
                log.warning(f'Malformed line "{line}" in file "{file_path}"')
                rv = False

        return rv

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
    log.info('Beginning test [RuleParser.py]...')
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