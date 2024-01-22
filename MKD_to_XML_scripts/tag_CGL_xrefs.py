import logging, re, textwrap, difflib

# from mkd_to_xml import *
from identify_gloss import *  # for looking up glossary short names
from roman_to_arabic import arab_rom, rom_arab  # for converting Roman and Arabic numbers

# xref_logfile = "logs/cglo-xref.log"  # store information about discarded xrefs here

# Takes a paragraph string and returns a version with XML tags.
def tag_CGL_refs_new(paragraph):
    # print("Paragraph:", paragraph)
    tokens = tokenize_paragraph(paragraph)
    tagged_tokens = tag_tokens(tokens, paragraph)
    text = tokens_to_text(tagged_tokens)

    return text

# Tokenizes a paragraph string.
def tokenize_paragraph(paragraph):
    TOKENS = [
        ('FULL_XREF', r'(?<![XVI])(?P<FULL_XREF>I|II|III|IV|V|VI|VII) (?P<PAGE>\d+), (?P<LINE>\d+)(?P<SLASHED>/\d+)?'),
        ('PREFACE_XREF', r'(?P<PREFACE_XREF>I|II|III|IV|V|VI|VII) p\. (?P<ROM1>XC|XL|L?X{0,3})?(?P<ROM2>IX|IV|V?I{0,3})?(?!\d)'),
        ('PARTIAL_XREF', r"(?<![IV] )(?P<PARTIAL_XREF>\d+), (?P<P_LINE>\d+)(?P<P_SLASHED>/\d+)?"),
        ('EMPH_TAG', r'(?P<EMPH_TAG><emph>.+?</emph>)'),
        ('FORM_TAG', r'(?P<FORM_TAG><form.+?</form>)'),
        ('PB_TAG', r'(?P<PB_TAG><pb.+?</pb>)'),
        ('KLAMMER', r'(?P<KLAMMER>\(.+?\))'),
        ('SEMICOLON', r'(?<![tsp])(?P<SEMICOLON>;)'),  # excludes escape characters &lt; "&gt; &quot; &apos; &amp;
                                                    # and other instances where a semicolon terminates an alphabetic word
        ('PLUS', r'(?P<PLUS>\+)'),
        ('EQUALS', r'(?P<EQUALS>=)'),
        ('POSS_LINE_REF', r'(?P<POSS_LINE_REF>(?<![IVX]) \d{1,2}[;. ])')  # catches digits 1-99 that may be isolated line numbers
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


# Takes a list of tokens and converts to string.
def tokens_to_text(tokens):
    text = ''
    for name, content, span in tokens:
        text += content

    return text


# Takes a list of tokens and a corresponding paragraph stgring and converts the content
# of relevant tokens (full xrefs, partial xrefs, preface xrefs) into XML tags.
# Paragraph is used sometimes to compare underlying string (invalid_source_precedes function).
# The argument last_full_xref is used when processing parentheses to remember
# the last full xref in case all the xrefs are incomplete.
def tag_tokens(tokens, paragraph, last_xref_before_klammer = None):
    tagged_tokens = []
    for i, (name, content, span) in enumerate(tokens):
        if name == 'FULL_XREF':
            # check if something invalid precedes the xref
            if invalid_source_precedes(paragraph[:span[0]]):
                # print("Discarded xref", content)
                logging.warning(f"Discarded xref {content} after invalid source in: {paragraph[span[0]-20:span[1]+15]}")
                tagged_tokens.append(('TEXT', content, span))
                continue

            content = tag_full_xref(content)
            # print("FULL_XREF!", content)

        elif name == 'PREFACE_XREF':
            content = tag_preface_xref(content)
            # print("PREFACE_XREF!", content)

        elif name == 'PARTIAL_XREF':
            # check if it follows a full_xfref or preface_xref
            previous_xref = find_previous_xref(tagged_tokens)
            if previous_xref == None:
                logging.warning(f"Discarded xref {content} without prev. xref in: {paragraph[span[0]-20:span[1]+15]}")
                tagged_tokens.append(('TEXT', content, span))
                continue
            elif previous_xref == 'START_OF_KLAMMER?':  # we are in a parenthesis, so supply the last xref from last_full_xref
                if last_xref_before_klammer is None:
                    logging.warning(f"Discarded POSS_LINE_REF {content} after unidentifable xref in: {paragraph[span[0]-20:span[1]+15]}")
                    tagged_tokens.append(('TEXT', content, span))
                    continue
                else:
                    print(f"Supplying xref ({content}) from before Klammer:", last_xref_before_klammer)
                    previous_xref = last_xref_before_klammer

            content = tag_partial_xref(content, extract_vol(previous_xref))
            # print("PARTIAL XREF: ", content)

        elif name == 'POSS_LINE_REF':
            previous_xref = find_previous_xref(tagged_tokens)
            if previous_xref == None:
                logging.warning(f"Discarded POSS_LINE_REF {content} in: {paragraph[span[0]-20:span[1]+15]}")
                tagged_tokens.append(('TEXT', content, span))
                continue
            elif previous_xref == 'START_OF_KLAMMER?':
                if last_xref_before_klammer is None:
                    logging.warning(f"Discarded POSS_LINE_REF {content} after unidentifable xref in: {paragraph[span[0]-20:span[1]+15]}")
                    tagged_tokens.append(('TEXT', content, span))
                    continue
                else:
                    print(f"Supplying xref ({content}) from before Klammer:", last_xref_before_klammer)
                    previous_xref = last_xref_before_klammer

            content = tag_line_number(content, extract_vol(previous_xref), extract_page(previous_xref))
            name = 'PARTIAL_XREF'  # change token name

        elif name == 'KLAMMER':
            # check if parenthesis contains xrefs of any kind!
            # print("KLAMMER!", content)
            tokenized_klammer = tokenize_paragraph(content[1:-1])  # delete parentheses at the beginning and end
            # print("Tokenized klammer:", tokenized_klammer)
            # If the very first token in a parenthesis is a PARTIAL_XREF, pass
            # the last full xref from before the Klammer.
            last_xref_before_klammer = find_previous_xref(tagged_tokens)

            tagged_klammer = tag_tokens(tokenized_klammer, content[1:-1], last_xref_before_klammer)
            # print("Tagged, tokenized klammer:", tagged_klammer)

            klammer_text = tokens_to_text(tagged_klammer)
            content = '(' + klammer_text + ')'
            # print(" -> TAGGED KLAMMER:", content)

        tagged_tokens.append((name, content, span))

    return tagged_tokens


# Takes a full xref string and returns an XML tagged string.
def tag_full_xref(text):
    pattern = r'(?P<FULL_XREF>I|II|III|IV|V|VI|VII) (?P<PAGE>\d+), (?P<LINE>\d+)(?P<SLASHED>/\d+)?'
    regex = re.compile(pattern)

    try:
        match = regex.search(text)
        volume = match.group('FULL_XREF')
        page = match.group('PAGE')
        line = match.group('LINE') + (match.group('SLASHED') or '')

        # Get the short abbreviation of the ref to be added with <addName> attribute.
        xref = f'{volume} {page}, {line}'
        short_name = identify_gloss_from_xref(xref)

        formatted_xref = f"<ref addName=\"{short_name}\" cRef=\"CGL.{volume}.{page}.{line}\">{match.group().strip()}</ref>"
    except:
        raise Exception(f"Not a valid xref: {text}")

    return formatted_xref


# Takes a full preface xref string and returns an XML tagged version.
def tag_preface_xref(text):
    pattern = r'(?P<PREFACE_XREF>I|II|III|IV|V|VI|VII) p\. (?P<ROM1>XC|XL|L?X{0,3})?(?P<ROM2>IX|IV|V?I{0,3})?'
    regex = re.compile(pattern)
    match = regex.search(text)

    volume = match.group('PREFACE_XREF')
    Roman_page = (match.group('ROM1') or '') + (match.group('ROM2') or '')

    formatted_xref = f"<ref cRef=\"CGL.{volume}.praef_{Roman_page}\">{match.group()}</ref>"

    return formatted_xref


# Given a list of tokens preceding a partial xref, return the last full xref
# as long as no invalid sequences intervene.
# If we reach the end of the token list without an invalid token, return 'START_OF_KLAMMER?'
# Otherwise return None.
def find_previous_xref(tokens):
    IGNORE_TOKENS = ['PB', 'WS', 'KLAMMER']  # filter out these tokens
    filtered_tokens = [token for token in tokens if token[0] not in IGNORE_TOKENS]
    filtered_tokens.reverse()

    i = 0
    for i, (name, content, span) in enumerate(filtered_tokens):
        if name in ['TEXT', 'EMPH_TAG', 'FORM_TAG']:  # if any of these tokens intervene the sequence is invalid
            return None
        elif name == 'SEMICOLON' or name == 'PLUS' or name == 'EQUALS':  # a semicolon,  plus, or equals is a valid separator
            continue
        elif name == 'PARTIAL_XREF':
            break
        elif name == 'FULL_XREF':
            break

    if i < len(filtered_tokens) - 1:
        return filtered_tokens[i]
    else:  # it's possible this token is at the beginning of a parenthesis and no invalid token intervenes
        return 'START_OF_KLAMMER?'

# Takes a partial xref string and a volume number as Roman numeral and returns xml tag.
def tag_partial_xref(text, volume_Roman):
        pattern = r"(?P<PARTIAL_XREF>\d+), (?P<P_LINE>\d+)(?P<P_SLASHED>/\d+)?"
        regex = re.compile(pattern)
        match = regex.search(text)

        page = match.group('PARTIAL_XREF')
        line = match.group('P_LINE') + (match.group('P_SLASHED') or '')

        # Get the short abbreviation of the ref to be added with <addName> attribute.
        xref = f'{volume_Roman} {page}, {line}'
        short_name = identify_gloss_from_xref(xref)

        tagged_partial_ref = f'<ref addName="{short_name}" cRef="CGL.{volume_Roman}.{page}.{line}">{text}</ref>'

        return tagged_partial_ref


# Takes a partial xref in the form of a single line number and converts to <ref>.
# Will be one to two digits between 1-99.
def tag_line_number(text, volume_Roman, page):
    line = text.strip()  # remove initial space
    if line[-1] == ';' or line[-1] == '.':
        divider = line[-1]
        line = line[:-1]
    else:
        divider = ''

    xref = f'{volume_Roman} {page}, {line}'
    short_name = identify_gloss_from_xref(xref)

    # NB: space moved within line-text to before <ref>
    tagged_partial_ref = f' <ref addName="{short_name}" cRef="CGL.{volume_Roman}.{page}.{line}">{line}</ref>{divider}'

    return tagged_partial_ref


# Takes an xref token (full or partial) and extracts the volume number.
def extract_vol(xref):
    # print("Extracting volume:", xref)
    name, content, span = xref  # take apart the token
    pattern = r'CGL\.(?P<VOL>[IV]+)\.(\d+)'  # find the first part of the string in the format 'CGL.IV.433.32/34'
    match = re.search(pattern, content)

    try:
        return match.group('VOL')
    except:
        print("Vol could not be extracted from incomplete xref:", content)


# Takes an xref token (full or partial) and extracts page number.
def extract_page(xref):
    name, content, span = xref  # take apart the token
    pattern = r'CGL\.(?P<VOL>[IV]+)\.(?P<PAGE>\d+)'  # find the second part of the string in the format 'CGL.IV.433.32'
    match = re.search(pattern, content)

    return match.group('PAGE')

# Checks whether the text preceding a valid-looking xref actually contains a CGL xref.
# Currently excludes "Isid." and "GR. L.", possibly more tweaking necessary.
def invalid_source_precedes(prior_text):
    INVALID_SOURCES = (' L', 'Isid', 'epist', 'Oros', 'Ien', 'Epi', 'Verg',
    'carm', 'Sat', 'Aen', 'Gell', 'Ecl', 'GL', 'Aurel', 'inst', ' ep', 'Eun',
    'sat', 'Hor', ' ac', 'Quint', 'dial', ' Ep', 'Max', 'Carm', 'off', 'Trist',
    'Colum', 'Is', 'Orig', 'Hor. c', 'hist', 'Anthol. l', 'rer', 'de re r',
    'Hec', 'Val')

    try:
        split_prior_text = prior_text.split('.')
        text_before_previous_dot = split_prior_text[-2]
        if text_before_previous_dot.endswith(' p'):  # if the text ends with " p. " (e.g. II p. XI; III 34, 3) step back one dot
            text_before_previous_dot = split_prior_text[-3]
        if text_before_previous_dot.endswith(INVALID_SOURCES):
            if ")" in split_prior_text[-1] or "<form>" in split_prior_text[-1]:
                return False
            else:
                return True
    except:
        pass


# Takes two paragraph strings and prints the differences.
def compare_paragraphs(par1, par2):  # takes two non-separated paragraphs and compares them
    par1 = textwrap.wrap(par1)
    par2 = textwrap.wrap(par2)

    diff = difflib.context_diff(par1, par2, fromfile='par1', tofile='par2')
    print('\n'.join(list(diff)))


# If this module called as main, perform some tests.
if __name__ == '__main__':
    TEST_PAR = r"""**Defrutum** ἕψημα II 41, 5 (deflutum *cod.*); 41, 6 (deflictum
*cod.*); III 255, 36/37; II 321, 39 (pluralia non habet: *cf. GR. L.* II
34, 30 *et alibi*); 69. ἀπόβρασμα, ἕψημα II 41, 17; 143, 3; 200, 20; 500, 50; 66. coerin (*AS.*) V
404, 59; 355, 51 (defructum). quod defraudatur et quasi fraudem patiatur
V 653, 21 (*cf. Serv. in Georg.* II 93; *Isid.* XX 3, 14; 32); <emph>Isid.</emph> II 43, 2. uinum
quoquendo defraudatum et dictum defrutum eo quod quoquendo arescat
minusue faciat (!) V 653, 22; <emph>Buech p.</emph> 23, 3. **defritum** ἕψημα III 15, 33. ἀφέψημα III
315, 42. chrodidon (χονδρίον *Buech.*; II 43, 2; 456, 24) III 184, 50. frixum II 576, 19.
uinum squamaticum III 559, 42. **defretum** sapa, passum II p. XIII; V
543, 40. uinum quoquendo defrudatum V 188, 21; 34. **defruta** quod aruit:
graece enim dicitur ἕψημα, unde et defretum eo quod coquendo arescat
minusue fiat (*vel* fecit) IV p. XI. *V.* defersum.
**Abdomini natus** gulae deditus V 660, 4 + 662, 15 (*cf. Ind. Ien.*
1888 *p.* VII). ab actu remotus (= *Isid.* X 20) IV 3, 3; 201, 4; 301, 2; V
259, 21; 343, 21.
**Disputatis (dissupatis?) bonis** dilapidato patrimonio, de
inofficioso testamento V 661, 32; 33; 34 (*Ind. Ien.* 1888 *p.* VI).
**Haud (haut) clam fuit** non latuit, non fefellit *Plac.* V 73, 4 =
12 = V 108, 2.
**Mustum de uua (*vel* uuas) agresti** ὀμφάκιον III 548, 37; 593, 20
(mustus deuius); 627, 9 (intusdeuas).
<form>Aeramentum</form> χάλκωμα II 475, 11; III 439, 6; 478, 30. χαλκός
(<emph>vel</emph> χαλκόν) II 556, 44; III 434, 49. aes IV 306, 11.
<form>aeramenta</form> χαλκώματα III 23, 4; 163, 59; 203, 49; 215, 58
(= 231, 30 = 235, 9); 343, 39; 439, 7."""

    paragraph = TEST_PAR.replace('\n', ' ')
    paragraph = escape_characters(paragraph)
    paragraph = tag_forms(paragraph)
    paragraph = tag_italics(paragraph)

    old_paragraph = tag_CGL_refs(paragraph)  # tagged according to OLD function
    # tagged_paragraph = xref_scanner(paragraph)  # tagged according to NEW function
    # compare_paragraphs(old_paragraph, tagged_paragraph)

    tokens = tokenize_paragraph(paragraph)
    print(tokens, '\n\n')
    tagged_tokens = tag_tokens(tokens, paragraph)
    text = tokens_to_text(tagged_tokens)
    print(tagged_tokens)

    # compare_paragraphs(old_paragraph, text)

    print(old_paragraph)
    print(text)
