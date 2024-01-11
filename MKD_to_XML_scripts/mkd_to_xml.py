# System library imports
import os, re, logging

# Project imports
from tag_CGL_xrefs import tag_CGL_refs_new  # new xref function
from identify_gloss import *  # for looking up short names
from combine_xml import combine_XML_files
# from tag_lemma_refs import tag_lemma_refs  # to tag <xr> xrefs to named lemmata
from roman_to_arabic import arab_rom, rom_arab
from pretty_print import prettify_file

# from bs4 import BeautifulSoup # For pretty printing XML
# from bs4.builder import LXMLTreeBuilderForXML # For pretty printing XML, lxml module must also be installed

# Takes a markdown file and transforms to basic XML. Intended now for use on 'sections' (i.e. letters of alphabet)
# rather than individual pages.
def process_file(file_name, input_path, output_path):
    list_of_paragraphs = file_to_paragraphs(file_name, input_path)
    # print(f"There are {len(list_of_paragraphs)} paragraphs in the file {file_name}.")
    logging.warning(f"Processing {file_name}")  # add name of file to log

    # Add XML tags to each paragraph
    for i, paragraph in enumerate(list_of_paragraphs):
        # paragraph = escape_characters(paragraph)
        # paragraph = tag_forms(paragraph)
        # paragraph = tag_italics(paragraph)
        # paragraph = tag_CGL_refs_new(paragraph)
        # # paragraph = tag_lemma_refs(paragraph)
        # paragraph = wrap_paragraph(paragraph)

        paragraph = xmlize_paragraph(paragraph)
        list_of_paragraphs[i] = paragraph

    # Add pb tag to the text of first paragraph.
    # list_of_paragraphs[0] = pb_tag(file_name) + list_of_paragraphs[0]

    # Wrap the file with <head> and whatever other tags are necessary.
    list_of_paragraphs[0] = '<head>' + list_of_paragraphs[0]
    list_of_paragraphs[-1] = list_of_paragraphs[-1] + '</head>'

    xml_file = save_paragraphs_to_XML_file(file_name, list_of_paragraphs, output_path)
    # prettify_file(xml_file)

# Take a paragraph of continuous mkd text and convert to XML.
def xmlize_paragraph(paragraph):
        paragraph = escape_characters(paragraph)
        paragraph = tag_forms(paragraph)
        paragraph = tag_italics(paragraph)
        paragraph = tag_CGL_refs_new(paragraph)
        # paragraph = tag_lemma_refs(paragraph)
        paragraph = wrap_paragraph(paragraph)

        return paragraph

# Takes all .mkd files in input_path and saves them to output_path.
def generate_XML_from_dir(input_path, output_path):
    file_list = [f for f in os.listdir(input_path) if f.endswith('.mkd')]

    for filename in file_list:
        try:
            section_prefix, section_number, section_name, extension = filename.split('.')
            section_number = int(section_number)
        except:
            print(f"File {filename} in {input_path} doesn't follow naming conventions.")

        # If we need to process certain sections separately:
        # if section_number in [14, 15, 24,  28]:  # corrigenda files
        #     process_corrigenda(file_name, input_path, output_path)
        # elif section_number == 25:  # Graeco-Latinus
        #     process_Graeco-Latinus(file_name, input_path, output_path)
        # elif section_number == 26:
        #     process_Anglosaxonicus(file_name, input_path, output_path)
        # elif section_number == 27:
        #     process_Palaeotheodiscus(file_name, input_path, output_path)
        # elif section_number == 99:  # skip combined MKD file
        #     continue
        # else:  # the rest are normal Latino-Graecus alphabetic sections
        #     process_file(file_name, input_path, output_path)

        print(f"Turning {filename} into XML.")
        process_file(filename, input_path, output_path)

    try:
        combine_XML_files(output_path)
    except Exception as e:
        raise

# Takes a file name as argument and returns a list containing
# each indented paragraph.
def file_to_paragraphs(file_name, input_path):
    with open(f"{input_path}/{file_name}", 'r', encoding='utf-8') as file:
        text = file.read()

        # Split the text file into a list by looking for empty newlines.
        list_of_paragraphs = text.split('\n\n')

        # Replace every newline within each paragraph with a space EXCEPT after XML tag </pb>
        for i, paragraph in enumerate(list_of_paragraphs):
            # list_of_paragraphs[i] = re.sub(r'(?<!</pb>)\n', ' ', paragraph)
            list_of_paragraphs[i] = re.sub(r'</pb>\n', '</pb>', paragraph)
            list_of_paragraphs[i] = paragraph.replace('\n', ' ')
        return list_of_paragraphs

