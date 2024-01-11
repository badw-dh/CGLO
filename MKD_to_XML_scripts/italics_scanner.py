import re
import logging

# An object for storing information about a page of CGL data. Keeps track of
# relationship between lines and paragraphs and italicization.
class CGLO_Page(object):

    def __init__(self, list_of_lines):
        self.list_of_lines = list_of_lines
        self.dict_of_paragraphs = {}

        self.create_dict_of_paragraphs()

    def convert_line_to_paragraph(self, line_number):
        if line_number > len(self.list_of_lines):
            raise LengthError("line number was greater than extant lines")
        else:
            return self.dict_of_paragraphs[line_number]

    # Function creates a dictionary that maps a line number to the Paragraph object
    # containing that line. The Paragraph object can be used to test whether
    # a span of characters is italic or not.
    def create_dict_of_paragraphs(self):
        start_of_paragraph = 0
        for i, line in enumerate(self.list_of_lines):
            if line == '':
                # Either there is a blank line as separator or we have reached EOF.

                if i == 0:
                    logging.warning("Blank line at beginning of file.")
                    continue

                new_paragraph = Paragraph(self.list_of_lines[start_of_paragraph:i], start_of_paragraph)

                for counter in range(start_of_paragraph, i + 1):
                    self.dict_of_paragraphs.update({counter : new_paragraph})

                start_of_paragraph = i + 1
                # print(f"Line {i+1}, text: {line}")

            # Special case for when we have reached EOF and it is not a blank line.
            elif  i == len(self.list_of_lines) - 1:

                # Create a new paragraph that includes the very last line.
                new_paragraph = Paragraph(self.list_of_lines[start_of_paragraph:], start_of_paragraph)

                for counter in range(start_of_paragraph, i + 1):
                    self.dict_of_paragraphs.update({counter : new_paragraph})

                # print(f"Line {i+1}, text: {line}")
            # The paragraph continues so advance to the next line.
            else:
                continue


        if len(self.dict_of_paragraphs) == 0:
            logging.warning("No paragraphs identified.")


class Paragraph(object):

    def __init__(self, list_of_lines, first_line_number):
        self.list_of_lines = list_of_lines
        self.first_line_number = first_line_number
        self.italic_segments = []
        self.chunk_into_italics()

    def chunk_into_italics(self):
        within_italics = False

        for line_number, line_text in enumerate(self.list_of_lines):
            i = 0
            while i < len(line_text):
                # match = re.search(r"(?<!(\\|\*))\*(?!\*)", line_text[i:])
                match = re.search(r"(?<!(\\|\*))\*(?!\*[^\*])", line_text[i:])
                if match:
                    end = match.end()
                    if within_italics == False:
                        # Start a new italic segment.
                        italic_start_line = line_number
                        italic_start_character = end + i - 1 # Subtract one to include opening *
                        within_italics = True
                        i += end
                    elif within_italics == True:
                        # End an italic segment.
                        italic_end_character = end + i # Includes final *
                        italic_end_line = line_number
                        italic_text = self.extract_text(italic_start_line,
                            italic_start_character + 1, italic_end_line, italic_end_character - 1)
                        self.italic_segments.append((italic_start_line,
                            italic_start_character, italic_end_line, italic_end_character, italic_text))
                        within_italics = False
                        i += end
                else:
                    break
        if within_italics == True:
            # All lines have been checked without a closing asterisk.
            # raise Exception(f"Paragraph has no closing italics: {self.list_of_lines}")
            print(f"Paragraph has no closing italics: {self.list_of_lines}")

    def extract_text(self, start_line, start_character, end_line, end_character):
        extract_text = ""
        if start_line == end_line:
            line = self.list_of_lines[start_line]
            extract_text = line[start_character:end_character]
        else:
            line = self.list_of_lines[start_line]
            extract_text = line[start_character:].strip('\n')
            current_line = start_line + 1
            while current_line < end_line:
                extract_text += self.list_of_lines[current_line]
                current_line += 1

            # current_line == end_line
            line = self.list_of_lines[current_line]
            extract_text += line[:end_character]

        return extract_text

    def within_italics(self, line, start, end):
        # Given a span of text within a line determine whether it is italics.
        # The initial and concluding * are considered part of the italic italic_segment
        # even though not included within the text of italic_segments.
        # If any part of the start or end position is outside italics, return False.

        # First convert absolute line number to line number relative to paragraph.
        line = line - self.first_line_number

        for italic_segment in self.italic_segments:
            start_line, start_character, end_line, end_character, italic_text = italic_segment
            if line == start_line and line == end_line:
                # The italic segment is on a single line and it is the same as line.
                if start >= start_character and end <= end_character:
                    return True
            elif line > start_line and line < end_line:
                # The segment falls between the beginning and lines of a very long italic segment.
                return True
            elif line == start_line:
                # If the segment is on the first line of an italic segment that
                # extends across multiple lines we only need to check that
                # it is after the starting position.
                if start >= start_character:
                    return True
            elif line == end_line:
                # The segment falls on the last line of multi-line italic segment.
                # We only need to check the end position.
                if end <= end_character:
                    return True
            else:
                continue
        return False

def test_paragraph_class(paragraph):
    # txt = [
    #     r"**ob** διά II 135, 39. διὰ ἡ πρόθεσις II 270, 3. propter IV 127, 30;",
    #     r"129, 42; 263, 7; 369, 50; 546, 8. diuersas significationes habet:",
    #     r"significat propter, significat contra, significat circum, ut Ennius: ob",
    #     r"Romam noctu legiones ducere coepit V 573, 45 (*Festus* *Pauli p.* 175,",
    #     r"5; *Serv. in A*e*n.* I 233). multa *significat, id est propter, contra,",
    #     r"circum V 315, 42, obter \[obiurgandum, imputandum, castigandum,",
    #     r"accusandum\] V 469, 59 (*cf* obter, obiurgandum). propter. Terentius",
    #     r"(Heaut. 956): quodnam ob factum V 123, 7; 227*, 22."
    #     ]

    # test_paragraph = Paragraph(txt, 1)

    # print(test_paragraph.italic_segments)
    #
    # match = re.search(r"\*Pauli p.\* ", txt[3])
    # start, end = match.span()
    # print(test_paragraph.within_italics(4, start, end))

    print(paragraph.italic_segments)

def test_page_class():
    default_file = "c:/users/adamg/cglo-git/scripts/mkd_raw/VII.1.mkd"
    with open(default_file, encoding="utf-8") as file:
        text = file.read()
        list = text.split("\n")
        page = CGLO_Page(list)

        for line, paragraph in page.dict_of_paragraphs.items():
            print(f"Paragraph at line {line}")
            test_paragraph_class(paragraph)

    paragraph = page.dict_of_paragraphs[9]

    match = re.search(r"\*n.\*", list[9])
    start, end = match.span()
    print(paragraph.within_italics(9, start, end))


if __name__ == "__main__":
    # test_paragraph_class()
    test_page_class()
