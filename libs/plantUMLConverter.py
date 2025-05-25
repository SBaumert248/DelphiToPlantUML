import pandas as pd

def dataframes_to_plantuml(df_classes, df_members) -> str:
    lines = ["@startuml",
             "'+ property",
             "'- private",
             "'# protected",
             "'+ public",
             "'~ published",
             ""]

    for _, cls in df_classes.iterrows():
        class_name = cls["className"]
        lines.append(f"class {class_name} {{")

        # Alle Mitglieder dieser Klasse
        members = df_members[df_members["className"] == class_name]

        # Sichtbarkeitsreihenfolge
        visibility_order = ["published", "public", "protected", "private"]
        vis_map = {
            "private": "-",
            "protected": "#",
            "public": "+",
            "published": "~"  # frei wählbar für Delphi
        }

        for visibility in visibility_order:
            vis_members = members[members["visibility"] == visibility]

            if vis_members.empty:
                continue

            # Methoden alphabetisch sortieren
            methods = vis_members[vis_members["memberType"] == "method"] \
                .sort_values(by="signature", key=lambda col: col.str.lower())

            for _, member in methods.iterrows():
                signature = member["signature"].strip().rstrip(';')
                lines.append(f"    {vis_map[visibility]} {signature}")

            # Properties alphabetisch sortieren
            properties = vis_members[vis_members["memberType"] == "property"] \
                .sort_values(by="signature", key=lambda col: col.str.lower())

            for _, member in properties.iterrows():
                signature = member["signature"].strip().rstrip(';')
                lines.append(f"    {vis_map[visibility]} {signature}")

        lines.append("}")
        lines.append("")

    # Vererbungen
    for _, row in df_classes.iterrows():
        parent = row["parentClassName"]
        child = row["className"]
        if pd.notna(parent) and parent:
            lines.append(f"{parent} <|-- {child}")

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)