# Save a list of paragraphs to a file
def save_paragraphs_to_XML_file(file_name, list_of_paragraphs, output_path):

    # If the filename ends with ".mkd" delete this suffix.

    file_name = file_name.removesuffix(".mkd")
    # if file_name.endswith(".mkd"):
    #    file_name. = file_name[:-4]

    output_file = f"{output_path}/{file_name}.xml"

    with open(output_file, "w", encoding="utf-8") as f:
        paragraph_string = "\n\n".join(list_of_paragraphs)

        # paragraph_string = pretty_print_XML(paragraph_string)
        f.write(paragraph_string)

        # print(f"Saved {file_name}")
    return output_file

# Replace **lemma** with <form>lemma</form>.
def tag_forms(text):
    return re.sub(r"(?<!\\)\*\*(.+?)(?<!\\)\*\*", r"<form>\1</form>", text)

# Replace *italics* with <emph>italics</emph>
def tag_italics(text):
    pattern = r"(?<!\\)\*(.*?)(?<!\\)\*"
    for m in re.finditer(pattern, text):
        if '<form' in m.group(1) or '</form>' in m.group(1):  # don't add <emph> if <form> is already inside!
            continue
        else:
            emph_tag = f'<emph>{m.group(1)}</emph>'
            text = text.replace(m.group(), emph_tag)

    # return re.sub(r"(?<!\\)\*(.*?)(?<!\\)\*", r"<emph>\1</emph>", text)
    return text

# Wrap a paragraph with <div><entryFree> ... </entryFree></div>"
# HACK: currently after mkd files are combined into sections of the alphabet
# there is are <head> and </head> tags at the very beginning and end.
# These need special treatment so that the <div><entryFree> are placed
# correctly.
def wrap_paragraph(text):
    # Delete trailing space.
    text = text.strip()

    if text == "":
        # There is a blank line so just return it.
        return text

    elif text != "":
        # There is some text. If it's the very first paragraph in a section
        # we need to ignore the pre-existing tags (<div type="..."> and potentially <pb ...>>)
        if text.startswith('<div type'):
            partitioned = text.partition('</pb>')  # Partition the text after the pb tag.
            text = partitioned[0] + partitioned[1] + '\n<entryFree>' + partitioned[2] + '</entryFree>'
            # print("Partitioned text:", partitioned[2])
            return text

        # elif text.startswith('</div>'):
            # If it's the last paragraph in a section we have to put the <div> tags
            # before the enclosing <div>
            ## text = re.sub(r'</div>', r'</entryFree></div></div>', text)
            ## text = "<div><entryFree>" + text
            # return text
        elif text.strip().endswith('</div>'):  # paragraph ends with a section </div>
            partitioned = text.partition('</div>')
            text = '<entryFree>' + partitioned[0] + '</entryFree>' + '\n</div>'
            return text
        else:
            return f"<entryFree>{text}</entryFree>"




# Add framing XML tags to page: <body>. Others, e.g. <TEI> may eventually be necessary.
def wrap_page(text):
    result = "<body>" + text + "</body>"
    return result

# Wraps a larger section of text (letters of alphabet). Called when the MKD section
# files are combined.
# HACK: The <head></head> tags at beginning and end cause problems for wrap_paragraph
# function below. Newlines are necessary so that it can be treated separately
# is not wrapped by </entryFree></head>.
def wrap_section(list_of_lines, name, type="section"):
    list_of_lines.insert(0, f'<div type="{type}" xml:id="{name}">')
    list_of_lines.append('</div>')
    return list_of_lines


# Extracts volume and page numbers from a filename.
# Most files named e.g. VI.032.mkd, preface files are named e.g. VI.praef_09
# and sometimes individual pages are split across two files, e.g. VI.159a.mkd, VI.159b.mkd
def extract_page_number(file_name):

    split_name = file_name.split('.')

    volume = split_name[0]
    page = split_name[1]

    if page.startswith('praef_'):
        page_Arabic = int(page.split('praef_')[1])
        page_Roman = arab_rom(page_Arabic)
        page = 'praef_' + page_Roman
    else:
        page = str(int(page.rstrip('abc')))

    return volume, page


# Function to add <pb> tag with attributes to a text
def pb_tag(file_name):

    volume_Roman, page = extract_page_number(file_name)
    volume_Arabic = rom_arab(volume_Roman)

    if page.startswith('praef_'):
        page_Roman = page.split('praef_')[1]
        page_Arabic = rom_arab(page_Roman)
        return f'<pb n="{volume_Roman}.praef_{page_Roman}" facs="{volume_Arabic}_praef.{page_Arabic}.jpg"></pb>\n'
    else:
        return f'<pb n="{volume_Roman}.{page}" facs="{volume_Arabic}.{page}.jpg"></pb>\n'


