import csv
import re
import sys

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

# This script requires 'filled.sql' which can be obtained from:
# https://github.com/Quran-Journey/roots/blob/master/db/filled.sql
FILLED_SQL_PATH = 'filled.sql'
TSV_PATH = 'quran_word_translation.tsv'
OUTPUT_TSV_PATH = 'quran_word_translation_v2.tsv'

def normalize_common(text, keep_marks):
    chars = []
    for c in text:
        cp = ord(c)
        if 0x0621 <= cp <= 0x064A:
            # Check exclusions
            # 0621 Hamza
            # 0624 Hamza on Waw
            # 0626 Hamza on Yeh
            # 0640 Tatweel
            if cp in [0x0621, 0x0624, 0x0626, 0x0640]:
                continue

            # Alif variants -> Alif
            elif cp in [0x0622, 0x0623, 0x0625, 0x0649]:
                chars.append('\u0627')
            else:
                chars.append(c)
        elif cp == 0x0671: # Wasla -> Alif
            chars.append('\u0627')
        elif cp == 0x0670: # Superscript Alef -> Keep for variants
            chars.append(c)

        # Small letters (markers for long vowels)
        elif cp == 0x06E5: # Small Waw
            if keep_marks: chars.append('\u0648')
        elif cp == 0x06E6: # Small Yeh
            if keep_marks: chars.append('\u064A')
        elif cp == 0x06E7: # Small High Yeh
            if keep_marks: chars.append('\u064A')
        # Skip others

    res = "".join(chars)
    # Collapse consecutive Alifs (e.g. Alif Maksura + Superscript Alef -> Alif Alif -> Alif)
    res = re.sub(r'\u0627+', '\u0627', res)
    return res

def generate_variants(text):
    bases = set()
    bases.add(normalize_common(text, keep_marks=True))
    bases.add(normalize_common(text, keep_marks=False))

    variants = set()
    for b in bases:
        # Case 1: 0670 -> Alif
        v1 = b.replace('\u0670', '\u0627')
        # Normalize Alifs again
        v1 = re.sub(r'\u0627+', '\u0627', v1)
        variants.add(v1)

        # Case 2: 0670 -> Empty
        v2 = b.replace('\u0670', '')
        v2 = re.sub(r'\u0627+', '\u0627', v2)
        variants.add(v2)

    # Additional patches for common mismatches
    extended_variants = set(variants)
    for v in variants:
        # Al-Layl patch: 'اليل' -> 'الليل'
        if 'اليل' in v:
            extended_variants.add(v.replace('اليل', 'الليل'))

        # Defective Ya patch: Ends in Ya -> Try Double Ya
        if v.endswith('\u064A'):
            extended_variants.add(v + '\u064A')

    return extended_variants

def parse_sql_dump(filepath):
    tables = {
        'rootword': {}, # id -> root_text
        'arabicword': {}, # id -> {text, root_id}
        'quran_text': {}, # index -> {sura, aya} (map to index)
        'texttoword': {}  # index -> [word_id, word_id, ...]
    }

    sura_aya_to_index = {}
    current_table = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('COPY public.'):
                if 'public.rootword' in line:
                    current_table = 'rootword'
                elif 'public.arabicword' in line:
                    current_table = 'arabicword'
                elif 'public.quran_text' in line:
                    current_table = 'quran_text'
                elif 'public.texttoword' in line:
                    current_table = 'texttoword'
                else:
                    current_table = None
                continue

            if line == r'\.':
                current_table = None
                continue

            if current_table:
                parts = line.split('\t')

                if current_table == 'rootword':
                    if len(parts) >= 2:
                        rid = int(parts[0])
                        rword = parts[1].replace(' ', '')
                        tables['rootword'][rid] = rword

                elif current_table == 'arabicword':
                    if len(parts) >= 3:
                        wid = int(parts[0])
                        word = parts[1]
                        rid = int(parts[2])
                        tables['arabicword'][wid] = {'text': word, 'root_id': rid}

                elif current_table == 'quran_text':
                    if len(parts) >= 3:
                        idx = int(parts[0])
                        sura = int(parts[1])
                        aya = int(parts[2])
                        tables['quran_text'][idx] = {'sura': sura, 'aya': aya}
                        sura_aya_to_index[(sura, aya)] = idx

                elif current_table == 'texttoword':
                    if len(parts) >= 2:
                        idx = int(parts[0])
                        wid = int(parts[1])
                        if idx not in tables['texttoword']:
                            tables['texttoword'][idx] = []
                        tables['texttoword'][idx].append(wid)

    return tables, sura_aya_to_index

def main():
    print("Parsing SQL dump...")
    tables, sura_aya_to_index = parse_sql_dump(FILLED_SQL_PATH)
    print(f"Loaded {len(tables['rootword'])} roots.")
    print(f"Loaded {len(tables['arabicword'])} arabic words.")
    print(f"Loaded {len(tables['quran_text'])} verses.")

    print("Processing TSV...")

    with open(TSV_PATH, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_TSV_PATH, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile, delimiter='\t')
        fieldnames = reader.fieldnames
        if 'root' not in fieldnames:
            fieldnames = fieldnames + ['root']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')

        writer.writeheader()

        matches = 0
        total = 0
        missing = 0

        ayah_cache = {}

        for row in reader:
            total += 1
            sura = int(row['surah'])
            ayah = int(row['ayah'])
            ar_text = row['ar']

            idx = sura_aya_to_index.get((sura, ayah))
            root_found = ""

            if idx:
                if idx not in ayah_cache:
                    word_ids = tables['texttoword'].get(idx, [])
                    words_data = []
                    for wid in word_ids:
                        aw_entry = tables['arabicword'].get(wid)
                        if aw_entry:
                            rid = aw_entry['root_id']
                            rword = tables['rootword'].get(rid, "")
                            sql_text = aw_entry['text']
                            variants = generate_variants(sql_text)
                            words_data.append({
                                'variants': variants,
                                'root': rword,
                                'original': sql_text
                            })
                    ayah_cache[idx] = words_data

                tsv_variants = generate_variants(ar_text)

                for candidate in ayah_cache[idx]:
                    if not candidate['variants'].isdisjoint(tsv_variants):
                         root_found = candidate['root']
                         break

            if root_found:
                matches += 1
            else:
                missing += 1
                if missing <= 10:
                     print(f"Missing: {sura}:{ayah} {ar_text} (Variants: {generate_variants(ar_text)})")
                     if idx in ayah_cache:
                         print(f"  Candidates: {[list(c['variants'])[0] for c in ayah_cache[idx]]}")

            row['root'] = root_found
            writer.writerow(row)

    print(f"Total words: {total}")
    print(f"Matches found: {matches}")
    print(f"Missing roots: {missing}")
    print(f"Success rate: {matches/total*100:.2f}%")

if __name__ == "__main__":
    main()
