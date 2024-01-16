# Contains a SAX XML handler used for converting XML file into a list
# of lemmata and XREFS for display on the BAdW Publikationsserver.

from xml.sax import parse
from xml.sax import saxutils
from xml.sax.handler import ContentHandler
import re
import lxml.etree # for pretty_print function

# xml_file = "xml_output/VI.001.xml"

class xml_handler(ContentHandler):
    def __init__(self):
        super().__init__()
        self.lemma_stack = []
        self.current_content = ''

    @property
    def current_lemma(self):
        return self.lemma_stack[-1]

    def startElement(self, name, attrs):
        if name == "form":
            try:
                lang = attrs["lang"]
                type = attrs["type"]
                id = attrs["xml:id"]
            except:
                loc = self._locator
                line, col = loc.getLineNumber(), loc.getColumnNumber()
                print(f"Error reading form attributes at line {line}, col. {col}, page {self.current_location}")
                lang = ''
                type = ''
                id = ''

            self.lemma_stack.append({
                "lemma": "",
                "location": self.current_location,
                "x-refs": [],
                "lang": lang,  # Latinum, Graecum, etc.
                "id": id,  # id-string
                "type": type  # lemma, sublemma
            })
            self.current_content = ''

        if name == "ref":
            x_ref_target = parse_xref(attrs["cRef"])

            self.current_lemma["x-refs"].append(x_ref_target)

        if name == "pb":
            self.current_location = attrs["n"]

    def endElement(self, name):
        if name == 'form':  # delete \ before *, [, ] in lemma name:
            self.current_lemma["lemma"] = undo_escaped_chars(self.current_content)
            # delete newlines and tabs that occur in pretty-printed content, mainly around <emph> tags
            self.current_lemma["lemma"] = delete_extra_ws(self.current_lemma["lemma"])

    def characters(self, content):
        self.current_content += content

def parse_xref(xref_text):
    list = xref_text.split(".")
    return_text = '.'.join(list[1:])

    return return_text

# Deletes backslash before markdown escaped characters
def undo_escaped_chars(lemma):
    for old, new in [
        (r'\\\[', '['),
        (r'\\\]', ']'),
        (r'\\\*', '*')
    ]:
        lemma = re.sub(old, new, lemma)

    return lemma

def delete_extra_ws(lemma):
    lemma = lemma.replace('\n', '')
    lemma = re.sub(' {2,}', ' ', lemma).rstrip()
    return lemma


# Deletes sections of lemma text unimportant for word-to-word comparison: parentheses,
# angle brackets, and spaces.
def clean_lemma(lemma):
    # lemma = lemma.replace('V', 'u')
    lemma = lemma.lower()
    lemma = lemma.replace(' ', '')  # ignore spaces
    lemma = re.sub(r'[<>*]', '', lemma)  # ignore <>, *
    # lemma = re.sub(r'\[.+$\]', '', lemma) # delete anything in square brackets
    lemma = re.sub(r'\(.+\)', '', lemma)  # ignore parentheses

    return lemma


if __name__ == "__main__":
    with open(xml_file, "r", encoding="utf-8") as my_file:
        text = my_file.read()

    pretty_text = pretty_print_XML(text)

    with open(f'{xml_file}-pretty.xml', "w", encoding="utf-8") as my_file:
        my_file.write(pretty_text)

    # text = escape_sequences(text)
    # parseString(text, xml_handler())

    # handler = xml_handler()
    # parse(xml_file, handler)
    #
    # print(handler.current_lemma)