# Converts 5 special characters to XML escape code.
def escape_characters(paragraph):
    ESCAPE_CODES = [
        (r"\\<", r"&lt;"),
        (r"\\>", r"&gt;"),
        (r'"', r"&quot;"),
        (r"'", r"&apos;"),
        (r"&", r"&amp;")
    ]

    fixed_paragraph = paragraph

    # Delete all XML tags to avoid escaping quotation marks inside brackets.
    cleaned_paragraph = re.sub(r"(?<!\\)<.*?>(?!\\)", "", paragraph)

    for regex, replacement in ESCAPE_CODES:
        matches = re.finditer(regex, cleaned_paragraph)

        for match in matches:
            fixed_paragraph = re.sub(regex, replacement, fixed_paragraph)

    return fixed_paragraph


# OLD tag XML functions kept for testing purposes
def tag_CGL_refs(text):
    # search_string = r"(I|II|III|IV|V|VI|VII) (\d+), (\d+)(/\d+)?"
    # search_string = r"(?<!emph> )(I|II|III|IV|V|VI|VII) (\d+), (\d+)(\/\d+)?"  # Converts *Isid.* VII 13, 5 to </emph> V<ref cRef="II.13.5">
    search_string = r"(?<!emph>) (I|II|III|IV|V|VI|VII) (\d+), (\d+)(\/\d+)?"
    # NB: the space is captured before the Roman numeral; needs to be deleted and placed before <ref> tag later.
    # TODO: valid xref's are sometimes deleted, e.g. "*Plac.* V 554, 44"

    search_string_preface = r'(I|II|III|IV|V|VI|VII) p\. (XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?(\.|;)'

    match_list = re.finditer(search_string, text)
    match_list_preface = re.finditer(search_string_preface, text)

    # if x := re.search(search_string_preface, text):
    #     logging.info(f"XREF TO PREFACE: {x.group()}")

    # Convert all ordinary xrefs.
    for match in match_list:
        # Initialize some variables.
        matched_string = match.group()
        matched_volume = match.group(1)
        matched_page = match.group(2)

        if match.group(4):  # for refs like "IV 54, 32/33"
            matched_line = match.group(3) + match.group(4)
        else:
            matched_line = match.group(3)


        sub_refs = []

        # Get the text in the paragraph following the match.
        text_following_match = text.partition(matched_string)[2]

        # If the text before the most recent full stop is "GR. L.</emph>" or "Isid." discard.
        text_before_match = text.partition(matched_string)[0]
        try:
            text_before_previous_dot = text_before_match.split('.')[-2]
            if text_before_previous_dot.endswith(' p'):  # if the text ends with " p. " (e.g. II p. XI; III 34, 3) step back one dot
                text_before_previous_dot = text_before_match.split('.')[-3]
            if text_before_previous_dot.endswith((" L", "Isid")):
                if ")" in text_before_match.split('.')[-1] or "<form>" in text_before_match.split('.')[-1]:
                    # if there's a closing bracket or new lemma between "GR. L." and the xref, discorard
                    pass
                else:
                    print("Discarded xref", matched_string)
                    continue
        except:
            pass

        # Ignore parentheses, italics, and pb tags.
        clean_text_following_match = re.sub(r" \(.+?\)", "", text_following_match)
        clean_text_following_match = re.sub(r"<emph.+?</emph>", "", clean_text_following_match)
        clean_text_following_match = re.sub(r"<pb.+?</pb>", "", clean_text_following_match)
        # clean_text_following_match = text_following_match

        # if clean_text_following_match != text_following_match:
        #    print("Parenthesis detected in xref string:", text_following_match, "\n-->", clean_text_following_match)

        # Check if there is a colon immediately after.
        if clean_text_following_match.startswith(";"):
            # Strip the leading semicolon.
            clean_text_following_match = clean_text_following_match.removeprefix(";")

            # Take only the part of the string before the first "." or next <form>
            # TODO: what if . is part of "praef."?
            clean_text_following_match = clean_text_following_match.split(".")[0]
            clean_text_following_match = clean_text_following_match.split("<form")[0]

            # Divide the text into sub-strings separated by semicolon.
            for sub_string in clean_text_following_match.split(";"):

                # Check if the sub-ref is a complete CGL xref starting with a
                # Roman numeral. If so, it has already been found and we can
                # ignore it.
                sub_string = sub_string.strip()
                if re.search(search_string, sub_string):
                    continue

                # Call a function to process the partial xrefs.
                tagged_partial_ref = tag_partial_refs(sub_string, matched_volume)
                if tagged_partial_ref:
                    # Assemble a list of tuples containing pairs of pre-tagged and post-tagged
                    # strings for later replacement.
                    sub_refs.append(tagged_partial_ref)
                else:
                    continue

        # Get the short abbreviation of the ref to be added with <addName> attribute.
        # Probably there are xref's throwing up errors. Handle them!
        xref = f'{matched_volume} {matched_page}, {matched_line}'
        xref = f"{matched_volume} {matched_page}, {matched_line}"
        short_name = identify_gloss_from_xref(xref)


        # Alternate format for <bibl> tag:
        # formatted_xref = f"<bibl type=\"CGL\"><citedRange unit=\"volume\">"\
        # f"{match.group(1)}</citedRange><citedRange unit=\"page\">"\
        # f"{match.group(2)}</citedRange><citedRange unit=\"line\">"\
        # f"{match.group(3)}</citedRange></bibl>"

        # formatted_xref = f" <ref cRef=\"CGL.{matched_volume}.{matched_page}.{matched_line}\">{match.group().strip()}</ref>"
        formatted_xref = f" <ref addName=\"{short_name}\" cRef=\"CGL.{matched_volume}.{matched_page}.{matched_line}\">{match.group().strip()}</ref>"
        # NB: space needs to be deleted from beginning of match.group() and placed before <ref>

        # First replace the complete reference in the match with the correct string.
        # print(f"MAIN XREF: Replacing {match.group()} with {formatted_xref}")
        text = text.replace(match.group(), formatted_xref)

        # Next replace any partial sub-references after the match.
        for tuple_match in sub_refs:
            # print(f"PARTIAL XREF: Replacing {tuple_match[0]} with {tuple_match[1]}")
            text = text.replace(tuple_match[0], tuple_match[1])

    # Convert xrefs that refer to prefatory pages.
    for match in match_list_preface:
        # Initialize some variables.
        matched_list = match.groups()
        matched_string = match.group()
        matched_volume = match.group(1)
        matched_Roman_page = ''.join(matched_list[1:-1])
        divider = matched_list[-1]
        # print(match.groups(), matched_volume, matched_Roman_page, divider)

        # Adjust matched_string: delete beginning space and remove trailing divider.
        fixed_matched_string = matched_string.strip()

        formatted_xref = f"<ref cRef=\"CGL.{matched_volume}.praef_{matched_Roman_page}\">{fixed_matched_string}</ref>{divider}"

        # Simple case when xref followed by dot.
        if divider == '.':
            text = text.replace(matched_string, formatted_xref)
            # logging.info(f"XREF TO PREFACE: {formatted_xref}")

        # The xref followed by more xrefs
        elif divider == ';':
            text_following_match = text.partition(matched_string)[2]

            text_following_match = text_following_match.split('.')[0]
            text_following_match = text_following_match.split('<form')[0]
            text_following_match = text_following_match.split('<ref')[0]

            for sub_string in text_following_match.split("; "):
                if re.search(search_string, sub_string):
                    continue
                else:
                    # Call a function to process the partial xrefs.
                    tagged_partial_ref = tag_partial_refs(sub_string, matched_volume)
                    if tagged_partial_ref:
                        # Assemble a list of tuples containing pairs of pre-tagged and post-tagged
                        # strings for later replacement.
                        sub_refs.append(tagged_partial_ref)
                        # print("Tagged partial ref:", tagged_partial_ref)
                    else:
                        continue

            # First replace the initial xref
            text = text.replace(matched_string, formatted_xref)

            # Next replace any partial sub-references after the match.
            for tuple_match in sub_refs:
                # print(f"PARTIAL XREF: Replacing {tuple_match[0]} with {tuple_match[1]}")
                text = text.replace(tuple_match[0], tuple_match[1])

    return text

