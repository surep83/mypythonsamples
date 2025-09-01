import os
import xml.etree.ElementTree as ET

def parse_df_file(df_path):
    import re
    sequences = []
    tables = {}
    table_descriptions = {}

    current_table = None
    in_multiline_description = False
    multiline_desc = ""
    last_field = None
    # Track if we are inside a table block
    table_block = False
    with open(df_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')

            # Sequence parsing
            seq_match = re.match(r'^\s*ADD SEQUENCE\s+"([^"]+)"', line)
            if seq_match:
                sequences.append(seq_match.group(1))
                current_table = None
                last_field = None
                table_block = False
                continue

            # Table parsing
            table_match = re.match(r'^\s*ADD TABLE\s+"([^"]+)"', line)
            if table_match:
                current_table = table_match.group(1)
                tables[current_table] = []
                last_field = None
                # Reset multiline description state when a new table starts
                in_multiline_description = False
                multiline_desc = ""
                table_block = True
                continue
                
            # Only allow table-level DESCRIPTION if we are in a table block and before any field/index
            desc_match = re.match(r'^\s*DESCRIPTION\s+"(.*)', line)
            if desc_match and current_table and table_block:
                desc_content = desc_match.group(1)
                if desc_content.endswith('"'):
                    desc_text = desc_content[:-1]
                    table_descriptions[current_table] = desc_text.strip()
                    table_block = True  # Still in table block until a field/index
                else:
                    multiline_desc = desc_content
                    in_multiline_description = True
                continue

            # Handle multiline description (closing quote may be on its own line or same line)
            if in_multiline_description:
                if line.strip() == '"':
                    table_descriptions[current_table] = multiline_desc.strip()
                    in_multiline_description = False
                    multiline_desc = ""
                elif line.endswith('"'):
                    multiline_desc += '\n' + line[:-1]
                    table_descriptions[current_table] = multiline_desc.strip()
                    in_multiline_description = False
                    multiline_desc = ""
                else:
                    multiline_desc += '\n' + line
                continue

            # Field parsing (ends table block for DESCRIPTION)
            field_match = re.match(r'^\s*ADD FIELD\s+"([^"]+)"\s+OF\s+"([^"]+)"\s+AS\s+(\w+)', line)
            if field_match:
                table_block = False  # No more table-level DESCRIPTION allowed
                field_name = field_match.group(1)
                table_name = field_match.group(2)
                field_type = field_match.group(3)
                field_info = {'name': field_name, 'type': field_type, 'column_label': '', 'help': ''}
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append(field_info)
                last_field = field_info
                continue

            # COLUMN-LABEL parsing (associate with last field)
            col_label_match = re.match(r'^\s*COLUMN-LABEL\s+"(.*)"', line)
            if col_label_match and last_field is not None:
                last_field['column_label'] = col_label_match.group(1).strip()
                continue

            # HELP parsing (associate with last field)
            help_match = re.match(r'^\s*HELP\s+"(.*)"', line)
            if help_match and last_field is not None:
                last_field['help'] = help_match.group(1).strip()
                continue

            # Index parsing (ends table block for DESCRIPTION)
            index_match = re.match(r'^\s*ADD INDEX\s+"([^"]+)"\s+ON\s+"([^"]+)"', line)
            if index_match:
                table_block = False
                continue

    # Ensure every table has a description key
    for t in tables:
        if t not in table_descriptions:
            table_descriptions[t] = ""

    return sequences, tables, table_descriptions

def generate_main_html(sequences, tables, table_descriptions):
    html = ['<html><head><title>DF Overview</title></head><body>']
    html.append('<h1>QAD EAM DF Overview</h1>')
    html.append('<ul>')
    html.append('<li><a href="sequences.html">Sequences</a></li>')
    html.append('</ul>')
    html.append('<h2>Tables</h2>')
    html.append('<table border="1"><tr><th>Table Name</th><th>Link</th><th>Description</th></tr>')
    for table in tables:
        desc = table_descriptions.get(table, "")
        html.append(
            f'<tr><td>{table}</td>'
            f'<td><a href="{table}.html">{table}</a></td>'
            f'<td>{desc}</td></tr>'
        )
    html.append('</table>')
    html.append('</body></html>')
    return '\n'.join(html)

def generate_sequences_html(sequences):
    html = ['<html><head><title>Sequences</title></head><body>']
    html.append('<h1>Sequences</h1>')
    html.append('<ul>')
    for seq in sequences:
        html.append(f'<li>{seq}</li>')
    html.append('</ul>')
    html.append('<a href="index.html">Back to Main</a>')
    html.append('</body></html>')
    return '\n'.join(html)

def generate_table_html(table_name, fields, table_description):
    html = [f'<html><head><title>{table_name}</title></head><body>']
    html.append(f'<h1>Table: {table_name}</h1>')
    html.append(f'<p><b>Description:</b> {table_description}</p>')
    html.append('<table border="1"><tr><th>Field Name</th><th>Type</th><th>Column Label</th><th>Help</th></tr>')
    for field in fields:
        html.append(
            f'<tr><td>{field["name"]}</td><td>{field["type"]}</td><td>{field["column_label"]}</td><td>{field["help"]}</td></tr>'
        )
    html.append('</table>')
    html.append('<a href="index.html">Back to Main</a>')
    html.append('</body></html>')
    return '\n'.join(html)

def generate_xml(sequences, tables, table_descriptions, output_path):
    root = ET.Element('DFSchema')

    seqs_elem = ET.SubElement(root, 'Sequences')
    for seq in sequences:
        seq_elem = ET.SubElement(seqs_elem, 'Sequence')
        seq_elem.text = seq

    tables_elem = ET.SubElement(root, 'Tables')
    for table_name, fields in tables.items():
        table_elem = ET.SubElement(tables_elem, 'Table', name=table_name)
        desc = table_descriptions.get(table_name, "")
        table_elem.set('description', desc)
        for field in fields:
            field_elem = ET.SubElement(table_elem, 'Field', name=field['name'], type=field['type'])

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def convert_df_to_html_and_xml(df_path, output_dir):
    sequences, tables, table_descriptions = parse_df_file(df_path)
    os.makedirs(output_dir, exist_ok=True)

    # Main HTML
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(generate_main_html(sequences, tables, table_descriptions))

    # Sequences HTML
    with open(os.path.join(output_dir, 'sequences.html'), 'w', encoding='utf-8') as f:
        f.write(generate_sequences_html(sequences))

    # Table HTMLs
    for table, fields in tables.items():
        desc = table_descriptions.get(table, "")
        with open(os.path.join(output_dir, f'{table}.html'), 'w', encoding='utf-8') as f:
            f.write(generate_table_html(table, fields, desc))

    # XML output
    xml_output_path = os.path.join(output_dir, 'schema.xml')
    generate_xml(sequences, tables, table_descriptions, xml_output_path)

if __name__ == "__main__":
    convert_df_to_html_and_xml(
        r'C:\Users\apas\OneDrive - Adient\Documents\Personal\AI\MapPlaces\schema.df',   'output_html'

    )