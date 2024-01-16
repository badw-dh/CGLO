# Not fully implemented.
# Finds cross-refs to other lemmata in the Thes. gloss. and transforms
# them to correct XML tags, e.g. <xr target="#Index-B11">Babylon</xr>
# Lemma references begin with <emph>v.</emph> or <emph>V.</emph>
    # sometimes cross-references occur in parentheses in the middle of an entry.
    # sometimes cross-refs to multiple words are separated by commas (or *vel*, *et*).
    # sometimes a cross-ref. to a single word is followed by smthg else in italics
    # xref list usually terminated with full stop, sometime with comma, sometimes italic phrase, sometimes closing parenthesis or square bracket.
    # If a dot has been mistakenly replaced by comma, then bold may follow.

# TODO: parse paragraphs after xrefs have been identified but before finally saved as XML.
# Leave XML target tag blank. Fill the target in at a later stage of processing.
# TODO: bolded form tags are not currently put in xrefs, even when they are xrefs.
# e.g. "*V.* anes, **anitas**."

import re
# from mkd_to_xml import xmlize_paragraph


# Main function: takes a paragraph of partly tagged MKD text and adds <xr> tags to
# named lemmata.
def tag_lemma_refs(paragraph):
    tokens = tokenize_lemma_refs(paragraph)
    tagged_tokens = tag_lemma_tokens(tokens)
    output = tokens_to_text(tagged_tokens)

    return output

def tokenize_lemma_refs(paragraph):
    TOKENS = [
        ('VIDE', r"(?P<VIDE><emph>[vV]\.</emph>) "),
#       ('FULL_STOP', r"(?P<FULL_STOP>\.)(?!,| .{1,10},)"),
        ('FULL_STOP', r"(?P<FULL_STOP>(?<! \w)\.(?= |<|$))"),
        ('COMMA', r"(?P<COMMA>, )"),
        ('SEMICOLON',  r"(?P<SEMICOLON>(?<!&lt|&gt|uot|pos|amp); )"),
        ('KLAMMER', r'(?P<KLAMMER>\(.+?\))'),
    #    ('END_SQUARE_BRACKET', r"(?P<END_SQUARE_BRACKET>\])"),
        ('VEL_OR_ET', r"(?P<VEL_OR_ET><emph> *(vel|et) *</emph>)"),
        ('EMPH_TAG', r"(?P<EMPH_TAG><emph>.+?</emph>)"),  # excludes *vel* or *et*
        ('FORM_TAG', "(?P<FORM_TAG><form.+?</form>)"),
        ('ROMAN_NUM', "(?P<ROMAN_NUM>[IVX] )"),
    #    ('ARAB_NUM',  r'(?P<ARAB_NUM>\d)'),
        ('XREF_TAG', r'(?P<XREF_TAG><ref.+?</ref>)')
    ]

    regex = re.compile('|'.join([pattern for name, pattern in TOKENS]))
    tokens = []
    i = 0
    for m in regex.finditer(paragraph):
        begin, end = m.span()

        if i != begin:  # there is an unmatched gap to tokenize as WP or TEXT
            if paragraph[i:begin].isspace():
                tokens.append(('WS', paragraph[i:begin], m.span()))
            else:
                tokens.append(('TEXT', paragraph[i:begin], m.span()))

        for name in [name for name, pattern in TOKENS]:
            if m.group(name) != None:
                token_type = name
                break

        tokens.append((token_type, m.group(), m.span()))
        i = end

    # append any unmatched tail in the paragraph
    # print("Length of paragraph:", len(paragraph), "i:", i, "last char:", paragraph[i:])
    if i <= (len(paragraph) - 1) or i == 0:  # if i == 0, the content consists of a single unmatched character, e.g. '!'
        if paragraph[i:].isspace():
            tokens.append(('WS', paragraph[i:], (i, len(paragraph) - 1)))
        else:
            tokens.append(('TEXT', paragraph[i:], (i, len(paragraph) - 1)))

    return tokens


