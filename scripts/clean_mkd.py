# Importing modules
import os
import re
import logging
from italics_scanner import *
from mkd_to_xml import file_to_paragraphs

# Core directories. Unnecessary if called from main.
default_mkd_input_path = "mkd_raw"
default_mkd_clean_path = "mkd_clean"
default_xml_output_path = "xml_output"
default_file = "VI.0001.mkd"

# Cleans all .mkd files in input_path and saves them to output_path.
def clean_MKD_directory(input_path, output_path):
    for file_name in os.listdir(input_path):
        # Check if the file has a '.mkd' extension
        if file_name.endswith(".mkd"):
            print("Cleaning file:", file_name)
            logging.info(f"Cleaning file: {file_name}")
            logging.warning(f"Cleaning file {file_name}")
            check_markdown(file_name, input_path, output_path)


def check_markdown(file_name, input_path, output_path):
    # Runs all checks and fixes basic errors on a markdown file.
    # Takes as arguments the file name, input path, and output path.

    line_number = 0
    minimum_column_length = 65

    # Make sure the file can be opened.
    try:
        my_file = open(f"{input_path}/{file_name}", encoding="utf-8")
    except IOError:
        print(f"Error: cannot open {file_name}")
        return 0

    output_file = open(f"{output_path}/{file_name}", "w", encoding="utf-8")

    # Initialize some variables.
    text_of_file = my_file.read()
    list_of_lines = text_of_file.split("\n")

    # If the last line is blank, delete it.
    # TODO: when this is moved before CGLO_Page errors result.
    if list_of_lines[-1] == "":
         list_of_lines.pop()

    # First delete comments
    for line_number, line in enumerate(list_of_lines):
        list_of_lines[line_number] = delete_comments(line, file_name, line_number)

    current_page = CGLO_Page(list_of_lines)

    # Iterate through each line in the file and clean up/make checks.
    for line_number, line in enumerate(list_of_lines):
        # line = delete_comments(line, file_name, line_number)
        line = delete_mkd_escaped_chars(line)
        line = fix_italics(line, current_page, file_name, line_number)
        line = fix_bad_sequences(line, file_name, line_number)

        output_file.write(f"{line}\n")

    # If the file has fewer than a certain number of lines, it hasn't been
    # fully converted to markdown.
    if line_number < minimum_column_length:
        logging.warning(f"Error: file {file_name} has {line_number} lines,"\
            f"which is less than {minimum_column_length}.")
    #    print(f"Error: file {file_name} has {number_of_lines} lines,"\
    #    f"which is less than {minimum_column_length}.")

    my_file.close()
    output_file.close()

def delete_comments(line, file_name, line_number):
    # Deletes lines beginning with >

    if line.startswith('>'):
        if line == "> \n":
            line == "\n"
        else:
            line = line[2:]
        logging.info(f"Line {line_number + 1}: deleted initial <")

    return line


def fix_italics(line, page, file_name, line_number):

    # List of tuples of the form: search sequence, replacement sequence,
    # within_italics (True or False), name for logging purposes.
    bad_italic_sequences = [
        (r"\*,\*", r",", True, "ISOLATED COMMA IN ITALICS"),
        (r"\*\.\*", r".", True, "ISOLATED PERIOD IN ITALICS"),
        (r"\*;\*", r";", True, "ISOLATED SEMICOLON IN ITALICS"),
        (r"(?<!\*);\*", r"*;", True, "SEMICOLON AT END OF ITALICS"),
#        (r"(?<!\*)\*\.(?![\*| \*])", r".*", False, "PERIOD OUTSIDE ITALICS"),
        (r"(?<!\*)\*\.(?!\*| \*)", r".*", False, "PERIOD OUTSIDE ITALICS"),
        (r"(?<!(\*|\\))\* \*(?![\\|\*])", r" ", False, "SINGLE SPACE OUTSIDE ITALICS"),
        (r"(?<!(\*|\\))\* \*(?![\\|\*])", r" ", True, "SINGLE SPACE INSIDE ITALICS"),
        (r"(?<![\*|\\])\*\. \*(?![\\|\*])", r". ", False, "DOT AND SPACE OUTSIDE ITALICS"),
        (r" vel ", r" uel ", True, "vel for uel IN ITALICS")
        # (r"\*(\s+)\*", r"\1", True, "WHITE SPACE ALONE IN ITALICS")  # Doesn't catch any exx. in Vol. 6.
    ]

    fixed_line = line
