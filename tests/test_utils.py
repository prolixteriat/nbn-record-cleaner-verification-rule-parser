'''
About  : Tests for utility.py module.
Author : Kevin Morley
Version: 1 (07-Jun-2023)
Note   : Does not test utils.ElapsedTime class.
'''

# ------------------------------------------------------------------------------

import pytest
import sys

# ------------------------------------------------------------------------------

sys.path.append('./')  # path to module to be tested

# ------------------------------------------------------------------------------

import utils
    
# ------------------------------------------------------------------------------
# Fixture to return path to Record Cleaner's verification folder.

@pytest.fixture
def path_to_nbn_folder():
    return r'C:\Program Files (x86)\NBNRecordCleaner\VerificationData'

# ------------------------------------------------------------------------------
# Verification folder should contain 31 sub-folders at top-level.

def test_get_folders(path_to_nbn_folder):
    folders = utils.get_folders(path_to_nbn_folder)
    assert len(folders) == 31

# ------------------------------------------------------------------------------
# Verification folder should contain 17 files at top level.

def test_get_files(path_to_nbn_folder):
    folders = utils.get_files(path_to_nbn_folder)
    assert len(folders) == 17

# ------------------------------------------------------------------------------
# Ensure that a MultiOrderedDict object can contain multiple values for same key.

def test_MultiOrderedDict():
    mod = utils.MultiOrderedDict()
    mod['test'] = [5]
    mod['test'] = [6]
    mod['test'] = [7]
    assert len(mod['test']) == 3

# ------------------------------------------------------------------------------
       
'''
End
'''
