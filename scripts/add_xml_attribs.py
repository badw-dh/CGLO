from lxml import etree
from pathlib import Path
import pretty_print
import os
import logging

BASE_PATH = Path(__file__).resolve().parent.parent
DEFAULT_PATH = BASE_PATH / "XML"
# filename = 'xml_output/CGLO.15.corr-I.xml'


# A dictionary for looking up section number with tuple for name, lingua
CGL_SECTIONS = {
    1: ('A', 'Latinum'),
    2: ('B', 'Latinum'),
    3: ('C', 'Latinum'),
    4: ('D', 'Latinum'),
    5: ('E', 'Latinum'),
    6: ('F', 'Latinum'),
    7: ('G', 'Latinum'),
    8: ('H', 'Latinum'),
    9: ('I', 'Latinum'),
    10: ('K', 'Latinum'),
    11: ('L', 'Latinum'),
    12: ('M', 'Latinum'),
    13: ('N', 'Latinum'),
    14: ('corr_II', 'incertum'),
    15: ('corr_I', 'incertum'),
    16: ('O', 'Latinum'),
    17: ('P', 'Latinum'),
    18: ('Q', 'Latinum'),
    19: ('R', 'Latinum'),
    20: ('S', 'Latinum'),
    21: ('T', 'Latinum'),
    22: ('U', 'Latinum'),
    23: ('V', 'Latinum'),
    24: ('XYZ', 'Latinum'),
    25: ('corr_III', 'incertum'),
    26: ('Graecolatinus', 'Graecum'),
    27: ('Anglosaxonicus', 'Anglosaxonicum'),
    28: ('Palaeotheodiscus', 'Palaeotheodiscum'),
    29: ('corr_IV', 'incertum')
}

logging.basicConfig(filename="logs/CGLO-xml.log", encoding='utf-8', filemode='w', level=logging.INFO)

def add_form_attribs(filename, index_part='A', language="Latinum"):

    # Lookup the filename in the CGL section dictionary for index_name and language.
    try:
        truncated_filename = os.path.split(filename)[1]
        prefix, section_number, index_part, suffix = truncated_filename.split('.')
        section_number = int(section_number)
        index_part, language = CGL_SECTIONS[section_number]
    except:
        print(f"Filename {filename} doesn't conform to CGLO naming conventions.")

    tree = etree.parse(filename)
    root = tree.getroot()

    class XMLNamespaces:
        xml = "http://www.w3.org/XML/1998/namespace"

    # print("Length:", len(root))

    # for element in root.iter():
    #     print(element.tag, element.text)

    form_count = 1  # Counter to give numbered id's to every form tag.

    logging.info(f"Adding XML attributes to {filename}")

    for paragraph in root.iter('entryFree'):
        main_lemma = paragraph.find('form')

        # Set attribute on main lemma
        if main_lemma is not None:
            main_lemma.set(etree.QName(XMLNamespaces.xml, 'id'),
                # f"Index-{index_part}{form_count}")
                f"{index_part}-{form_count}")
            if index_part.startswith('corr_'):  # corrigenda entries have to be corrected and lemma type assigned
                lemma_type = fix_corrigendum(main_lemma)
            else:  # elsewhere main lemmata are just called 'lemma'
                lemma_type = 'lemma'
            main_lemma.set('type', lemma_type)
            # print("Lemma type:", main_lemma.attrib['type'])
            main_lemma.set('lang', language)
            form_count += 1


            if main_lemma.text is None:
                page = main_lemma.xpath("preceding::pb[@n]")[-1].get("n")
                print(f"Main lemma with no text at page {page}, line {main_lemma.sourceline}")
            elif main_lemma.text[0].islower():
                if language == 'Latinum':  # only expect Latin lemmata to be uppercase
                    page = main_lemma.xpath("preceding::pb[@n]")[-1].get("n")
                    logging.info(f"Lower-case lemma ({main_lemma.text}) at page {page}, line {main_lemma.sourceline}?")


        else:
            logging.info(f"Error: no <form> tag in paragraph at line {paragraph.sourceline}")
            continue

        # print("Main lemma:", main_lemma)
        # print("Siblings:", main_lemma.itersiblings())
        for sibling in main_lemma.itersiblings():
            # print(f"We have a sibling at {main_lemma.sourceline}!", sibling.text)
            if sibling.tag == 'form':
                sibling.set(etree.QName(XMLNamespaces.xml, 'id'),
                    # f"Index-{index_part}{form_count}")
                    f"{index_part}-{form_count}")
                if index_part.startswith('corr_'):  # any sublemma (v. v. rare) in corrigenda gets labeled 'corrigendum'
                    lemma_type = 'corrigendum'
                else:  # elsewhere they are labeled 'sublemma'
                    lemma_type = 'sublemma'

                sibling.set('type', lemma_type)
                sibling.set('lang', language)
                form_count += 1

                # Check if the sublemma begins with an upper case character and report it.
                try:
                    if sibling.text[0].isupper():
                        page = sibling.xpath("preceding::pb[@n]")[-1].get("n")
                        logging.info(f"Upper-case sublemma ({sibling.text} at page {page}, line {sibling.sourceline})?")
                except:
                    logging.info(f"<form> tag with empty text at line {sibling.sourceline}")

    tree.write(f'{filename}', encoding='utf-8')
    print(f"Saved XML attributes to {filename}")
    # filename = filename.removesuffix('.xml')
    # tree.write(f'{filename}-attrib.xml', encoding='utf-8')
    # print(f"Saved XML attributes to {filename}-attrib.xml")


