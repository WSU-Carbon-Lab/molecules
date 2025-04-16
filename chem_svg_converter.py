import os
import argparse
from lxml import etree

CPK_COLORS = {
    "elements": {
        "C": {"light": "#000000", "dark": "#e0e0e0"},   # Carbon
        "N": {"light": "#2144d9", "dark": "#8fa3ff"},    # Nitrogen
        "O": {"light": "#ff0d0d", "dark": "#ff6666"},    # Oxygen
        "S": {"light": "#e1e100", "dark": "#ffff00"},    # Sulfur
        "P": {"light": "#ff8000", "dark": "#ffb366"},    # Phosphorus
        "F": {"light": "#90e000", "dark": "#c3ff00"},    # Fluorine
        "Cl": {"light": "#00e000", "dark": "#66ff66"},   # Chlorine
        "Br": {"light": "#a52a2a", "dark": "#d47878"},   # Bromine
        "I": {"light": "#940094", "dark": "#d478d4"},    # Iodine
        "Metal": {"light": "#eb9d9d", "dark": "#d47878"} # Metals
    },
    "bonds": {"light": "#000000", "dark": "#ffffff"}
}

def convert_svg(svg_path, output_dir):
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
                elem.set('fill', f'var(--{elem_symbol.lower()})')
                
                # Skip subscript numbers for elements
                next_sibling = elem.getnext()
                if next_sibling is not None and next_sibling.tag.endswith('text'):
                    num_text = next_sibling.text.strip()
                    if num_text.isdigit():
                        next_sibling.set('fill', f'var(--{elem_symbol.lower()})')
        
        # Process bonds and other paths
        elif elem.tag.endswith('path'):
            if elem.get('fill', '') != 'none':
                elem.set('fill', 'var(--bonds)')
            if elem.get('stroke', '') != 'none':
                elem.set('stroke', 'var(--bonds)')

    # Save output
    filename = os.path.basename(svg_path)
    output_path = os.path.join(output_dir, filename)
    tree.write(output_path, pretty_print=True, 
              xml_declaration=True, encoding='utf-8')

def process_svgs(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for fname in os.listdir(input_dir):
        if fname.lower().endswith('.svg'):
            convert_svg(os.path.join(input_dir, fname), output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert chemical SVGs to theme-aware formats')
    parser.add_argument('-i', '--input', required=True, help='Input directory')
    parser.add_argument('-o', '--output', required=True, help='Output directory')
    args = parser.parse_args()
    
    process_svgs(args.input, args.output)
    print(f"Converted SVGs saved to {args.output}")
