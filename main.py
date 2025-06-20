import sys
import os

from libs.pasParser import read_pas_files
from libs.plantUMLConverter import dataframes_to_plantuml


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input.pas> <output.puml>")
        return

    input = os.path.abspath(sys.argv[1])
    output = os.path.abspath(sys.argv[2])

    print("Usage: python pas-files to plantuml parser.")
    print(f"input:  {input}")
    print(f"output: {output} ")

    df_classes, df_members = read_pas_files(input)
    # print(df_classes.head().to_string())
    # print(df_members.head().to_string())
    plantuml_text = dataframes_to_plantuml(df_classes, df_members)

    if os.path.isfile(input):
        basename = os.path.splitext(os.path.basename(input))[0]
        output_file = os.path.join(output, basename + ".puml")
    else:
        output_file = os.path.join(output, "all_results.puml")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(plantuml_text)

    print(f"PlantUML written to {output_file}")

if __name__ == "__main__":
    main()