# Tags CGL x-refs that are incomplete, i.e. the volume number is implicit
# since it follows a semicolon.
def tag_partial_refs(sub_string, matched_volume, format = "ref"):
    # A regex search string to find the sequence [page #], [line #]
    # search_string = r"([0-9]|[1-9][0-9]|[1-9][0-9][0-9]), ([0-9]|[1-9][0-9])\b"
    search_string = r"(\d+), (\d+)(\/\d+)?"

    match = re.search(search_string, sub_string)

    if match:
        # Then there is a line followed by a forward slash combine both elements.
        if match.group(3):
            matched_line = match.group(2) + match.group(3)
            # print("Sub-group:", matched_line)
        else:
            matched_line = match.group(2)

        # Check the format argument and use <bibl> or <ref> tags accordingly.
        if format == "bibl":
            replace_string = f"<bibl type=\"CGL\"><citedRange unit=\"page\">"\
            f"{match.group(1)}</citedRange><citedRange unit=\"line\">"\
            f"{match.group(2)}</citedRange></bibl>"
        else:
            replace_string = f"<ref cRef=\"CGL.{matched_volume}.{match.group(1)}.{matched_line}\">{match.group()}</ref>"

        # Replace with the appropriate XML tags.
        tagged_sub_string = sub_string.replace(match.group(), replace_string)

        # Return a tuple containing the original text and the replacement text.
        return (match.group(), replace_string)
    else:
        return []
