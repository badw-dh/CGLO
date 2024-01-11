import argparse
import os
from pathlib import Path

# Project imports
from mkd_to_xml import *

BASE_PATH = Path(__file__).resolve().parent.parent
DEFAULT_PATH = BASE_PATH / "XML"
DEFAULT_OUTPUT_FILE = "CGLO.99.combined.xml"

def combine_XML_files(path, output_filename = DEFAULT_OUTPUT_FILE, combine_attributes = False):
    # Copy all files from CGLO.01.A.xml to CGL.01.13.N.xml
    files = [f for f in os.listdir(path) if f.endswith(".xml") and int(f.split('.')[1]) < 99]

    print("Files before cleaning:", files)
    if combine_attributes:
        files = [f for f in files if f.split('.')[2].endswith('-attrib')]
    else:
        files = [f for f in files if not f.split('.')[2].endswith('-attrib')]

    print("Files after cleaning:", files)

    # for filename in files:
    #     print(filename)
    #
    #     # if combine_attributes:
    #     #     if not filename.split('.')[2].endswith('-attrib'):
    #     #         files.remove(filename)
    #     # else:
    #     #     # print(filename)
    #     if filename.split('.')[2].endswith('-attrib') or filename.split('.')[2].endswith('-pretty'):
    #         files.remove(filename)


    with open(f"{path}/{output_filename}", 'w', encoding='utf-8') as outfile:
        outfile.write('<head>')  # Initial head tag
        for filename in files:
            with open(f"{path}/{filename}", encoding='utf-8') as infile:
                content = infile.readlines()
                content[0] = content[0].replace('<head>', '\n')  # Delete initial head for each section
                content[-1] = content[-1].replace('</head>', '')  # Delete closing head for each section
                outfile.writelines(content)
        outfile.write('\n</head>')  # Closing head tag

    print(f"Combined XML files in {path} as {output_filename}.")

# def combine_XML(path, start_page = None, end_page = None):
#
#     complete_paragraphs = []
#     list_of_files = []
#
#     # Create a list of files in the directory whose name matches naming criteria.
#
#     list_of_files = [f for f in os.listdir(path) if f.startswith("VI") and f.endswith(".xml")]
#
#     # If no start page is given, set default at 0.
#     if start_page:
#         start_page = start_page - 1
#     else:
#         start_page = 0
#
#     # If no end page is given, set default to the end of the directory.
#     if end_page:
#         if end_page > len(list_of_files):
#             raise Exception(f"End page {end_page} is more than {len(list_of_files)} files in {path}.")
#     else:
#         end_page = len(list_of_files)
#
#     print(f"Start {start_page} to end {end_page} in {path}.")
#
#     for count in range(start_page, end_page):
#         file_name = list_of_files[count]
#
#         file_paragraphs = file_to_paragraphs(file_name, path)
#
#         complete_paragraphs.extend(file_paragraphs)
#
#     save_paragraphs_to_file(f"CGLOcombined{start_page + 1}to{end_page}", complete_paragraphs, path)

if __name__ == "__main__":
    # Run the script with arguments: -s <start page> -e <end page> -d <directory>
    # otherwise combine all XML files in default directory.
    parser = argparse.ArgumentParser()
    # parser.add_argument("-s", "--start", type=int)
    # parser.add_argument("-e", "--end", type=int)
    parser.add_argument("-d", "--directory")
    parser.add_argument("-a", "--attributes", action="store_true")
    args = parser.parse_args()

    if args.attributes:
        combine_attributes = True
        default_output_file = 'CGLO.99.combined-attrib.xml'
    else:
        combine_attributes = False

    if args.directory:
        path = args.directory
    else:
        path = DEFAULT_PATH

    combine_XML_files(path, DEFAULT_OUTPUT_FILE, combine_attributes)
