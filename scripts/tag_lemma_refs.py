# Finds cross-refs to other lemmata in the Thes. gloss. and transforms
# them to correct XML tags, e.g. <xr target="#Index-B11">Babylon</xr>
# Lemma references begin with <emph>v.</emph> or <emph>V.</emph>
    # sometimes cross-references occur in parentheses in the middle of an entry.
    # sometimes cross-refs to multiple words are separated by commas (or *vel*, *et*).
    # sometimes a cross-ref. to a single word is followed by smthg else in italics
    # xref list usually terminated with full stop, sometime with comma, sometimes italic phrase, sometimes closing parenthesis or square bracket.
    # If a dot has been mistakenly replaced by comma, then bold may follow.

import re
from mkd_to_xml import xmlize_paragraph

def tokenize_lemma_refs(paragraph):
    TOKENS = [
        ('VIDE', r"(?P<VIDE><emph>[vV]\.</emph>)"),
        ('FULL_STOP', r"(?P<FULL_STOP>\.)(?!,| .{1,10},)"),
        ('SEMICOLON',  r"(?P<SEMICOLON>;)"),
        ('END_ROUND_BRACKET', r"(?P<END_ROUND_BRACKET>\))"),
        ('END_SQUARE_BRACKET', r"(?P<END_SQUARE_BRACKET>\])"),
        ('VEL_OR_ET', r"(?P<VEL_OR_ET><emph> *(vel|et) *</emph>)"),
        ('EMPH_TAG', r"(?P<EMPH_TAG><emph>.+?</emph>)"),  # excludes *vel* or *et*
        ('FORM_TAG', "(?P<FORM_TAG><form.+?</form>)"),
        ('ROMAN_NUM', "(?P<ROMAN_NUM>[IVX] )"),
        ('ARAB_NUM',  r'(?P<ARAB_NUM>\d)'),
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



def tag_lemma_refs(paragraph):  # input is a paragraph of text
    # vide = re.compile(r"<emph>[vV]\.</emph>")
    vide = re.compile(r"<emph>[vV]\.</emph>")
    TERMINATORS = [r"\.(?!,| .{1,10},)", r";", r"\)", r"\]", r"<emph>(?!(vel</emph>|et</emph>|\s))", "<form", "[IVX] ", r'\d', r'\n', '<ref']
    # TERMINATORS = [r"\.(?!,| .{1,10},)", r";", r"\)", r"\]", r"\*(?!(vel\*|et\*|\s))", r"\*\*", "[IVX] ", r'\d', '\n']
    terminator = re.compile('|'.join(TERMINATORS))
    tagged_paragraph = paragraph

    # Test TERMINATORS
    # print("Terminators:", TERMINATORS)
    # print("Joined terminators:", '|'.join(TERMINATORS))
    # test_terminator = re.compile(r";")
    # print(test_terminator.match("This is a sentence with ; in the middle"))

    matches = vide.finditer(paragraph)

    # Split paragraph into substrings beginning with the end of each match and continuing
    # to a valid terminator. If no valid terminator is found, make sure to end before
    # the beginning of the next match.

    for match in matches:
        substring = paragraph[match.end():]

        next_terminator = terminator.search(substring)
        if next_terminator:
            next_terminator_pos = next_terminator.start()
            # print("Terminator found:", next_terminator.group())
        else:
            next_terminator_pos = -1
        substring = substring[:next_terminator_pos]
        # print("Substring:", substring)

        substring = re.sub(r"<emph>(vel|et)</emph>", ",", substring)  # replace *vel* and *et* with commas
        # substring = re.sub(r"\*(vel|et)\*", ",", substring)  # replace *vel* and *et* with commas

        lemma_refs = substring.split(',')

        for lemma_ref in lemma_refs:
            lemma_ref = lemma_ref.strip()
            if lemma_ref == '':
                continue
            lemma_ref_XML = f'<xr target="">{lemma_ref}</xr>'
            # print(f"Lemma_ref: {lemma_ref}, XML: {lemma_ref_XML}")
            tagged_paragraph = tagged_paragraph.replace(lemma_ref, lemma_ref_XML)

    return tagged_paragraph



if __name__ == "__main__":
    test_lines = [
        "559, 3. ὑπεναντίοι pluraliter II 559, 4. *V.* aduores, contrarius.",
        "**aduertere** intelligere IV 9, 20. *V.* aduorti hercle animum.",
        "conuocat IV 484, 9. **aduocentur** ἐπασχολοῦνται II 10, 3 (*v.* auoco).",
        "**Aeramen** χάλκωμα III 93, 69. *V.* aeris flos, aerosus, aerugo, aes ustum, flos aeraminis.",
        "**Aeuus** eiusdem aetatis, par IV 306, 29. *V.* coaeuus *et* aequaeuus.",
        "*V.* adoria *sub fin.,* adorium, affaber.",
        "[inpiger] V 264, 10 (*v.* 8). **adlisum** adlositum IV 304, 22)",
        "oberrare (ab.?) V 642, 39 (*Non.* 121, 19). *V.* futura alucinatus, V *praef.* V. *Cf. Martian. Gap. p.* 167",
        "(*Eyssenh.*); *Wessner Comm. Ien. *V.* anclena, *AHD. GL.* III 123, 58; 222, 20; 633, 49.",
        "*v.* *d. Vliet Arch.* IX 302)",
        "*V.* anes, **anitas**",
        "Virg. Georgicon lib. III (*v.* 80)",
        "*v.* **arma** unius hominis).",  # This is a valid ref. to another lemma!
        "*v.* axilla *et Isid.* XI 1, 65).",  # followed by *et ...* but not another lemma
        "*V.* ependyten, melos 2.",  # lemma followed by Arabic numeral
        "*V.* alta mente, in m. est, i. m. habeo, in mentem, mente captus, mentis inops, mentis compos, sine m.",  # abbreviated phrases
        "361, 22. *V.* uenter merguli *Cf. GR. L.* IV 199, 7.",  # missing closing period after merguli
    ]

    for i, test_line in enumerate(test_lines):
        xml_line = xmlize_paragraph(test_line)
        tokens = tokenize_lemma_refs(xml_line)
        print(f"{i} {test_line} ->", xml_line)
        print(tokens, '\n\n')
