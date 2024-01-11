# Copies data files and scripts to the public directory.
import os
from pathlib import Path
from shutil import copytree, copy

BASE_PATH = Path(__file__).resolve().parent.parent
TARGET_PATH = Path("c:/Users/adamg/cglo-public")
TARGET_SCRIPTS_PATH = TARGET_PATH / "MKD_TO_XML_scripts"

DATA_FOLDERS = [
    "markdown",
    "markdown-combined",
    "XML",
    "JSON"
    ]

# Files in the scripts directory not to copy:
EXCLUDE_FILES = ["word_test", "old_scripts", "!TODO.txt", ".gitkeep", "schema-CGLO.xml"]

# Copy all contents of each data folder.
for dir in DATA_FOLDERS:
    copytree(BASE_PATH / dir, TARGET_PATH / dir, dirs_exist_ok = True)
    print("Copied files to", TARGET_PATH / dir)

files = [BASE_PATH / "scripts" / f for f in os.listdir() if f not in EXCLUDE_FILES]

for filename in files:
    copy(filename, TARGET_SCRIPTS_PATH)
    print("Copying", filename)
