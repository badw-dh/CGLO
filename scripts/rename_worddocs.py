# Renames Word docs in Abbyy directory so that file name corresponds to pg number.

import os
import re

word_dir = "C:/Gloss Abbyy Projects/Index graecolatinus"
offset = 440 # Add 440 to the output page number for the real page in CGL VII

for file_name in os.listdir(word_dir):
    # Check if the file has a '.docx' extension
    if file_name.endswith(".docx"):

        # Check if the name has a Roman numeral VI or VII followed by an Arabic
        # number.
        name_match = re.search(r".*(VII|VI).*?(\d+).*", file_name)
        if name_match:
            vol_number = name_match.group(1)
            page_number = int(name_match.group(2))
            page_number += offset
            page_str = str(page_number).zfill(3) # Pad the page number with zeros to 3 digits
            split_name = file_name.split('.')

            # page_with_zeroes = str(int(page_number)).zfill(3)
            new_name = f"{vol_number}.{page_number}.docx"
            os.rename(f"{word_dir}/{file_name}", f"{word_dir}/{new_name}")
            print("Renamed file", file_name, "->", new_name)

        else:
            # Filename doesn't contain Roman numeral and digits, so ignore it.
            print(f"Filename {file_name} does not contain Roman numerals and digits.")
            continue
