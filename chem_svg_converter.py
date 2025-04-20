import os
import re
from lxml import etree

#TODO: Update to correctly set the dark colors
CPK_COLORS = {
    "elements": {
        "H": {"light": "#000000", "dark": "#000000"},     #"dark": "#e0e0e0"},
        "C": {"light": "#000000", "dark": "#000000"},    #"dark": "#e0e0e0"},
        "N": {"light": "#2144d9", "dark": "#2144d9"},    #"dark": "#8fa3ff"},
        "O": {"light": "#ff0d0d", "dark": "#ff0d0d"},    #"dark": "#ff6666"},
        "S": {"light": "#e1e100", "dark": "#e1e100"},    #"dark": "#ffff00"},
        "P": {"light": "#ff8000", "dark": "#ff8000"},    #"dark": "#ffb366"},
        "F": {"light": "#90e000", "dark": "#90e000"},    #"dark": "#c3ff00"},
        "Cl": {"light": "#00e000", "dark": "#00e000"},    #"dark": "#66ff66"},
        "Br": {"light": "#a52a2a", "dark": "#a52a2a"},    #"dark": "#d47878"},
        "I": {"light": "#940094", "dark": "#940094"},    #"dark": "#d478d4"},
    },
    "bonds": {"light": "#000000", "dark": "#ffffff"}
}

def convert_svg(svg_path):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    # Remove existing style elements
    for elem in root.xpath("//*[local-name()='style']"):
        elem.getparent().remove(elem)

    # Add new consolidated style element
    style = etree.Element('style')
    css_vars = [
        ":root {",
        *[f"  --{elem.lower()}: {colors['light']};" 
         for elem, colors in CPK_COLORS["elements"].items()],
        "  --bonds: #000000;",
        "}",
        "@media (prefers-color-scheme: dark) {",
        ":root {",
        *[f"  --{elem.lower()}: {colors['dark']};" 
         for elem, colors in CPK_COLORS["elements"].items()],
        "  --bonds: #ffffff;",
        "}}"
    ]
    style.text = "\n".join(css_vars)
    root.insert(0, style)

    # Process elements and groups
    for elem in root.iter():
        if elem.tag.endswith('text') and elem.text:
            text = elem.text.strip()
            
            # Handle polymer 'n'
            if text.lower() == 'n':
                elem.set('fill', 'var(--bonds)')
                continue
                
            # Match element symbols at start of text
            match = re.match(r"^([A-Z][a-z]?)", text)
            if match:
                elem_symbol = match.group(1)
                if elem_symbol in CPK_COLORS["elements"]:
                    color_var = 'c' if elem_symbol == 'H' else elem_symbol.lower()
                    elem.set('fill', f'var(--{color_var})')
                    
                    # Handle subscript numbers for multi-character groups
                    next_sibling = elem.getnext()
                    if next_sibling is not None and next_sibling.tag.endswith('text'):
                        num_text = next_sibling.text.strip()
                        if num_text.isdigit():
                            next_sibling.set('fill', f'var(--{color_var})')

        # Process bonds and other paths
        elif elem.tag.endswith('path'):
            if elem.get('fill', '') != 'none':
                elem.set('fill', 'var(--bonds)')
            if elem.get('stroke', '') != 'none':
                elem.set('stroke', 'var(--bonds)')

    # Save changes
    tree.write(svg_path, pretty_print=True, 
              xml_declaration=True, encoding='utf-8')

def process_svgs():
    for fname in os.listdir('.'):
        if fname.lower().endswith('.svg'):
            convert_svg(fname)

if __name__ == '__main__':
    process_svgs()
    print("Converted all SVGs in current directory")
