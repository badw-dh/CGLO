# Import necessary modules
import os  # Module for working with the operating system (file operations)
import re  # Module for regular expressions (used for text extraction)
import json  # Module for working with JSON data
from pathlib import Path

from xml_parser import *
from xml.sax.saxutils import escape
from roman_to_arabic import rom_arab # to convert Roman to Arabic numerals
from identify_gloss import identify_gloss_from_xref  # to get short names of glossaries

# Define the folder paths for input and output
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_XML_PATH = BASE_DIR / 'XML'
DEFAULT_JSON_PATH = BASE_DIR / 'JSON'
DEFAULT_FILE = 'CGLO.99.combined.xml'

# Define a function to extract text within specified XML tags
def extract_text(text, tag):
    # Construct a regular expression pattern to find and extract the text
    reg_str = "<" + tag + ".*?>(.*?)</" + tag + ">"
    # Use re.findall to extract the text and return it
    res = re.findall(reg_str, text)

    return res[0]


# Iterate through files in the input folder and output all lemma to a single JSON file.
def convert_directory_to_JSON(input_path, output_path):
    complete_text = ''

    for file_name in os.listdir(input_path):
        if file_name.endswith('.xml'):
            print("Current file:", file_name)

            with open(f"{input_path}/{file_name}", encoding='utf-8') as file:
                data = file.read()

            complete_text += XML_to_lemma_list(data, file_name)

    json_object = lemma_list_to_JSON(complete_text)

    output_file = file_name.strip('.xml')

    # Write the modified text to an output text file
    with open(f'{output_path}/complete_text.txt', "w", encoding="utf-8") as f:
        f.write(complete_text)

    # Write the JSON data to an output JSON file
    with open(f'{output_path}/CGLO_lemma_list.json', "w", encoding="utf-8") as outfile:
        outfile.write(json_object)

# Converts single file to JSON output.
def convert_file_to_JSON(file_name, input_path = DEFAULT_XML_PATH, output_path = DEFAULT_JSON_PATH):
    handler = xml_handler()
    parse(f"{input_path}/{file_name}", handler)

    json_object = lemma_dict_to_json(handler.lemma_stack)

    output_file = file_name.rstrip('.xml')

    # Write the JSON data to an output JSON file
    with open(f"{output_path}/{output_file}.json", "w", encoding="utf-8") as outfile:
        outfile.write(json_object)

    return handler.lemma_stack


def arabicize(term):
    for old, new in (
            ('I',   '1'),
            ('II',  '2'),
            ('III', '3'),
            ('IV',  '4'),
            ('V',   '5'),
            ('VI',  '6'),
            ('VII', '7'),
            ):
        term = re.sub(rf'^{old}(?=\.|$)', new, term)
        # term = re.sub(rf'(?<=/){old}(?=_|\.)', new, term)
        # term = re.sub(rf'^{old}\.', f'{new}.', term)
    return term

def lemma_dict_to_json(lemma_list):
    json_dictionary = []
    counter = 1

    for item in lemma_list:
        lemma = rename_corrigenda(item)  # add [CORR] or [ADD] to corrigenda lemmata
        lemma = remove_parentheses(lemma)  # delete all parenthesis except (?) and (!)
        lemma = escape(lemma)
        location = item["location"]
        xref_list = sort_xrefs(item["x-refs"])
        lang = abbreviate_lang(item["lang"])

        location_Ar = arabicize(location)

        if ".praef_" in location_Ar:  # special treatment for preface pages
            volume, praef_page  = location_Ar.split('.praef_')
            praef_page = str(rom_arab(praef_page))
            location_Ar = volume + '_praef.' + praef_page

        index_loc = f"<a onclick=\"rI(event,'-/{location_Ar}.jpg',4)\">{location.replace('.', ' ')}</a>"
        xref_locs = ""

        for xref in xref_list:
            xref_location, xref_readable = cref_to_JSON(xref)
            short_name = identify_gloss_from_xref(xref_readable)
            if short_name is not None:
                xref_locs += f"<a onclick=\"rI(event,'-/{xref_location}.jpg',4)\">{short_name} {xref_readable}</a> "
            else:
                xref_locs += f"<a onclick=\"rI(event,'-/{xref_location}.jpg',4)\">{xref_readable}</a> "

        current_entry = {
            "0": {
                "_": lemma,
                "s": counter
            },
            "1": index_loc,
            "2": lang,
            "3": xref_locs,
            "DT_RowId": counter
        }

        json_dictionary.append(current_entry)
        counter += 1

    json_object = json.dumps(
        {"data": json_dictionary}, indent=4, ensure_ascii=False)

    return json_object