#    match = re.search(r"(?<!\*)\*(\S)\*", line)

    for regex, replacement, is_italics, error_name in bad_italic_sequences:
        matches = re.finditer(regex, line)

        for match in matches:

            paragraph = page.dict_of_paragraphs[line_number]
            start, end = match.span()

            if paragraph.within_italics(line_number, start, end) == is_italics:

                if replacement:
                    # There is a replacement in the tuple so fix the line and log the change.
                    fixed_line = re.sub(regex, replacement, fixed_line)
                    logging.info(f"Line {line_number + 1} *CHANGED* {error_name} ({match.group()}): {fixed_line.strip()}")
                else:
                    # No replacement so just print a warning.
                    logging.warning(f"Line {line_number + 1} {error_name} ({match.group()}): {line.strip()}")

#    if match:
#        paragraph = page.dict_of_paragraphs[line_number]
#        start, end = match.span()
#        if paragraph.within_italics(line_number, start, end) == False:
#            logging.warning(f"Line {line_number} SINGLE CHARACTER OUTSIDE ITALICS {match.group()}: {line}")
        # else:
        #    print(f"A single character WITHIN italics at {line_number}: {match.group()}.")

    return fixed_line

# TODO: Check for italicized opening or closing parenthesis.
# TODO: Check for a single letter omitted from an italics sequence.
# TODO: Check for a single punctuation mark italicized after a parenthesis
# containing italics ends.
def fix_bad_sequences(line, file_name, line_number):

    # A tuple containing: search string, replacement string (or None), label.
    # TODO: Fix numbers without appropriate spaces.

    replace_sequences = [
        (r" \*V\*\. ", r" *V.* ", "INCORRECT ITALICS *V*."),
        (r" \*v\*\.", r" *v.*", "INCORRECT ITALICS *v*."),
        (r"cf\.\.", "cf.", "cf.. WITH EXTRA DOT"),
        (r"Cf\.\.", "Cf.", "Cf.. WITH EXTRA DOT"),
        (r"cf\.,", "cf.", "cf., WITH EXTRA COMMA"),
        (r"Cf\.,", "Cf.", "Cf., WITH EXTRA COMMA"),
        (r",\*\*", "**,", "COMMA INSIDE BOLD"),
        (r"(\d+),(\d+)", r"\1, \2", "COMMA BETWEEN DIGITS WITHOUT SPACE"),
        (r"coddi\*", r"codd.*", "coddi FOR codd."),
        (r"([I|II|III|IV|V|VI|VII])(\n)", r"\1 \2", "ROMAN NUMERAL WITHOUT FOLLOWING SPACE"),
        (r"cf ", "cf. ", "cf WITHOUT DOT"),
        (r"Cf ", "Cf. ", "Cf WITHOUT DOT"),
        # (r"\*cf\*", "*cf.*", "*cf* WITHOUT DOT"),
        (r"{.mark}", "", "ITALICS DELETED"),
        (r"gloss,", "gloss.", "gloss, CORRECTED"),
        (r"Bucchi,", "Buech.", "Bucchi CORRECTED"),
        (r"codd,", "codd.", "codd, CORRECTED"),
        (r"coddi", "codd.", "coddi CORRECTED"),
        (r"Journ,", "Journ.", "Journ, CORRECTED"),
        (r"Comm,", "Comm.", "Comm, CORRECTED"),
        (r"Vulc,", "Vulc.", "Vulc, CORRECTED."),
        (r"Serv,", "Serv.", "Serv, CORRECTED."),
        (r"HS.", "AS.", "HS. for AS. (Anglosaxonicum)"),
        (r"\*\*=\*\*", "=", "EQUALS SIGN UNBOLDED"),
        (r"(?<!\*)\*=\*(?!\*)", "=", "EQUALS SIGN UNITALICIZED"),
        (r"\\\. ", ". ", "ESCAPED DOT (MARKDOWN) DELETED") # Escaped dot smtms added by markdown are not needed by us.
    ]

    warning_sequences = [
        (r"\\'", "INDENTATION FOLLOWED BY APEX?"),
        (r"(\S),(\S)", "COMMA NOT FOLLOWED BY SPACE"),
        (r"\^\d\^", "SUPERSCRIPT?"),
        (r" H \d+", "H (h) FOR ROMAN NUMERAL II?"),
        (r" Π \d+", "Π for ROMAN NUMERAL II?"),
        (r" Η \d+", "Η (eta) for ROMAN NUMERAL II?"),
        (r"[ΠHΗ][IΙ]", "Π/HI for III?"),
        (r"[IΙ][ΠHΗ]", "IΠ/H for III?"),
        (r" 111 \d+", "111 for ROMAN NUMERAL III?"),
        (r" lll \d+", "lll for ROMAN NUMERAL III?"),
        (r" 11 \d+", "11 for ROMAN NUMERAL II?"),
        (r" ll \d+", "ll for ROMAN NUMERAL II?"),
        (r" 1 \d+", "1 for ROMAN NUMERAL I?"),
        (r" l \d+", "l for ROMAN NUMERAL I?"),
        (r"([I|II|III|IV|V|VI|VII])\d+", "ROMAN NUMERAL WITHOUT SPACE?"),
        (r"([I|II|III|IV|V|VI|VII]) \d\d\d\d", "NO COMMA BETWEEN PAGE AND LINE?"),
        (r"\S;\S", "SEMICOLON WITHOUT SPACES"),
        (r"\)\w", "CLOSING BRACKET WITHOUT SPACE"),
        (r"(?<![\*|\\])\*\S\*", "SINGLE CHARACTER IN/OUTSIDE ITALICS"),
        (r"\w- \w", "HYPHENATED WORD?"),
        (r"(?<![f|\.|\\])\.\.", "TWO DOTS"),
        (r"cf(?!\.)", "cf WITHOUT DOT"),
        (r"Cf(?!\.)", "Cf WITHOUT DOT"),
        (r", \*\*", "COMMA PRECEDING OR CONCLUDING BOLD"),  # Or only after closing bracket?
        (r"·,", "SEQUENCE ·, MAYBE A COLON?"),
        (r"\d/\d", "FORWARD SLASH IN NUMERIC SEQUENCE"),
        (r"[ΧXVI ]Χ[ΧXVI ]", "GREEK CHI IN ROMAN NUMERAL"),
        (r"uncte ", "uncte FOR unde?"),
        (r"codi", "codi FOR cod.?"),
        (r"\),", "COMMA AFTER CLOSING BRACKET FOR DOT?"),
        (r" Α ", "BIG ALPHA FOR BIG A?"),
        (r"Ι", "BIG IOTA WITHOUT ACCENT FOR LATIN I?"),
        (r"Η", "BIG ETA WITHOUT ACCENT FOR LATIN H?"),
        (r'[βγδζθκλμνξπρστφχψ]ν[βγδζθκλμνξπρστφχψ]', "GREEK NU FOR UPSILON?"),
        (r'\[^αειυωΑΕΙΥΩ\s][ὐὑ]\w', "WORD INTERNAL GREEK UPSILON WITH BREATHING"),
        (r" α ", "LOWER CASE ALPHA FOR LATIN a?"),
        # (r"[aeiou]nu", "-nu- FOR -uu-?")   Generates too many results.
#        (r" Ι ", "BIG IOTA FOR BIG I?"),
#        (r"[l1IΙV ]Ι[IΙ1l ]", "BIG IOTA IN ROMAN NUMERAL")
#       (r"\*\S\*",  "SINGLE LETTER OUTSIDE ITALICS")
    ]

    fixed_line = line

    for regex, replacement, error_name in replace_sequences:
        matches = re.finditer(regex, line)

        for match in matches:
            fixed_line = re.sub(regex, replacement, fixed_line)
            logging.info(f"Line {line_number + 1} *CHANGED* {error_name} ({match.group()}): {fixed_line.strip()}")

    for regex, error_name in warning_sequences:

        matches = re.finditer(regex, fixed_line)

        for match in matches:
            logging.warning(f"Line {line_number + 1} {error_name} ({match.group()}): {line.strip()}")

    return fixed_line

# Deletes markdown escaped characters that aren't needed for XML.
def delete_mkd_escaped_chars(line):
    MKD_ESCAPED_CHARS = [
        (r"\\\[", r"["),
        (r"\\\]", r"]"),
        (r"\\\|", r"|")
        # (r"\\\+", r"+"),  # Apparently not found in CGL
        # (r"\\_", r"_"),   # Apparently not found in CGL
    ]

    for escaped_char, replacement in MKD_ESCAPED_CHARS:
        line = re.sub(escaped_char, replacement, line)

    return line

if __name__ == "__main__":
    check_markdown(default_file, default_mkd_input_path, default_mkd_clean_path)
