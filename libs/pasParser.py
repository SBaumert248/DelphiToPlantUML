import os
import re
import pandas as pd
from pandas import DataFrame


def parse_class_members(lines, start_line, end_line):
    visibility = None
    members = []

    visibility_keywords = ['private', 'protected', 'public', 'published']

    for i in range(start_line-1, end_line):
        line = lines[i].strip()
        lower = line.lower()

        if lower in visibility_keywords:
            visibility = lower
            continue

        # Nur innerhalb einer Sichtbarkeitssektion erfassen
        if visibility:
            # Funktionen/Prozeduren
            if re.match(r'^(procedure|function)\s+\w+', line):
                members.append((visibility, 'method', line))

            # Properties
            elif line.startswith('property '):
                members.append((visibility, 'property', line))

    return members

def parse_pas_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    class_entries = []
    all_members = []

    inside_class = False
    class_definition_line = False
    class_name = ''
    parent_class = ''
    start_line = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Start einer Klasse erkennen
        match = re.match(r'(\w+)\s*=\s*class\s*(?:\((\w+)?\))?', stripped, re.IGNORECASE)
        if match:
            class_name = match.group(1)
            parent_class = match.group(2) if match.lastindex >= 2 else ''
            start_line = i + 1
            inside_class = True
            # Erkennt wenn es nur eine single line Definition ist, z.B. TMyObj = class(TParentObj);
            if stripped.endswith(');'):
                class_definition_line = True
            else:
                continue

        # Ende der Klasse erkennen
        if (inside_class and stripped.lower() == 'end;') or class_definition_line:
            end_line = i + 1
            class_entries.append({
                'className': class_name,
                'parentClassName': parent_class,
                'classFileRowStart': start_line,
                'classFileRowEnd': end_line,
                'filename': os.path.basename(filepath)
            })

            # Mitglieder parsen
            if not class_definition_line:
                members = parse_class_members(lines, start_line, end_line)
                for vis, kind, signature in members:
                    all_members.append({
                        'className': class_name,
                        'visibility': vis,
                        'memberType': kind,
                        'signature': signature,
                        'filename': os.path.basename(filepath)
                    })

            inside_class = False
            class_definition_line = False

    return class_entries, all_members

def parse_all_pas_files(directory):
    all_classes = []
    all_members = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pas'):
                filepath = os.path.join(root, file)
                class_data, member_data = parse_pas_file(filepath)
                all_classes.extend(class_data)
                all_members.extend(member_data)

    df_classes = pd.DataFrame(all_classes)
    df_members= pd.DataFrame(all_members)

    return df_classes, df_members

def read_pas_files(path: str):
    if os.path.isdir(path):
        df_classes, df_members = parse_all_pas_files(path)
    else:
        list_classes, list_members = parse_pas_file(path)
        df_classes = pd.DataFrame(list_classes)
        df_members = pd.DataFrame(list_members)
    return df_classes, df_members
