import sys, os
from pathlib import Path
from xml.sax import parse
from lxml import etree
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xml_parser import xml_handler, clean_lemma

BASE_DIR = Path(__file__).resolve().parent.parent.parent
XML_COMBINED_FILE = BASE_DIR / 'XML' / 'CGLO.99.combined.xml'
OUTPUT_FILENAME = 'non_matching_xrs.md'


# Initializes a dictionary whose key matches all lemmata with the same headword.
SEARCH_DICT = None

def initialize_dictionary(lemma_list):
    search_dict = {}
    for lemma in lemma_list:
        key = clean_lemma(lemma['lemma'])

        if key in search_dict.keys():
            search_dict[key].append(lemma)
        else:
            search_dict[key] = [lemma]

    return search_dict


# Returns list of all lemmata whose name matches lemma.
def find_lemma(search_str, lemma_list):
    matches = []
    search_str = clean_lemma(search_str)
    global SEARCH_DICT
    if SEARCH_DICT is None:
        SEARCH_DICT = initialize_dictionary(lemma_list)

    # Create a dictionary whose key is a cleaned headword. The contents are a list containing all relevant lemmata.
    try:
        return SEARCH_DICT[search_str]
    except:
        return []


if __name__ == '__main__':
    handler = xml_handler()
    parse(XML_COMBINED_FILE, handler)
    lemma_stack = handler.lemma_stack
    main_lemmata = [lemma for lemma in handler.lemma_stack if lemma['type'] == 'lemma']

    # Traverse the XML tree and find occurrences of <xr>
    # If the <xr> name corresponds to a lemma name, ignore.
    # Otherwise print the result.
    tree = etree.parse(XML_COMBINED_FILE)
    root = tree.getroot()


    output_file = open(OUTPUT_FILENAME, "w", encoding="utf-8")
    for xr in root.iter('xr'):
        target = xr.text
        try:
            preceding_lemma = xr.xpath("preceding-sibling::form")[-1].text
        except:
            print("No preceding <form> at line", xr.sourceline)
            preceding_lemma = 'NONE'

        results = find_lemma(target, main_lemmata)

        if results == []:
            # print("Xr", target, "not found.")
            output_file.write(f"Xr '{target}' (s.v. '{preceding_lemma}') not found.\n")
        else:
             if len(results) > 1:
                output_file.write(f"Xr '{target}' (s.v. '{preceding_lemma}') returns multiple results.\n")

    output_file.close()