# def tag_lemma_refs(paragraph):  # input is a paragraph of text
#     # vide = re.compile(r"<emph>[vV]\.</emph>")
#     vide = re.compile(r"<emph>[vV]\.</emph>")
#     TERMINATORS = [r"\.(?!,| .{1,10},)", r";", r"\)", r"\]", r"<emph>(?!(vel</emph>|et</emph>|\s))", "<form", "[IVX] ", r'\d', r'\n', '<ref']
#     # TERMINATORS = [r"\.(?!,| .{1,10},)", r";", r"\)", r"\]", r"\*(?!(vel\*|et\*|\s))", r"\*\*", "[IVX] ", r'\d', '\n']
#     terminator = re.compile('|'.join(TERMINATORS))
#     tagged_paragraph = paragraph
#
#     # Test TERMINATORS
#     # print("Terminators:", TERMINATORS)
#     # print("Joined terminators:", '|'.join(TERMINATORS))
#     # test_terminator = re.compile(r";")
#     # print(test_terminator.match("This is a sentence with ; in the middle"))
#
#     matches = vide.finditer(paragraph)
#
#     # Split paragraph into substrings beginning with the end of each match and continuing
#     # to a valid terminator. If no valid terminator is found, make sure to end before
#     # the beginning of the next match.
#
#     for match in matches:
#         substring = paragraph[match.end():]
#
#         next_terminator = terminator.search(substring)
#         if next_terminator:
#             next_terminator_pos = next_terminator.start()
#             # print("Terminator found:", next_terminator.group())
#         else:
#             next_terminator_pos = -1
#         substring = substring[:next_terminator_pos]
#         # print("Substring:", substring)
#
#         substring = re.sub(r"<emph>(vel|et)</emph>", ",", substring)  # replace *vel* and *et* with commas
#         # substring = re.sub(r"\*(vel|et)\*", ",", substring)  # replace *vel* and *et* with commas
#
#         lemma_refs = substring.split(',')
#
#         for lemma_ref in lemma_refs:
#             lemma_ref = lemma_ref.strip()
#             if lemma_ref == '':
#                 continue
#             lemma_ref_XML = f'<xr target="">{lemma_ref}</xr>'
#             # print(f"Lemma_ref: {lemma_ref}, XML: {lemma_ref_XML}")
#             tagged_paragraph = tagged_paragraph.replace(lemma_ref, lemma_ref_XML)
#
#     return tagged_paragraph


# Take a list of tokens and tag the named lemma xrefs (leaving the target open for later filling).
def tag_lemma_tokens(tagged_paragraph):
    tagged_tokens = []

    i = 0
    in_vide_sequence = False

    while i < len(tagged_paragraph):
        name, content, span = tagged_paragraph[i]
        pass_tokens = ['COMMA', 'VEL_OR_ET', 'FORM_TAG']  # don't break out of a vide-sequence if these tokens intervene

        if name == 'VIDE':
            in_vide_sequence = True

        elif name == 'TEXT':
            if in_vide_sequence:
                # next_token = tagged_paragraph[i + 1]
                # next_name = next_token[0]
                # end_of_vide_sequence = next_name not in pass_tokens
                content = tag_lemma_ref(content)

        elif name in pass_tokens:
            pass

        elif name == 'EMPH_TAG':
            # If next token is a comma, pass; otherwise break out of the vide_sequence.
            try:
                next_token_name = tagged_paragraph[i + 1][0]
            except:
                next_token_name = None

            if next_token_name == 'COMMA':
                pass
            else:
                in_vide_sequence = False

        elif name == 'KLAMMER':
            tokenized_klammer = tokenize_lemma_refs(content[1:-1])  # exclude opening and closing brackets
            tagged_klammer = tag_lemma_tokens(tokenized_klammer)
            klammer_text = tokens_to_text(tagged_klammer)
            content = '(' + klammer_text + ')'

        else:
            in_vide_sequence = False

        tagged_tokens.append((name, content, span))
        i += 1

    return tagged_tokens


