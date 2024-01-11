# Module to identify a glossary given a volume, page, and line number in CGL

import openpyxl  # for excel
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent
gloss_xml = ROOT_DIR / 'data' / 'gloss_names.xlsx'  # glossary spreadsheet
GLOSSARIES = None  # a dict of glossaries initialized once from file

class Glossary(object):
    previous_glossary = None  # class attribute to remember the previous Glossary instance

    def __init__(self, short_name, TLL_name, start, end):
        self.short_name = short_name
        self.TLL_name = TLL_name
        self.previous_glossary = Glossary.previous_glossary
        self.set_start(start)
        self.set_end(end)

        # Uncomment next line to check for overlaps:
        # self.check_for_overlaps(short_name, self.start['volume'], self.start['page'], self.start['line'])

        Glossary.previous_glossary = self


    def is_in_range(self, volume, page, line):
        # volume, page, line = parse_xref(xref)

        if volume != self.start['volume']:
            return False

        if page > self.start['page'] and page < self.end['page']:
            return True
        elif page == self.start['page'] == self.end['page']:
            # The glossary begins and ends on the same page
            if line >= self.start['line'] and line <= self.end['line']:
                return True
            else:
                return False
        elif page == self.start['page'] and line >= self.start['line']:
            return True
        elif page == self.end['page'] and line <= self.end['line']:
            return True
        else:
            return False

    # Store the start position as a dict {'volume': v, 'page': int, 'line': int}
    # Assume start is in the form 'V 453, 9' or 'V 453'
    def set_start(self, start):
        volume, page, line = parse_xref(start)
        if line is None:
            line = 1

        self.start = {'volume': volume, 'page': page, 'line': line}


    def set_end(self, end):
        volume, page, line = parse_xref(end)
        if line is None:
            line = 100  # Max number of lines. Are there ever more than this on a CGL page?

        self.end = {'volume': volume, 'page': page, 'line': line}

    # Cycles through previous glossaries in the same volume to identify any overlaps.
    # Currently not in use.
    def check_for_overlaps(self, name, volume, page, line):
        last_glossary = self.previous_glossary

        if last_glossary == None or last_glossary.end['volume'] != volume:
            return
        else:
            if last_glossary.is_in_range(volume, page, line):
                print(f"{volume}: {name} ({page}, {line} to {self.end['page']},"
                f" {self.end['line']}) overlaps with {last_glossary.short_name}"
                f" ({last_glossary.start['page']}, {last_glossary.start['line']}"
                f" to {last_glossary.end['page']}, {last_glossary.end['line']}).")
            else:
                last_glossary.check_for_overlaps(name, volume, page, line)

# Function takes an xref in form "II 432, 42" and returns the name of the glossary
# it belongs to.
def identify_gloss_from_xref(xref):
    try:
        volume, page, line = parse_xref(xref)
    except Exception:  # E.g. references of the form "II p. XLV"
        return None

    global GLOSSARIES
    if GLOSSARIES is None:
        GLOSSARIES = load_spreadsheet()


    possible_glossaries = []

    if volume not in ["II", "III", "IV", "V"]:
        # print(f"Xref {xref} outside of named glossaries.")
        logging.warning(f"Xref {xref} has an invalid volume number.")
        return None

    for glossary in GLOSSARIES[volume]:
        if glossary.is_in_range(volume, page, line):
            possible_glossaries.append(glossary)

    # There is just one possible glossary, so return its name.
    if len(possible_glossaries) == 1:
        return possible_glossaries[0].short_name

    # There are no results:
    elif len(possible_glossaries) == 0:
        # return None
        logging.warning(f"No named glossary found for xref {xref}.")
        return ''

    # There are multiple results to resolve:
    else:
        return resolve_gloss_conflict(possible_glossaries)


# Loads spreadsheet containing name of glossary and beginning and end values.
# Returns a dictionary with keys as volume number "I" , "II", etc.
# Each key contains a list of all the glossary objects in that volume.
# Each glossary object can be queried whether the xref belongs in its range.
def load_spreadsheet():
    glossaries = {}
    wb = openpyxl.load_workbook(gloss_xml)
    sheet = wb['ToC']  # The sheet is named 'ToC'

    for row in range(2, sheet.max_row + 1):
        volume = sheet['A' + str(row)].value
        short_name = sheet['B' + str(row)].value
        TLL_name = sheet['C' + str(row)].value
        start = sheet['D' + str(row)].value
        end = sheet['E' + str(row)].value

        if short_name is not None:
            if short_name.startswith('#'):  # If escape character starts the name, ignore the row.
                continue

            else:
                short_name = short_name.strip()

        glossary = Glossary(short_name, TLL_name, start, end)

        if volume in glossaries.keys():
            glossaries[volume].append(glossary)
        else:
            if volume not in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']:
                raise Exception(f'volume {volume} not in expected range at {gloss_xml}, A{row}')
            else:
                glossaries[volume] = [glossary]

    return glossaries

# Takes an xref string and breaks it down into a volume, page, and line number.
# currently doesn't handle page numbers as Roman numerals ("p. XLVII")
# TODO: store prefatory pages as negative integers?
def parse_xref(xref: str) -> (str, int, int):
    try:
        split_xref = xref.strip().split(' ')
        volume = split_xref[0]
        page = int(split_xref[1].rstrip('ab,'))  # ignore 'a' and 'b' for now
        if len(split_xref) > 2:
            line = split_xref[2].partition('/')  # If line looks like "56/57" take only 56.
            line = int(line[0])
        else:
            line = None

        return volume, page, line
    except:
        raise Exception(f"not a valid xref format {xref}")


# Takes a list of possible glossaries in conflict and returns a single name.
def resolve_gloss_conflict(possible_glossaries):

    # Ignore glossaries without a valid short_name
    for glossary in possible_glossaries:
        if glossary.short_name is None:
            possible_glossaries.remove(glossary)

    name = possible_glossaries[0].short_name
    for glossary in possible_glossaries[1:]:
        name += f" / {glossary.short_name}"

    return name


if __name__ == "__main__":
    # glossaries = load_spreadsheet()

    # for volume in glossaries.keys():
    #     print(volume)
    #     for glossary in glossaries[volume]:
    #         print(glossary.short_name, glossary.start, glossary.end)

    for xref in ['II 561, 35', 'II 563, 10', 'II 563, 47', 'II 564, 1', 'III 506, 5']:
        name = identify_gloss_from_xref(xref)
        print(f"xref {xref} -> {name}")
