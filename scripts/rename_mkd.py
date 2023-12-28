# Rename all markdown files according to CGL conventions necessary
# for later processing.
# e.g. take file like "CGL VII - 0001.mkd" and rename it "VII.001.mkd"
# Preface files should have the form "VI.praef_09.mkd" (Arabic for Roman numeral)

import re, os

default_mkd_directory = 'word_test'

def rename_mkd_files(mkd_input_path):

    name_input_pattern = re.compile(r".*(VII|VI).*?(\d+)(a|b)?.*")
    name_output_pattern = re.compile(r"(VII|VI).(\d+)[ab]?.mkd")

    for file_name in os.listdir(mkd_input_path):
        if not file_name.endswith('.mkd'):
            continue

        # Check if the name has a Roman numeral VI or VII followed by an Arabic
        # number.
        name_match = name_input_pattern.search(file_name)
        if name_match == None:
            print(f"Filename {file_name} does not contain Roman numerals and digits.")
            continue

        # Ignore if the file is already in the correct format.
        if name_output_pattern.search(file_name):
            continue

        vol_number = name_match.group(1)
        page_number = str(int(name_match.group(2))).zfill(3) # Pad the page number with zeros to 3 digits

        # If the file_name is already in the correct format ignore.
        split_name = file_name.split('.')
        if split_name[0] == vol_number and split_name[1] == page_number:
            continue

        # If the name is a preface page also ignore.
        if split_name[1].startswith('praef'):
            continue

        # Otherwise rename the file in the correct format.
        if name_match.group(3):
            new_name = f"{vol_number}.{page_number}{name_match.group(3)}.mkd"
        else:
            new_name = f"{vol_number}.{page_number}.mkd"

        os.rename(f"{mkd_input_path}/{file_name}", f"{mkd_input_path}/{new_name}")
        print("Renamed file", file_name, "->", new_name)

if __name__ == "__main__":
    rename_mkd_files(default_mkd_directory)
