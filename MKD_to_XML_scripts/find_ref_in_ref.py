# Finds <ref> elements that contain another <ref> element
import os
from lxml import etree

path = 'xml_output'

files = [f for f in os.listdir(path) if f.endswith(".xml") and int(f.split('.')[1]) < 99]

for filename in files:
    print(f"Checking {filename} for nested <ref> tags.")
    tree = etree.parse(f"{path}/{filename}")
    r = tree.xpath('//ref/ref')

    for element in r:
        page = element.xpath("preceding::pb[@n]")[-1].get("n")
        print(f"Line {element.sourceline} ({page}), text: {element.text}")
