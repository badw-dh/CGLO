import argparse
import os
from mkd_to_xml import *

# input_path = 'mkd_clean'
# input_path = 'mkd_clean'  # Directory with correct filenames (change later!)
# output_path = 'mkd_combined'

THE_GLOSS_TOC = [
    ("A", "VI", "001", "122"),
    ("B", "VI", "123", "159a"),
    ("C", "VI", "159b", "302a"),
    ("D", "VI", "302b,", "370"),
    ("E", "VI", "371", "427"),
    ("F", "VI", "428", "480a"),
    ("G", "VI", "480b", "509a"),
    ("H", "VI", "509b", "533a"),
    ("I", "VI", "533b", "614a"),
    ("K", "VI", "614b", "614b"),
    ("L", "VI", "615", "665a"),
    ("M", "VI", "665b", "724a"),
    ("N", "VI", "724b", "753a"),
    ("corr-II", "VI", "753b", "754"),  # 14
    ("corr-I", "VI", "praef_09", "praef_10"),  #15
    ("O", "VII", "001", "036a"),  # 16
    ("P", "VII", "036b", "165a"),  # 17
    ("Q", "VII", "165b", "179a"),  # 18
    ("R", "VII", "179b", "220a"),  #19
    ("S", "VII", "220b", "327a"),  # 20
    ("T", "VII", "327b", "378a"),  #21
    ("U", "VII", "378b", "389a"),  #22
    ("V", "VII", "389b", "431a"),  #23
    ("XYZ", "VII", "431b", "433"), # 24
    ("corr-III", "VII", "434", "438"),  #25
    ("Graeco-Latinus", "VII", "441", "687"),  #26
    ("Anglosaxonicus", "VII", "689", "712a"),  #27
    ("Palaeotheodiscus", "VII", "712b", "712b"),  # 28
    ("corr-IV", "VII", "712c", "712c")  #29
]

# Combines MKD files into separate files for each section and into a complete MKD file.
# Assumes files in path are all correctly named, e.g. VI.001.mkd, VI.159a.mkd, VI.159b.mkd, VI.praef_09.mkd, etc.
# Files are stored in by default in path MKD_combined.

def combine_MKD_TOC(input_path, output_path):
    sections = {}
    all_lines = []
    section_num = 0
    section_lines = []

    list_of_files = [f for f in os.listdir(input_path) if f.startswith("VI") and f.endswith(".mkd")]

    section_name, section_vol, section_start, section_end = THE_GLOSS_TOC[section_num]

    # Construct a dictionary of sections mapped to all their lines.
    for current_file in list_of_files:
        print("Combining file:", current_file)

        volume, page, extension = current_file.split('.')

        with open(f"{input_path}/{current_file}", "r", encoding="utf-8") as my_file:
            new_lines = my_file.readlines()

        # Replace xml special characters with escape codes. We need to do this
        # here before adding pb tags, otherwise " in XML tags will be escaped.
        # for i, line in enumerate(new_lines):
        #     new_lines[i] = escape_characters(line)

        # We don't need to add a newline to the very first line of the first file.
        if section_lines == []:
            pass
        # But if the new file starts with a new paragraph, add an extra line break and continue.
        elif is_new_paragraph(new_lines[0]):
            section_lines[-1] = section_lines[-1] + "\n"

        # Otherwise combine the paragraphs and store the new lines in the right places.
        else:
            # print("Combining two paragraphs!")
            first_line, second_line = combine_lines(section_lines[-1], new_lines[0])
            section_lines[-1] = first_line
            new_lines[0] = second_line


        # Add a pb tag to remember the page number (except for filenames ending in 'b'
            # Sometimes pages are split across two files e.g. VI.159a.mkd, IV.159b.mkd
            # In these cases we only want to give a pb tag before VI.159a.mkd.
        # if not current_file.endswith('b.mkd'):
        #     section_lines.append(pb_tag(current_file))
        section_lines.append(pb_tag(current_file))

        # Keep adding lines to section_lines.
        section_lines.extend(new_lines)

        if page != section_end:
            continue
        elif page == section_end:
            # Add new key and section_lines to map.
            wrap_section(section_lines, section_name)

            sections.update({section_name: section_lines})
            print("Completed section:", section_name)
            # clear section_lines
            section_lines = []
            section_num += 1

            if section_num == len(THE_GLOSS_TOC):
                 break

            section_name, section_vol, section_start, section_end = THE_GLOSS_TOC[section_num]

    # Iterate over the map of sections and save files for each section.
    section_num = 1
    for section_name in sections:
        formatted_num = str(section_num).zfill(2)
        output_name = f"CGLO.{formatted_num}.{section_name}.mkd"
        print(f"Saving {section_name} as {output_name}.")
        with open(f"{output_path}/{output_name}", "w", encoding="utf-8") as output_file:
            output_file.write(''.join(sections[section_name]))

        # Create a combined list of lines and save this also.
        all_lines.extend(sections[section_name])
        section_num += 1

    print("Saving CGLO.99.combined.mkd")
    with open(f"{output_path}/CGLO.99.combined.mkd", "w", encoding="utf-8") as output_file:
        output_file.write(''.join(all_lines))


