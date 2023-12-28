import os
from DHParser import nodetree, transform

def fix_cglo_xml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
    tree = nodetree.parse_xml(data)

    def is_first_form_element(path):
        assert path[-1].name == "form"
        assert path[-2].name == "entryFree"
        parent, node = path[-2:]
        return parent[0] == node

    transformations = {
        "div": transform.apply_if(transform.replace_by_single_child,
                                  transform.has_child("entryFree")),
        "form": transform.apply_ifelse(transform.add_attributes({'form': 'headword'}),
                                       transform.add_attributes({'form': 'variant'}),
                                       is_first_form_element),
        "ref": transform.move_fringes(transform.is_one_of('ref'))
    }
    transform.transformer(tree, transformations)
    xml = tree.as_xml(inline_tags={'entryFree'})

    directory, filename = os.path.split(filename)
    outdir = os.path.join(directory, 'out')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    with open(os.path.join(outdir, filename), 'w', encoding='utf-8') as f:
        f.write(xml)

if __name__ == "__main__":
    fix_cglo_xml('CGLO.01.A.xml')