# Take a lemma_list produced from parser and return a text file containing
# human-readable lemmata and cross-references.
def lemma_list_to_txt(lemma_list):
    lemma_dictionary = []

    for item in lemma_list:
        # lemma = item["lemma"]
        lemma = rename_corrigenda(item)
        location = item["location"]
        xref_list = item["x-refs"]
        id = item["id"]
        lang = item["lang"]
        type = item["type"]

        if item["type"] == "sublemma":  # add spaces before a sublemma
            lemma = '  ' + lemma

        new_entry = lemma + ": " + id + ', ' + lang + ', ' + type + ': ' + location + ": " + '; '.join(xref_list)

        lemma_dictionary.append(new_entry)

    lemma_txt = '\n'.join(lemma_dictionary)
    return lemma_txt

# Takes a reference in the form "V.532.34" and returns 1) a machine-readable
# image location; and 2) a human-readable "V 532, 34"
def cref_to_JSON(xref):
    split_xref = xref.split('.')
    xref_Ar = arabicize(split_xref[0])

    # If the xref is to a prefatory page:
    if split_xref[1].startswith('praef'):
        preface_page = split_xref[1].removeprefix('praef_')
        preface_page_Ar = rom_arab(preface_page)
        location = xref_Ar + '_praef.' + str(preface_page_Ar)
        readable_xref = split_xref[0] + ' ' + 'p. ' + preface_page
        # print(location, ' = ', readable_xref)
    else:
        location = xref_Ar + '.' + split_xref[1]
        readable_xref = split_xref[0] + ' ' + split_xref[1] + ', ' + split_xref[2]

    # print(location, ' = ', readable_xref)
    return location, readable_xref


# Sort xrefs in sequential order. Currently praef. appears at end of volume.
def sort_xrefs(xref_list):
    xref_tuples = []

    for xref in xref_list:
        xref_split = xref.split('.')

        # Check if it is a reference to a preface page, which needs special treatment.
        if xref_split[1].startswith('praef'):
            xref_split.append(xref_split[1]) # Move the page to the end of the list.
            xref_split[1] = 0 # Replace it with number 0 so that it is indexed first.
        else:
            xref_split[1] = int(xref_split[1])

        xref_tuples.append(tuple(xref_split))

    sorted_tuples = sorted(xref_tuples)
    # sorted_tuples = sorted(xref_tuples, key=lambda xref: (arabicize(xref[0]), xref[1], xref[2]))
    # sorted_tuples = sorted(xref_tuples, key=lambda xref: xref[1])
    # print("Sorted:", sorted_xrefs)

    sorted_xrefs = []
    for xref in sorted_tuples:
        if xref[2].startswith('praef'): # The order of preface refs needs to be rearranged.
            sorted_xrefs.append(f'{xref[0]}.{xref[2]}')
            print(sorted_xrefs[-1])
        else:
            sorted_xrefs.append(f'{xref[0]}.{xref[1]}.{xref[2]}')

    # print(sorted_xrefs)

    return sorted_xrefs


# Takes a lemma-list item and adds text to the lemma to distinguish corrigenda, delenda, addenda.
def rename_corrigenda(item):
    lemma = item["lemma"]
    type = item["type"]

    if type in ["lemma", "sublemma"]:
        return lemma

    if lemma.endswith(']'):
        lemma = lemma[:-1]

    match type:
        case 'corrigendum':
            lemma += ' [CORR]'
        case 'addendum':
            lemma += ' [ADD]'
        case 'delendum':
            lemma += ' [DEL]'

    return lemma


# Deletes any parenthetical remarks within a lemma string except for (?) and (!)
def remove_parentheses(lemma):
    parentheses = re.finditer(r'\((.+\))', lemma)
    for match in parentheses:

        if match.group(1) == '!' or match.group(1) == '?':
            replace_string = match.group()
        else:
            replace_string = ''

        lemma = re.sub(r'\((.+\))', replace_string, lemma)

    return lemma


# Takes a string defining the language and returns an abbreviation:
# Latinum -> L
# Graecum -> G
# incertum -> I
# Palaeotheodiscum -> T
# Anglosaxonicum -> A
def abbreviate_lang(lang):
    if lang == 'Palaeotheodiscum':
        return 'T'
    else:
        return lang[0].upper()


if __name__ == "__main__":
    # convert_directory_to_JSON(default_XML_path, default_JSON_path)

    lemma_stack = convert_file_to_JSON(DEFAULT_FILE, DEFAULT_XML_PATH, DEFAULT_JSON_PATH)

    # Print a file with just lemmata and cross-references.
    with open(f"{DEFAULT_JSON_PATH}/lemma_list.txt", "w", encoding="utf-8") as f:
        f.write(lemma_list_to_txt(lemma_stack))
