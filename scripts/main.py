# Module calls functions in the two main modules "mkd_to_xml.py"
# and "clean_mkd.py".
# Basic job is to clean up the MKD files and then generate XML from them.

# Standard library imports
import argparse, logging, re
from pathlib import Path

# Project imports
from mkd_to_xml import *
from clean_mkd import *
from combine_mkd import *
from combine_xml import combine_XML_files
from rename_mkd import rename_mkd_files
from add_xml_attribs import add_attribs_to_dir

# Default data directories
BASE_DIR = Path(__file__).resolve().parent.parent
MKD_INPUT_PATH = BASE_DIR / "markdown_raw"
MKD_CLEAN_PATH = BASE_DIR / "markdown"
MKD_COMBINED_PATH = BASE_DIR / "markdown-combined"
XML_OUTPUT_PATH = BASE_DIR / "XML"
# mkd_input_path = "mkd_raw"
# mkd_clean_path = "mkd_clean"
# mkd_combined_path = "mkd_combined"
# xml_output_path = "xml_output"
# mkd_prepped_for_TOC = "mkd_prepped_for_TOC"  # Directory where file names are consistent for producing sections. Delete later.


# Initiate two logging files: everything at info level and below to CGLO-info.log
# and warning messages to CGLO-warning.log. New logging file on every run.
# To keep INFO and WARNING messages separate we need a Filter.
class WarningFilter(logging.Filter):
    def filter(self, record):
        return record.levelno <= logging.INFO

logging.basicConfig(filename="logs/CGLO.log", encoding='utf-8', filemode='w', level=logging.INFO)
log_error = logging.FileHandler("logs/cglo-warning.log", encoding="utf-8", mode="w")
log_error.setLevel(logging.WARNING)
log_info = logging.FileHandler("logs/cglo-info.log", encoding="utf-8", mode="w")
log_info.setLevel(logging.INFO)
log_info.addFilter(WarningFilter())

# Add the handlers to the root logger.
logging.getLogger('').addHandler(log_error)
logging.getLogger('').addHandler(log_info)

# Basic logging to one file.
# logging.basicConfig(filename="CGLO.log", encoding='utf-8', filemode='w', level=logging.INFO)

# Initialize argument parser.
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")
parser.add_argument("-d", "--directory")
args = parser.parse_args()

if args.mode:
    mode = args.mode
else:
    mode = 'default'

# Depending on the mode change the default directory variable.
if args.directory:
    match mode:
        case 'default':
            MKD_INPUT_PATH = args.directory
        case 'clean':
            MKD_INPUT_PATH = args.directory
        case 'rename':
            MKD_INPUT_PATH = args.directory
        case 'combine':
            MKD_CLEAN_PATH = args.directory
        case 'xml':
            MKD_COMBINED_PATH = args.directory

match mode:
    case 'default':
        # Clean up the markdown files and save them to directory mkd_clean_path.
        clean_MKD_directory(MKD_INPUT_PATH, MKD_CLEAN_PATH)

        # Next combine all markdown files in mkd_clean_path together, save in mkd_combined_path.
        # combine_MKD_TOC(mkd_clean_path)
        combine_MKD_TOC(MKD_CLEAN_PATH)

        # Next generate an XML from all files in xml_output_path and save.
        generate_XML_from_dir(MKD_COMBINED_PATH, XML_OUTPUT_PATH)

        # Add final attribute tags to all XML files in the xml directory.
        add_attribs_to_dir(XML_OUTPUT_PATH)

        # Combine XML files into one file named CGLO.99.combined.xml
        combine_XML_files(XML_OUTPUT_PATH)

        # Fill in lemma cross-refs <xr> with <target> tags.

    case 'rename':
        # Check the input files and change any names that don't conform to the
        # name convention: "vol.page#.mkd"
        rename_mkd_files(MKD_INPUT_PATH)

    case 'clean':
        clean_MKD_directory(MKD_INPUT_PATH, MKD_CLEAN_PATH)

    case 'combine':
        combine_MKD_TOC(MKD_CLEAN_PATH, MKD_COMBINED_PATH)

    case 'xml':
        generate_XML_from_dir(MKD_COMBINED_PATH, XML_OUTPUT_PATH)

# CLose log files.
log_error.close()
log_info.close()
