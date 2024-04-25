# nbn-record-cleaner-verification-rule-parser

## Overview
This Python script uses the set of data verification rules published by the **National Biodiversity Network** (NBN) as part of its [NBN Record Cleaner](https://nbn.org.uk/tools-and-resources/nbn-toolbox/nbn-record-cleaner/) software. The NBN Record Cleaner verification rules are in the form of INI-type configuation files with one file per rule. The script traverses the verification rule folder structure, parsing and consolidating the rules into rule types. One CSV file is produced for each rule type. In addition, the species list included with NBN Record Cleaner is parsed and output in CSV format.

## Installation
Installation uses the [Pipenv](https://pipenv.pypa.io/en/latest/) package manager. In order to install Pipenv if it is not already installed:

`pip install pipenv`

In order to install this project's dependencies, from within the **Code** folder run the command:

`pipenv install`

## Operation
The script is invoked via the **NBN_Parser.bat** batch file within **Code** folder. Edit the contents of the batch file to specify the paths to the verification rule folder and the output folder:

`pipenv run python main.py --input "C:\Program Files (x86)\NBNRecordCleaner\VerificationData" --output "..\Results"`

The script will overwrite existing files of the same name in the output folder. Note that:
- If any existing files in the output folder are file-locked (e.g. open in Excel), then the script will fail with a file permission error.
- The default output folder is supplied with a set of output files produced from the full set of NBN Record Cleaner rules. A backup copy of the output files is provided in zip format (**_results_original.zip**) in the event that the original files are overwritten.
- The default output folder also contains a file **taxa_lib.csv** which is not produced by the script. This file is exported from the **GMEU** Swift software. The file is not used by the script but is included for completeness as it is used subsequently in production of a database which incorporates the CSV files.

By default, the script ignores three folders within the NBN Record Cleaner verification folder structure. These folders are:

`SKIP_FOLDERS = ['National Biodiversity Network Trust', 
                 'Personal', 
                 'SystemRules']`
				 
This list can be edited within the **RuleController** class within the **RuleController.py** file.

Operational and debugging output is written both to the terminal and to a **debug.log** file in the **Code** folder. The level of debugging output can be specified in the **main.py** file. In addition, a **skip.log** file is written to the **Code** folder. The **skip.log** file will contain details of any rule file sections which the script has been unable to process: it will be empty in normal circumstances.

## Code
The script consists of the following files:
- **main.py** - Script entry point. Processes command line arguments and instantiates an instance of the RuleController class. 
- **RuleController.py** - Implements the RuleController class which orchestrates the data input, parsing and output processes. Instantiates an instance of the RuleParser class.
- **RuleParser.py** - Implements the RuleParser class which performs the data input and parsing processes for a single organisation rule set.
- **RuleOutput.py** - Implements the RuleOutput class which performs the writing of results to CSV files.
- **utils.py** - Utility functions.