# Looks for definitions in each <entryFree> and adds numbered <def> tags.
# Not fully functional.
def split_definitions(filename):
    tree = etree.parse(filename)
    root = tree.getroot()
    paragraph = None
    def_count = 0
    # def_count = 1

    for form in root.findall(".//form"):
        # Check if this paragraph is different from the previous.
        if paragraph != form.getparent():
            paragraph = form.getparent()
            def_count = 0

        form_location = paragraph.index(form)
        num_siblings = len(paragraph)
        print("Form:", form.text)
        # siblings = form.itersiblings()
        # i = 0
        #
        # while i < num_siblings - form_location:
        #     sibling = siblings[i]
        #     if sibling.tag == 'form':
        #         # Create a new enclosing element.
        #         # new_def = etree.Element("def")
        #         # new_def.set('n', str(def_count))
        #         # paragraph.insert(def_count, new_def)
        #         new_def = etree.SubElement(paragraph, "def")
        #         new_def.set('n', str(def_count))
        #         # print("Segment:", parent[form_location:form_location+i+1])
        #         new_def[0:i+1] = paragraph[form_location:form_location+i+1]
        #         print(f"New_def {def_count}:", new_def)
        #         # new_def.append(parent[form_location:form_location+i])
        #         print(f"Final tag {sibling.text} at position {form_location} + {i}")
        #         def_count += 1
        #         break
        #     else:
        #         i += 1
        #
        # else:
        #     new_def = etree.SubElement(paragraph, "def")
        #     # new_def = etree.Element("def")
        #     new_def.set('n', str(def_count))
        #     # paragraph.insert(def_count, new_def)
        #     new_def[0:i+1] = paragraph[form_location:form_location+i+1]
        #     # new_def.append(parent[form_location:form_location+i])
        #     print(f"New_def {def_count}:", new_def)
        #     print("Final tag at end of div:", sibling.text)

        # Find the last relevant element before a new form.
        for i, sibling in enumerate(form.itersiblings()):
            if sibling.tag == 'form':
                # Create a new enclosing element.
                new_def = etree.Element("def")
                new_def.set('n', str(def_count + 1))
                paragraph.insert(def_count, new_def)
                # new_def = etree.SubElement(paragraph, "def")
                # new_def.set('n', str(def_count))
                # print("Segment:", parent[form_location:form_location+i+1])
                new_def[0:i+1] = paragraph[form_location + 1:form_location + i + 2]
                print(f"New_def {def_count} from location {form_location} to {form_location + i + 1}:", new_def)
                # new_def.append(parent[form_location:form_location+i])
                print(f"Enclosing tag {sibling.text}; form_location: {form_location}, sibling count: {i}, absolute position: {form_location + i + def_count + 1}")
                def_count += 1
                break
            # elif i == num_siblings - form_location - 1:
            #     new_def = etree.SubElement(paragraph, "def")
            #     # new_def = etree.Element("def")
            #     new_def.set('n', str(def_count))
            #     # paragraph.insert(def_count, new_def)
            #     new_def[0:i+1] = paragraph[form_location:form_location+i+1]
            #     # new_def.append(parent[form_location:form_location+i])
            #     print(f"New_def {def_count}:", new_def)
            #     print("Final tag at end of div:", sibling.text)
        else:  # We've reached the end of the paragraph without an adjacent <form>
            # new_def = etree.SubElement(paragraph, "def")
            new_def = etree.Element("def")
            new_def.set('n', str(def_count + 1))
            paragraph.insert(def_count, new_def)
            new_def[0:i+2] = paragraph[form_location + 1 :form_location+i+3]
            # new_def.append(parent[form_location:form_location+i])
            print(f"New_def {def_count}:", new_def)
            print(f"Enclosing tag {sibling.text} at end of div; location form_location: {form_location}, sibling count: {i}, absolute position: {form_location + i + 1}")


    filename = filename.removesuffix('.xml')
    tree.write(f'{filename}-defs.xml', encoding='utf-8')

