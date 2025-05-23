import re
import sys
import os

def parse_pas_file(filename):
    with open(filename, 'r') as file:
        content = file.read()

    # Entferne Kommentare
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\{.*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\(\*.*?\*\)', '', content, flags=re.DOTALL)

    classes = []
    for match in re.finditer(r'(T\w+)\s*=\s*class\s*\((.*?)\)(.*?)end;', content, re.DOTALL | re.IGNORECASE):
        class_name = match.group(1)
        base_class = match.group(2).strip()
        body = match.group(3)

        class_info = {
            'name': class_name,
            'base': base_class if base_class.lower() != 'tobject' else None,
            'fields': [],
            'methods': [],
        }

        current_visibility = 'public'
        for line in body.splitlines():
            line = line.strip()
            if line.lower() in ['public', 'private', 'protected', 'published']:
                current_visibility = line.lower()
                continue

            # Simple field detection
            field_match = re.match(r'(\w+)\s*:\s*([^;]+);', line)
            if field_match:
                name, type_ = field_match.groups()
                class_info['fields'].append((current_visibility, name, type_.strip()))
                continue

            # Simple method detection
            method_match = re.match(r'(procedure|function)\s+(\w+)\s*(\(.*?\))?\s*[:;]', line, re.IGNORECASE)
            if method_match:
                kind, name, args = method_match.groups()
                args = args or ''
                class_info['methods'].append((current_visibility, name, kind.lower(), args.strip()))

        classes.append(class_info)

    return classes

def generate_plantuml(classes):
    lines = ["@startuml"]

    for cls in classes:
        lines.append(f"class {cls['name']} {{")

        for vis, name, type_ in cls['fields']:
            vis_symbol = {'public': '+', 'private': '-', 'protected': '#', 'published': '+'}.get(vis, '~')
            lines.append(f"    {vis_symbol} {name} : {type_}")

        for vis, name, kind, args in cls['methods']:
            vis_symbol = {'public': '+', 'private': '-', 'protected': '#', 'published': '+'}.get(vis, '~')
            method_sig = f"{name}{args}"
            lines.append(f"    {vis_symbol} {method_sig}")

        lines.append("}")

        if cls['base']:
            lines.append(f"{cls['base']} <|-- {cls['name']}")

    lines.append("@enduml")
    return '\n'.join(lines)

def main():
    if len(sys.argv) != 3:
        print("Usage: python pas_to_plantuml.py <input.pas> <output.puml>")
        return

    input_file = os.path.abspath(sys.argv[1])
    output_file = os.path.abspath(sys.argv[2])

    classes = parse_pas_file(input_file)
    plantuml_text = generate_plantuml(classes)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(plantuml_text)

    print(f"PlantUML written to {output_file}")

if __name__ == "__main__":
    main()