def combine_MKD(path, start_page = None, end_page = None):

    list_of_lines = []

    # Create a list of files in the directory whose name matches naming criteria.
    list_of_files = [f for f in os.listdir(path) if f.startswith("VI") and f.endswith(".mkd")]

    # If no start page is given, set default at 0.
    if start_page:
        start_page = start_page - 1
    else:
        start_page = 0

    # If no end page is given, set default to the end of the directory.
    if end_page:
        if end_page > len(list_of_files):
            raise Exception(f"End page {end_page} is more than {len(list_of_files)} files in {path}.")
    else:
        end_page = len(list_of_files)

    print(f"Start {start_page + 1} to end {end_page} in {path}.")

    for count in range(start_page, end_page):
        file_name = list_of_files[count]
        print("Combining file", file_name)


        with open(f"{path}/{file_name}", "r", encoding="utf-8") as my_file:
            new_lines = my_file.readlines()

        # Replace xml special characters with escape codes. We need to do this
        # here before adding pb tags, otherwise " in XML tags will be escaped.
        for i, line in enumerate(new_lines):
            new_lines[i] = escape_characters(line)

        # We don't need to add a newline to the very first line of the first file.
        if list_of_lines == []:
            pass

        # If the new file starts with a new paragraph, add an extra line break and continue.
        elif is_new_paragraph(new_lines[0]):
            list_of_lines[-1] = list_of_lines[-1] + "\n"

        # Otherwise combine the paragraphs and store the new lines in the right places.
        else:
            # print("Combining two paragraphs!")
            first_line, second_line = combine_lines(list_of_lines[-1], new_lines[0])
            list_of_lines[-1] = first_line
            new_lines[0] = second_line


        # Add a pb tag to remember the page number (except for filenames ending in 'b'
            # Sometimes pages are split across two files e.g. VI.159a.mkd, IV.159b.mkd
            # In these cases we only want to give a pb tag before VI.159a.mkd.
        if not file_name.endswith('b.mkd'):
            list_of_lines.append(pb_tag(file_name))

        list_of_lines.extend(new_lines)

    with open(f"{output_path}/CGLOcombined{start_page + 1}to{end_page}.mkd", "w", encoding="utf-8") as output_file:
        output_file.write(''.join(list_of_lines))

def is_new_paragraph(paragraph):
    return paragraph.startswith("**")

def combine_lines(first_line, second_line):

    # If the first line ends with a hyphen we need to combine the words and return
    # the modified lines.
    if first_line.endswith("-\n"):
        split_second_line = second_line.split(' ')
        word_fragment = split_second_line.pop(0)
        fixed_first_line = first_line.replace('-', word_fragment)
        fixed_second_line = ' '.join(split_second_line)

        return fixed_first_line, fixed_second_line

    # The second line begins with a digit (it's likely part of an xref).
    elif second_line[0].isdigit():

        # Take everyhing up until the first full stop and append it to the previous line.
        split_second_line = second_line.split('.')
        xref_fragment = split_second_line.pop(0)
        fixed_first_line = first_line + xref_fragment + '.'
        fixed_second_line = '.'.join(split_second_line)

        return fixed_first_line, fixed_second_line

    # Nothing to change.
    else:
        return first_line, second_line


if __name__ == "__main__":
    # Run the script with arguments: -s <start page> -e <end page> -d <directory>
    # otherwise combine all XML files in default directory.
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", type=int)
    parser.add_argument("-e", "--end", type=int)
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        path = args.directory
    else:
        path = input_path

    # combine_MKD(path, args.start, args.end)
    combine_MKD_TOC(path)
