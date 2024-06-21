import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import re

# Input files
file1 = 'ref_ICLpaper.bib'
file2 = 'ref_CDMpaper.bib'
file3 = 'ref_insituPaper.bib'

# Output file
output_file = 'merged_and_cleaned.bib'
manuscript_file = 'manuscript.tex'
final_manuscript = 'manuscript_final.tex'

# Function to read and parse a .bib file
def read_bib_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(f, parser=parser)
    return bib_database


# Function to check DOI and adsurl keys
def check_keys(bib_database, filename):
    for i, entry in enumerate(bib_database.entries, start=1):
        entry_type = entry['ENTRYTYPE']
        if entry_type in ['article', 'inproceedings']:
            key = entry.get('doi', '')
            if not key:
                print(f"Error: Entry {i} ({entry_type}) in {filename} is missing a 'doi' key.")
        else:
            print(f"Entry {i} ({entry_type}) in {filename} does not have a DOI!")
            key = entry.get('adsurl', '')
            print(f"  'adsurl': {key}")


# Function to remove duplicates based on doi or adsurl
def remove_duplicates(bib_database):
    unique_entries = []
    seen_entries = {}
    duplicate_IDs = []

    for entry in bib_database.entries:
        entry_type = entry['ENTRYTYPE']
        key = entry.get('doi', '') if entry_type in ['article', 'inproceedings'] else entry.get('adsurl', '')
        ID = entry.get('ID', '')

        if key:
            if key not in seen_entries:
                seen_entries[key] = [ID]
                unique_entries.append(entry)
            else:
                seen_entries[key].append(ID)
                duplicate_IDs.append((seen_entries[key][0], ID))

    return unique_entries, duplicate_IDs


# Function to replace duplicates in a manuscript
def replace_duplicates_in_manuscript(file_path, duplicate_IDs, final_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for original_id, duplicate_id in duplicate_IDs:
        if original_id != duplicate_id:
            # Replace only when it is a standalone word (useful for replacing a year-only alias)
            content = re.sub(r'\b' + re.escape(duplicate_id) + r'\b', original_id, content)

    with open(final_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Main script
def main():
    # Read and parse all input .bib files
    bib_database1 = read_bib_file(file1)
    bib_database2 = read_bib_file(file2)
    bib_database3 = read_bib_file(file3)

    # Check DOI and adsurl keys in the databases
    check_keys(bib_database1, 'file 1')
    check_keys(bib_database2, 'file 2')
    check_keys(bib_database3, 'file 3')

    # Combine all databases
    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = bib_database1.entries + bib_database2.entries + bib_database3.entries

    check_keys(bib_database, 'combined')

    # Remove duplicates
    unique_entries, duplicate_IDs = remove_duplicates(bib_database)

    # Write unique entries to the output .bib file
    with open(output_file, 'w', encoding='utf-8') as f:
        writer = bibtexparser.bwriter.BibTexWriter()
        new_bib_database = bibtexparser.bibdatabase.BibDatabase()
        new_bib_database.entries = unique_entries
        f.write(writer.write(new_bib_database))

    # Replace duplicates in the manuscript
    replace_duplicates_in_manuscript(manuscript_file, duplicate_IDs, final_manuscript)

if __name__ == "__main__":
    main()
