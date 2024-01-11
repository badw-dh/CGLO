import sys, os
from pathlib import Path
from xml.sax import parse
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xml_parser import xml_handler, clean_lemma

BASE_DIR = Path(__file__).resolve().parent.parent.parent
XML_COMBINED_FILE = BASE_DIR / 'XML' / 'CGLO.99.combined.xml'
OUTPUT_FILENAME = 'non-alphabetic-sequences.txt'
# XML_COMBINED_FILE = '/Users/adamg/cglo-git/scripts/XML/CGLO.99.combined.xml'


handler = xml_handler()
parse(XML_COMBINED_FILE, handler)

main_lemmata = [lemma for lemma in handler.lemma_stack if lemma['type'] == 'lemma']

output_file = open(OUTPUT_FILENAME, "w", encoding="utf-8")

for i, lemma in enumerate(main_lemmata):
    if i == len(main_lemmata) - 1:
        break

    current_lemma = lemma['lemma']
    next_lemma = main_lemmata[i + 1]['lemma']

    if clean_lemma(current_lemma) > clean_lemma(next_lemma):
        output_file.write(f"{current_lemma} ({lemma['location']}) > {next_lemma}\n")

output_file.close()
