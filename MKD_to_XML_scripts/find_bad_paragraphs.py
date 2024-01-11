from mkd_to_xml import *
import re, os

input_path = 'mkd_combined'
# file_list = ["CGLO.01.A.mkd", "CGLO.02.B.mkd", "CGLO.03.C.mkd"]

def check_file_for_bad_paragraphs(filename):
     paragraphs = file_to_paragraphs(filename, input_path)
     print("Checking for bad paragraphs:", filename)

     current_page = 'VI.000'

     for paragraph in paragraphs:
         # update page
         match = re.search(r'<pb n="(.*?)"', paragraph)
         if match:
             current_page = match.group(1)

         # Delete pb and div tags
         paragraph = re.sub(r'<pb.*?</pb>', '', paragraph)
         paragraph = re.sub(r'<div.*?>', '', paragraph)
         paragraph = paragraph.lstrip()
         if not paragraph.startswith('**'):
             print(f"{current_page} has paragraph without initial lemma:", paragraph[:50])

if __name__ == "__main__":
    file_list = [filename for filename in os.listdir(input_path) if filename.endswith('.mkd')]

    for filename in file_list:
        check_file_for_bad_paragraphs(filename)
