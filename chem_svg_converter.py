import os
import argparse
from lxml import etree

CPK_COLORS = {
    "elements": {
        "H": {"light": "#000000", "dark": "#e0e0e0"},   # Hydrogen (same as Carbon)
        "C": {"light": "#000000", "dark": "#e0e0e0"},   # Carbon
        "N": {"light": "#2144d9", "dark": "#8fa3ff"},   # Nitrogen
        "O": {"light": "#ff0d0d", "dark": "#ff6666"},   # Oxygen
        "S": {"light": "#e1e100", "dark": "#ffff00"},   # Sulfur
        "P": {"light": "#ff8000", "dark": "#ffb366"},   # Phosphorus
        "F": {"light": "#90e000", "dark": "#c3ff00"},   # Fluorine
        "Cl": {"light": "#00e000", "dark": "#66ff66"},  # Chlorine
        "Br": {"light": "#a52a2a", "dark": "#d47878"},  # Bromine
        "I": {"light": "#940094", "dark": "#d478d4"},   # Iodine
    },
    "bonds": {"light": "#000000", "dark": "#ffffff"}
}

def convert_svg(svg_path):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()
    
    # Add CSS variables
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

    # Process elements
    for elem in root.iter():
        if elem.tag.endswith('text') and elem.text:
            elem_symbol = elem.text.strip()
            if elem_symbol in CPK_COLORS["elements"]:
                # Use carbon's color variable for hydrogen
                color_var = 'c' if elem_symbol == 'H' else elem_symbol.lower()
                elem.set('fill', f'var(--{color_var})')
                
                # Handle subscript numbers
                next_sibling = elem.getnext()
                if next_sibling is not None and next_sibling.tag.endswith('text'):
                    num_text = next_sibling.text.strip()
                    if num_text.isdigit():
                        next_sibling.set('fill', f'var(--{color_var})')
        
        # Process bonds
        elif elem.tag.endswith('path'):
            if elem.get('fill', '') != 'none':
                elem.set('fill', 'var(--bonds)')
            if elem.get('stroke', '') != 'none':
                elem.set('stroke', 'var(--bonds)')

    # Overwrite original file
    tree.write(svg_path, pretty_print=True, 
             xml_declaration=True, encoding='utf-8')

def process_svgs():
    for fname in os.listdir('.'):
        if fname.lower().endswith('.svg'):
            convert_svg(fname)

if __name__ == '__main__':
    process_svgs()
    print("Converted all SVGs in current directory")