# Return an XML tagged lemma-xref.
def tag_lemma_ref(content):
    # strip a blank space before the content and a period at the end
    # print("Tag content:", content)

    leading_space = ''
    tail = ''

    if content.endswith('</div>'):
        tail = '</div>'
        content = content.rstrip('</div>')
        print("Content stripped of </div>:", content, ".")

    if content[0] == ' ':  # strip leading space but remember to add it later
        content = content[1:]
        leading_space = ' '

    # if content.endswith('</entryFree>'):  # probably only relevant in the test data
    #     content = content.rstrip('</entryFree>')
    #     tail = '</entryFree>'

    if content[-1] == '.':  # strip closing dot (unless an abbreviating dot!) but remember to add it later
        if not ends_with_abbreviation(content):
            tail = content[-1] + tail
            content = content[:-1]

    elif content[-1] == ' ':
        content = content[:-1]
        tail = ' ' + tail

    if content.isnumeric():  # if it's simply an integer, do not tag!
        return f"{leading_space}{content}{tail}"

    content = f"{leading_space}<xr>{content}</xr>{tail}"

    return content


# returns True if the string ends with an abbreviated word
def ends_with_abbreviation(text):
    if re.search(r' [a-zA-Z]\.$', text):
        return True
    else:
        return False

# Takes a list of tokens and converts to string.
def tokens_to_text(tokens):
    text = ''
    for name, content, span in tokens:
        text += content

    return text


if __name__ == "__main__":
    test_lines = [
        "559, 3. ὑπεναντίοι pluraliter II 559, 4. *V.* aduores, contrarius.",
        "**aduertere** intelligere IV 9, 20. *V.* aduorti hercle animum.",
        "conuocat IV 484, 9. **aduocentur** ἐπασχολοῦνται II 10, 3 (*v.* auoco).",
        "**Aeramen** χάλκωμα III 93, 69. *V.* aeris flos, aerosus, aerugo, aes ustum, flos aeraminis.",
        "**Aeuus** eiusdem aetatis, par IV 306, 29. *V.* coaeuus *et* aequaeuus.",
        "*V.* adoria *sub fin.*, adorium, affaber.",
        "[inpiger] V 264, 10 (*v.* 8). **adlisum** adlositum IV 304, 22)",
        "oberrare (ab.?) V 642, 39 (*Non.* 121, 19). *V.* futura alucinatus, V *praef.* V. *Cf. Martian. Gap. p.* 167",
        "*V.* anclena, *AHD. GL.* III 123, 58; 222, 20; 633, 49.",
        "blah (*v.* *d. Vliet Arch.* IX 302) blah.",
        "*V.* anes, **anitas**.",  # form not currently recognized as xr
        "Virg. Georgicon lib. III (*v.* 80)",
        "blah (blah; *v.* **arma** unius hominis).",  # This is a valid ref. to lemma "arma" with definition "unius hominis". TODO: not currently understood!
        "blah (*v.* axilla *et Isid.* XI 1, 65).",  # followed by *et ...* but not another lemma
        "*V.* ependyten, melos 2.",  # lemma followed by Arabic numeral
        "*V.* alta mente, in m. est, i. m. habeo, in mentem, mente captus, mentis inops, mentis compos, sine m.",  # abbreviated phrases
        "361, 22. *V.* uenter merguli *Cf. GR. L.* IV 199, 7.",  # missing closing period after merguli
    ]

    for i, test_line in enumerate(test_lines):
        xml_line = xmlize_paragraph(test_line)
        xml_line = xml_line.rstrip('</entryFree>')
        tokens = tokenize_lemma_refs(xml_line)
        tagged_tokens = tag_lemma_tokens(tokens)
        output = tokens_to_text(tagged_tokens)

        print(f"{i}\n{test_line} ->", output, '\n')

        # print(f"{i} {test_line} ->", xml_line)
        # print(tokens, '\n\n')
