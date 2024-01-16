import sys, os
from pathlib import Path
from xml.sax import parse
import re, unicodedata
from pyuca import Collator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xml_parser import xml_handler, clean_lemma

BASE_DIR = Path(__file__).resolve().parent.parent.parent
XML_COMBINED_FILE = BASE_DIR / 'XML' / 'CGLO.99.combined.xml'
OUTPUT_FILENAME = 'non-alphabetic-sequences.txt'
# XML_COMBINED_FILE = '/Users/adamg/cglo-git/scripts/XML/CGLO.99.combined.xml'

def strip_Greek_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                    if unicodedata.category(c) != 'Mn')

handler = xml_handler()
parse(XML_COMBINED_FILE, handler)

c = Collator()  # initialize unicode sorter key

main_lemmata = [lemma for lemma in handler.lemma_stack if lemma['type'] == 'lemma']
# Latin_lemmata = [lemma for lemma in main_lemmata if lemma['lang'] == 'Latinum']
# Greek_lemmata = [lemma for lemma in main_lemmata if lemma['lang'] == 'Graecum']

output_file = open(OUTPUT_FILENAME, "w", encoding="utf-8")

for i, lemma in enumerate(main_lemmata):
    if i == len(main_lemmata) - 1:
        break

    current_lemma = clean_lemma(lemma['lemma'])
    next_lemma = clean_lemma(main_lemmata[i + 1]['lemma'])

    if sorted([current_lemma, next_lemma], key=c.sort_key) != [current_lemma, next_lemma]:
        output_file.write(f"{lemma['lemma']} ({lemma['location']}) > {main_lemmata[i+1]['lemma']}\n")
        # print("First lemma", lemma['lemma'], "alphabetizes after second lemma", main_lemmata[i+1]['lemma'])

    # if clean_lemma(current_lemma) > clean_lemma(next_lemma):
    #     output_file.write(f"{current_lemma} ({lemma['location']}) > {next_lemma}\n")

output_file.close()

# for i, lemma in enumerate(Greek_lemmata):
#     c = Collator()
#
#     current_lemma = clean_lemma(lemma['lemma'])
#     next_lemma = clean_lemma(Greek_lemmata[i + 1]['lemma'])
#
#     if sorted([current_lemma, next_lemma], key=c.sort_key) != [current_lemma, next_lemma]:
#         print("First lemma", lemma['lemma'], "alphabetizes after second lemma", Greek_lemmata[i+1]['lemma'])
    # print(lemma['lemma'], '->', strip_Greek_accents(lemma['lemma']))
