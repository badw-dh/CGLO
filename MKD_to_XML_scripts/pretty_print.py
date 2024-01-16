from lxml import etree

filename = 'xml_output/CGLO.01.A-attrib.xml'

# INLINE_TAGS = ['form', 'emph', 'ref', 'def', 'xr']


# Calls indent_lxml() on a filename.
def prettify_file(filename):
    tree = etree.parse(filename)
    root = tree.getroot()

    indent_lxml(root)

    # filename = filename.removesuffix('.xml')
    tree.write(f'{filename}', encoding='utf-8')
    print(f"Prettified {filename}")


# Recursively indents an XML file starting from root.
# To do: put <pb> tags on isolated newlines?
# Simpler implementation: search and replace by tag name.
def indent_lxml(element: etree.Element, level: int = 0, is_last_child: bool = True, is_in_entryFree = False) -> None:
    space = "  "
    indent_str = "\n" + level * space

    element.text = strip_or_null(element.text)
    # if element.text:
    #     element.text = f"{indent_str}{space}{element.text}"

    num_children = len(element)
    if num_children:
        if element.tag == 'entryFree':
            is_in_entryFree = True

        element.text = f"{element.text or ''}{indent_str}{space}"

        for index, child in enumerate(element.iterchildren()):
            is_last = index == num_children - 1
            indent_lxml(child, level + 1, is_last, is_in_entryFree)


    # elif element.text:
    #     element.text += indent_str

    tail_level = max(0, level - 1) if is_last_child else level
    tail_indent = "\n" + tail_level * space

    tail = strip_newline(element.tail)

    if is_in_entryFree == True and element.tag != 'entryFree':
        if is_last_child:
            element.tail = f"{tail}{tail_indent}" if tail else tail_indent
            return

        # else:
        #     element.tail = tail

        next_sibling = element.getnext()

        if next_sibling is not None:
            if next_sibling.tag == 'form':
                 element.tail = f"{tail}{tail_indent}" if tail else tail_indent
                 return

            # if next_sibling.tag == 'pb':
            #     element.tail = f"{tail}\n" if tail else "\n"
            #     return

        element.tail = tail

    else:
        element.tail = f"{indent_str}{tail}{tail_indent}" if tail else tail_indent

def strip_newline(text):
    if text is not None:
        return text.replace('\n', '') or None

def strip_or_null(text) -> str:
    if text is not None:
        return text.strip() or None

if __name__ == "__main__":
    prettify_file(filename)