def add_attribs_to_dir(path):
    for filename in os.listdir(path):
        try:
            prefix, number, name, extension = filename.split('.')
        except:
            print(f"Filename {filename} in {path} doesn't conform to CGLO filename conventions.")

        if name.endswith('-attrib') or name.endswith('-pretty') or name == "combined":
            continue

        print("Adding attributes to:", filename)
        add_form_attribs(f"{path}/{filename}", name)
        # filename = filename.removesuffix('.xml')
        # pretty_print.prettify_file(f"{path}/{filename}-attrib.xml")
        pretty_print.prettify_file(f"{path}/{filename}")
        # print("Pretty printed.")
    print("Done with attributes.")


# Takes a corrigendum lemma, determines its type, cleans up any features of the name
# and returns the lemma_type: corrigendum, addendum, delendum
def fix_corrigendum(main_lemma):
    # If the preceding <entryFree> element contains "adde" we have an addendum, "dele" for delendum
    # Label addenda lemmata with [ADD]
    # otherwise a corrigendum, which should have a closing ]
    lemma_type = 'corrigendum'

    previous_sibling = main_lemma.getprevious()  # should give us the <entryFree>

    if previous_sibling is not None:
        previous_sibling_text = previous_sibling.text or ''
    else:
        previous_sibling_text = ''

    if previous_sibling_text.startswith('Adde'):
        lemma_type = 'addendum'
        # Commented text adds [ADD] to lemma
        # if main_lemma.text.endswith('[ADD]'):
        #     pass
        # else:
        #     main_lemma.text += ' [ADD]'

    elif previous_sibling_text.startswith('Dele'):
        lemma_type = 'delendum'
        # if main_lemma.text[0] == '[' and main_lemma.text[-1] == ']':
        #     pass
        # else:
        #     main_lemma.text = '[' + main_lemma.text + ']'

    else:  # a normal corrigendum so check if it ends with ']'
        pass
        # if main_lemma.text[-1] == ']':
        #     pass
        # else:
        #     main_lemma.text += ']'

    return lemma_type

if __name__ == "__main__":

    add_attribs_to_dir(DEFAULT_PATH)
    # add_form_attribs(filename)
    # split_definitions(filename)
    # add_form_attribs("CGLO.14.corr-II.xml")
    # pretty_print.prettify_file(f"{filename.removesuffix('.xml')}-defs.xml")
