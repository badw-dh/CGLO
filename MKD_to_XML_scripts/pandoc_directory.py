import subprocess
import os

# output_directory = r"C:/users/di57gab/cglo-git/CGLtoXML/word_test"
output_directory = r"C:/users/adamg/cglo-git/scripts/word_test"

# pandoc_path = r""c:\users\di57gab\appdata\local\pandoc\pandoc"
pandoc_path = "pandoc"

directory_list = [
    # r"C:/users/adamg/dropbox/cglo/vol 6/vol 6 word proofread",
    # r"C:/users/di57gab/cglo-git/ProofreadWordVol6"
    # r"C:/users/adamg/dropbox/cglo/vol 6/vol 6 word proofread corrigenda",
    # r"C:/users/adamg/dropbox/cglo/vol 7/vol 7 word proofread",
    # r"C:/users/adamg/dropbox/cglo/vol 7/vol 7 proofread corrigenda",
    # r"C:/users/adamg/dropbox/cglo/vol 7/vol 7 word proofread anglosaxonico-latinus",
    # r"C:/users/adamg/dropbox/cglo/vol 7/vol 7 word proofread index graeco-latinus",
    # r"C:/users/adamg/dropbox/cglo/vol 7/vol 7 word uncorrected Graeco-latinus"
    "C:/users/adamg/LRZ Sync+Share/GLOSS Online/Website"
]

for directory in directory_list:
    print(f"Pandoc'ing directory {directory}.")
    for file_name in os.listdir(directory):
        output_file = file_name.strip(".docx")
        # subprocess.run(["pandoc", "-f", "docx", "-t", "markdown", f"{directory}/{file_name}", "-o", f"{output_directory}/{output_file}.mkd"])
        subprocess.run([pandoc_path, "-f", "docx", "-t", "markdown", f"{directory}/{file_name}", "-o", f"{output_directory}/{output_file}.mkd"])
