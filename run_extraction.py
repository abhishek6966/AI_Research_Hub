import os
import re
import argparse
import csv
from pathlib import Path
from tqdm import tqdm
import time
import sys
import difflib

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    DocumentConverter = None

import pandas as pd

MAX_DOCLING_PAGES = 50

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    import pdfplumber
except ImportError:
    pdfplumber = None

# Default paths
DEFAULT_BASE_PATH = r"C:\Users\Mishra\Desktop\STEVENS INSTITUTE OF TECHNOLOGY\SUMMER 2027\Research Assistantship Work\Professionalism in AI Era - Data Collection - Abhishek"
DEFAULT_OUTPUT_PATH = r"C:\Users\Mishra\Desktop\STEVENS INSTITUTE OF TECHNOLOGY\SUMMER 2027\Research Assistantship Work\Extraction Output"

def create_organized_excels(base_dir=None):
    if base_dir is None:
        base_dir = Path(r"C:\Users\Mishra\Desktop\STEVENS INSTITUTE OF TECHNOLOGY\SUMMER 2027\Research Assistantship Work")
    
    # Run the separate formatter script
    import subprocess
    formatter_script = base_dir / "Text Conversion Tool" / "format_excel_company_yearly.py"
    if formatter_script.exists():
        subprocess.run([sys.executable, str(formatter_script)], check=True)

DOC_TYPE_MAP = {
    "1": (1, "Code of Conduct"),
    "2": (2, "Ethics & Compliance Policy"),
    "3": (3, "Responsible AI & AI Ethics Guidelines"),
    "4": (4, "SDG ESG Report"),
    "5": (5, "Annual Report"),
    "6": (6, "Earnings Call Transcript"),
    "7": (7, "Proxy Statement / Corp Gov Report"),
    "8": (8, "Supplier Code of Conduct"),
}

COMPANY_MASTER_MAP = {
    201: "John Deere", 202: "Nike", 203: "Banco Bradesco", 204: "Deutsche Post", 205: "Crédit Mutuel",
    206: "Bayer", 207: "Saint-Gobain", 208: "Volvo Group", 209: "Iberdrola", 210: "Veolia Environnement",
    211: "Bristol Myers Squibb", 212: "Landesbank Baden-Württemberg", 213: "General Dynamics", 214: "L'Oréal", 215: "Travelers",
    216: "Swiss Re", 217: "Eli Lilly", 218: "Orange", 219: "Telefónica", 220: "Woolworths",
    221: "Vodafone", 222: "DZ Bank", 223: "Dow", 224: "ANZ Group", 225: "Commonwealth Bank",
    226: "Thermo Fisher Scientific", 227: "Novo Nordisk", 228: "Abbott Laboratories", 229: "Standard Chartered", 230: "Inditex",
    231: "Best Buy", 232: "Schneider Electric", 233: "KB Financial Group", 234: "Northrop Grumman", 235: "National Australia Bank",
    236: "LyondellBasell", 237: "GSK", 238: "Cenovus Energy", 239: "Warner Bros", 240: "Netflix",
    241: "Qualcomm", 242: "Honeywell", 243: "Vale", 244: "Salesforce", 245: "Philip Morris",
    246: "Westpac Banking", 247: "AIA Group", 248: "SAP", 249: "Mondelez", 250: "Starbucks",
    251: "Visa", 252: "CBRE Group", 253: "ICICI Bank", 254: "International Airlines Group", 255: "PNC Financial",
    256: "Emirates", 257: "Cummins", 258: "Air France", 259: "Paccar", 260: "Metro Group",
    261: "BAE Systems", 262: "Amgen", 263: "Linde", 264: "ABB", 265: "Ecopetrol",
    266: "Medtronic", 267: "Heineken", 268: "JBS", 269: "Uniper", 270: "Korea Electric Power",
    271: "Itau Unibanco", 272: "Raizen", 273: "Energie Baden-Württemberg", 274: "CFE", 275: "Standard Bank",
    276: "Nedbank", 277: "Absa Group", 278: "Atlassian", 279: "ENBW", 280: "MTN Group",
    281: "RWE", 282: "KEPCO", 283: "Duke Energy", 284: "Air New Zealand", 285: "MercadoLibre",
    286: "Embraer", 287: "Wesfarmers", 288: "Sappi", 289: "Fortis", 290: "James Hardie",
    291: "Metalurgica Gerdau", 292: "Anywhere Real Estate", 293: "Sasol", 294: "Colliers International", 295: "Suncorp",
    296: "Grupo Argos", 297: "Adcorp", 298: "Warehouse Group", 299: "Nubank", 300: "Natura & Co"
}

def get_year_slot(year):
    try:
        year = int(year)
    except ValueError:
        return "unknown"
    if year <= 2014:   return "early"   # 2012, 2013, 2014
    if year <= 2018:   return "mid"     # 2015, 2016, 2017, 2018
    if year <= 2022:   return "recent"  # 2019, 2020, 2021, 2022
    return "current"                    # 2023, 2024, 2025, 2026

def parse_filename(filename):
    """Parses standard filenames: YYYY - Doc Type - Company_Name[_partX].ext"""
    ext = ""
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    
    parts = filename.rsplit(".", 1)[0].split(" - ")
    if len(parts) >= 3:
        year = parts[0][:4] # Ensure first 4 chars
        doctype_name = parts[1]
        company_raw = " - ".join(parts[2:])
    else:
        year = filename[:4] if filename[:4].isdigit() else "Unknown"
        doctype_name = "Unknown"
        company_raw = filename.rsplit(".", 1)[0]
        
    part = 1
    part_match = re.search(r'_part(\d+)$', company_raw, re.IGNORECASE)
    if part_match:
        part = int(part_match.group(1))
        company_raw = re.sub(r'_part\d+$', '', company_raw, flags=re.IGNORECASE)
    
    company = company_raw.replace('_', ' ').strip()
    return company, year, part, ext

def scan_files(base_path):
    files_to_process = []
    companies = set()
    doc_types_found = {}
    years_found = set()
    
    base_dir = Path(base_path)
    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_path}")
        return [], set(), {}, set()
        
    for doc_folder in base_dir.iterdir():
        if not doc_folder.is_dir(): continue
        
        match = re.match(r'^(\d+)', doc_folder.name)
        if not match: continue
        
        doc_type_key = match.group(1)
        if doc_type_key not in DOC_TYPE_MAP: continue
        
        doc_type_id, doc_type_name = DOC_TYPE_MAP[doc_type_key]
        if doc_type_name not in doc_types_found:
            doc_types_found[doc_type_name] = {'count': 0, 'years': set()}
            
        for year_folder in doc_folder.iterdir():
            if not year_folder.is_dir(): continue
            if not year_folder.name.isdigit(): continue
            
            year_str = year_folder.name
            years_found.add(year_str)
            
            for file_path in year_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt']:
                    company, year, part, ext = parse_filename(file_path.name)
                    # If year in filename doesn't match folder, use filename year
                    if year == "Unknown": year = year_str
                    
                    companies.add(company)
                    doc_types_found[doc_type_name]['count'] += 1
                    doc_types_found[doc_type_name]['years'].add(year)
                    
                    files_to_process.append({
                        'path': file_path,
                        'company': company,
                        'year': year,
                        'part': part,
                        'doc_type_id': doc_type_id,
                        'doc_type': doc_type_name,
                        'ext': ext
                    })
                    
    return files_to_process, companies, doc_types_found, years_found

def assign_company_ids(companies):
    mapping = {}
    
    # Create a lower-case lookup for the master list
    master_names = list(COMPANY_MASTER_MAP.values())
    master_names_lower = {name.lower(): cid for cid, name in COMPANY_MASTER_MAP.items()}
    
    unmatched_counter = 301 # Start assigning new IDs from 301 if they aren't in the list
    
    for comp in companies:
        comp_clean = comp.lower().replace('_', ' ').replace('-', ' ').strip()
        
        # Exact/Substring match first
        match_id = None
        for master_lower, cid in master_names_lower.items():
            if comp_clean in master_lower or master_lower in comp_clean:
                match_id = cid
                break
                
        # Fuzzy match fallback
        if not match_id:
            close_matches = difflib.get_close_matches(comp_clean, master_names_lower.keys(), n=1, cutoff=0.6)
            if close_matches:
                match_id = master_names_lower[close_matches[0]]
                
        if match_id:
            mapping[comp] = str(match_id)
        else:
            mapping[comp] = str(unmatched_counter)
            unmatched_counter += 1
            
    return mapping

def print_scan_results(files_to_process, companies, doc_types_found, years_found, base_path):
    print("\n=== SCAN RESULTS ===")
    print(f"Base path: {base_path}\n")
    
    print(f"Document folders found: {len(doc_types_found)}")
    print(f"Year folders found: {len(years_found)} total across all doc types")
    
    pdf_count = sum(1 for f in files_to_process if f['ext'] == 'pdf')
    txt_count = sum(1 for f in files_to_process if f['ext'] == 'txt')
    print(f"Files found: {pdf_count} PDFs, {txt_count} TXTs = {len(files_to_process)} total files")
    print(f"Companies detected: {len(companies)} unique companies\n")
    
    print("Breakdown by doc type:")
    for dt_name, dt_info in doc_types_found.items():
        print(f"  {dt_name[:25]:<25}: {dt_info['count']:>3} files across {len(dt_info['years'])} years")
    
    print("\nEstimated run time: ~" + str(int((pdf_count * 8 + txt_count * 1) / 60)) + " minutes (Docling averages 8 sec/PDF)")
    print("\nRun without --scan-only to begin extraction.")

def is_meaningful_paragraph(text):
    words = text.split()
    if len(words) < 10:
        return False
    return True

def extract_pdf_docling(pdf_path):
    import subprocess, tempfile, json, os, sys
    
    script_path = Path(__file__).parent / "extract_one.py"
    if not script_path.exists():
        return None, "extract_one.py not found"
        
    try:
        # Securely get total pages using lightweight pdfplumber before Docling touches it
        import pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
        except Exception as e:
            return None, f"PDF corrupted or unreadable by pdfplumber: {e}"
            
        CHUNK_SIZE = 5
        all_chunk_rows = []
        
        # Micro-chunking: Process only 5 pages at a time in a completely isolated process
        for start_page in range(1, total_pages + 1, CHUNK_SIZE):
            end_page = min(start_page + CHUNK_SIZE - 1, total_pages)
            
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                tmp_json = tmp.name
                
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), str(pdf_path), tmp_json, str(start_page), str(end_page)],
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour max per chunk
                )
            except subprocess.TimeoutExpired:
                if os.path.exists(tmp_json): os.remove(tmp_json)
                return None, f"Docling timed out on chunk {start_page}-{end_page}"
            
            if result.returncode != 0:
                if os.path.exists(tmp_json): os.remove(tmp_json)
                err_msg = result.stderr.strip() if result.stderr else "Unknown Docling crash (OOM)"
                print(f"\n[Docling Crash on {pdf_path.name} chunk {start_page}-{end_page}]:\n{err_msg}")
                return None, f"Docling crashed on chunk {start_page}-{end_page} (OOM)"
                
            with open(tmp_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if os.path.exists(tmp_json): os.remove(tmp_json)
            chunk_rows = data.get("rows", [])
            all_chunk_rows.extend(chunk_rows)
            
        final_rows = []
        for row in all_chunk_rows:
            text_val = row.get("text", "").strip()
            lbl = row.get("label", "text")
            
            if not text_val: continue
            
            # Filter out random numbers and short junk text to keep rows clean
            if text_val.isdigit() and len(text_val) < 5:
                continue
            if lbl == "text" and not is_meaningful_paragraph(text_val):
                continue
                
            final_rows.append({
                "index": len(final_rows),
                "page_no": row.get("page"),
                "label": lbl,
                "text": text_val,
                "char_length": len(text_val)
            })
            
        return final_rows, "docling"
        
    except Exception as e:
        import traceback
        error_tb = traceback.format_exc()
        print(f"\n[Subprocess Error on {pdf_path.name}]:\n{error_tb}")
        return None, str(e)

def extract_pdf_pdfplumber(pdf_path):
    rows = []
    row_counter = 0
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        line = line.strip()
                        if is_meaningful_paragraph(line):
                            rows.append({
                                "index": row_counter,
                                "page_no": page_num,
                                "label": "text",
                                "text": line,
                                "char_length": len(line)
                            })
                            row_counter += 1
        return rows, "pdfplumber"
    except Exception as e:
        return None, str(e)

def extract_txt(txt_path):
    rows = []
    encodings = ['utf-8', 'latin-1', 'cp1252']
    content = None
    used_encoding = None
    
    for enc in encodings:
        try:
            with open(txt_path, 'r', encoding=enc) as f:
                content = f.read()
            used_encoding = enc
            break
        except UnicodeDecodeError:
            continue
            
    if content is None:
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            used_encoding = 'utf-8-ignore'
        except Exception as e:
            return None, str(e)

    paragraphs = [p.strip() for p in content.split('\n\n') if is_meaningful_paragraph(p.strip())]
    for i, para in enumerate(paragraphs):
        rows.append({
            "index": i,
            "page_no": None,
            "label": "text",
            "text": para,
            "char_length": len(para)
        })
    return rows, f"txt ({used_encoding})"

def process_file(file_info):
    path = file_info['path']
    rows = []
    source_type = ""
    error_reason = ""
    
    if file_info['ext'] == 'txt':
        rows, source_type = extract_txt(path)
        if rows is None:
            error_reason = source_type # source_type holds error msg here
            rows = []
    elif file_info['ext'] == 'pdf':
        if DocumentConverter is not None:
            rows, source_type = extract_pdf_docling(path)
        else:
            rows, source_type = None, "Docling not installed"
            
        if rows is None:
            print(f"Docling failed on {path.name}: {source_type}. Falling back to OCR/pdfplumber...", flush=True)
            rows, source_type = extract_pdf_pdfplumber(path)
            
        if rows is None:
            error_reason = f"Docling & OCR failed: {source_type}"
            rows = []
                
    if rows:
        total_chars = sum(r['char_length'] for r in rows)
        if total_chars < 50:
            error_reason = f"Extracted < 50 chars ({total_chars} total)"
            rows = []
            
    return rows, source_type, error_reason, file_info

def deduplicate_rows(df):
    """Deduplicates rows where `text` is identical within the same company+doc_type+year group"""
    if df.empty: return df
    df = df.drop_duplicates(subset=['company', 'doc_type', 'year', 'text'], keep='first')
    return df

def main():
    parser = argparse.ArgumentParser(description="Professionalism in AI Era - Data Extraction")
    parser.add_argument("--scan-only", action="store_true", help="Scan folders without extracting")
    parser.add_argument("--company", type=str, help="Filter by specific company name")
    parser.add_argument("--company_id", type=str, help="Filter by specific company ID (e.g., 202)")
    parser.add_argument("--company_id_min", type=int, help="Filter by minimum company ID (inclusive)")
    parser.add_argument("--company_id_max", type=int, help="Filter by maximum company ID (inclusive)")
    parser.add_argument("--company_filter", type=str, help="Only process this specific company", default=None)
    parser.add_argument("--force", action="store_true", help="Force re-extraction of already processed files")
    parser.add_argument("--doctype", type=str, help="Filter by document type (1-8)")
    parser.add_argument("--year", type=str, help="Filter by specific year")
    parser.add_argument("--years", nargs="+", type=str, help="Filter by multiple years")
    parser.add_argument("--output-mode", choices=['combined', 'by-doctype', 'by-company'], default='combined', help="How to structure the output Excel files")
    parser.add_argument("--verbose", action="store_true", help="Show detailed progress")
    parser.add_argument("--limit", type=int, help="Limit the number of files to process")
    
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(DEFAULT_OUTPUT_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Scanning directories...")
    files_to_process, companies, doc_types_found, years_found = scan_files(DEFAULT_BASE_PATH)
    
    if args.company:
        files_to_process = [f for f in files_to_process if args.company.lower() in f['company'].lower()]
    if args.doctype:
        files_to_process = [f for f in files_to_process if str(f['doc_type_id']) == args.doctype]
    
    filter_years = []
    if args.year: filter_years.append(args.year)
    if args.years: filter_years.extend(args.years)
    if filter_years:
        files_to_process = [f for f in files_to_process if f['year'] in filter_years]
        
    company_id_map = assign_company_ids(companies)
    
    if args.company_id:
        files_to_process = [f for f in files_to_process if str(company_id_map.get(f['company'], '')) == str(args.company_id)]
        print(f"Filtered to {len(files_to_process)} files for company ID: {args.company_id}")
        
    if args.company_id_min is not None:
        files_to_process = [f for f in files_to_process if str(company_id_map.get(f['company'], '')).isdigit() and int(company_id_map.get(f['company'], '')) >= args.company_id_min]
        print(f"Filtered to {len(files_to_process)} files for company IDs >= {args.company_id_min}")
        
    if args.company_id_max is not None:
        files_to_process = [f for f in files_to_process if str(company_id_map.get(f['company'], '')).isdigit() and int(company_id_map.get(f['company'], '')) <= args.company_id_max]
        print(f"Filtered to {len(files_to_process)} files for company IDs <= {args.company_id_max}")
    
    if args.limit:
        files_to_process = files_to_process[:args.limit]
    
    if args.scan_only:
        print_scan_results(files_to_process, companies, doc_types_found, years_found, DEFAULT_BASE_PATH)
        return
        
    if not files_to_process:
        print("No files found matching criteria.")
        return
        
    if pdfplumber is None:
        print("Error: Missing required packages. Please install: pip install pdfplumber pandas openpyxl tqdm")
        return
    
    all_rows = []
    failed_files = []
    processed_file_names = set()
    
    csv_path = output_dir / "Company Data Extraction.csv"
    if csv_path.exists():
        try:
            existing_df = pd.read_csv(csv_path)
            all_rows = existing_df.to_dict('records')
            processed_file_names.update(existing_df['file_name'].dropna().tolist())
            print(f"Loaded {len(processed_file_names)} previously extracted files from autosave.")
        except Exception as e:
            print(f"Could not load previous extraction CSV: {e}")
            
    failed_csv = output_dir / "failed_extractions.csv"
    if failed_csv.exists():
        try:
            failed_df = pd.read_csv(failed_csv)
            if 'file_path' in failed_df.columns:
                processed_file_names.update([Path(p).name for p in failed_df['file_path'].dropna()])
            print(f"Loaded previously failed files from autosave.")
        except Exception:
            pass
            
    if processed_file_names and not args.force:
        original_count = len(files_to_process)
        files_to_process = [f for f in files_to_process if f['path'].name not in processed_file_names]
        print(f"Skipping {original_count - len(files_to_process)} already processed files.")
        
    if getattr(args, 'company_filter', None):
        files_to_process = [f for f in files_to_process if f['company'].lower() == args.company_filter.lower()]
        print(f"Filtered to {len(files_to_process)} files for company: {args.company_filter}")
        
    # ONLY extract target years to save hours of processing time
    # target_years = ['2015', '2020', '2025']
    # files_to_process = [f for f in files_to_process if str(f['year']) in target_years]
    # print(f"Filtered to {len(files_to_process)} remaining target year files (all years).")
    
    # Sort files by company ID to stream them sequentially by ID
    def get_sort_key(x):
        cid_str = company_id_map.get(x['company'], '999999')
        cid = int(cid_str) if cid_str.isdigit() else 999999
        return (cid, x['company'])
        
    files_to_process.sort(key=get_sort_key)
    
    start_time = time.time()
    print(f"\nStarting streaming extraction company-by-company...")
    
    current_company = None
    import subprocess
    formatter_script = Path(__file__).parent / "format_excel_company_only.py"
    
    with tqdm(total=len(files_to_process), disable=not args.verbose) as pbar:
        for idx, file_info in enumerate(files_to_process, start=1):
            current_company = file_info['company']
            
            extracted_rows, source_type, error_reason, file_info = process_file(file_info)
            
            path = file_info['path']
            company = file_info['company']
            doc_type = file_info['doc_type']
            year = file_info['year']
            part_str = f" (part{file_info['part']})" if file_info['part'] > 1 else ""
            
            if not extracted_rows:
                failed_files.append({
                    "file_path": str(path),
                    "company": company,
                    "doc_type": doc_type,
                    "year": year,
                    "reason": error_reason,
                    "file_size_kb": round(path.stat().st_size / 1024, 2)
                })
                if not args.verbose:
                    print(f"[{idx}/{len(files_to_process)}] FAILED: {company} / {doc_type} / {year}{part_str} -> {error_reason}")
                else:
                    pbar.write(f"[{idx}/{len(files_to_process)}] FAILED: {company} / {doc_type} / {year}{part_str} -> {error_reason}")
            else:
                formatted_rows = []
                file_name = path.name
                company_id = company_id_map.get(company, "")
                doc_type_id = file_info['doc_type_id']
                year_slot = get_year_slot(year)
                
                for r in extracted_rows:
                    yr_str = str(year)[-2:] if str(year).isdigit() and len(str(year)) >= 2 else str(year)
                    pg = r.get("page_no")
                    pg_str = str(pg) if pg is not None else "0"
                    
                    ref_id = f"{yr_str}.{company_id}.{doc_type_id}.{r['index']}.{pg_str}"
                    
                    full_row = {
                        "reference_id": ref_id,
                        "company": company,
                        "company_id": company_id,
                        "doc_type": doc_type,
                        "doc_type_id": doc_type_id,
                        "year": year,
                        "year_slot": year_slot,
                        "file_name": file_name,
                        "source_type": source_type,
                        "part": file_info['part'],
                        "index": r["index"],
                        "page_no": r["page_no"],
                        "label": r["label"],
                        "text": r["text"],
                        "char_length": r["char_length"]
                    }
                    formatted_rows.append(full_row)
                    
            # Instantly append to CSV auto-save right after EVERY file finishes!
            if formatted_rows:
                all_rows.extend(formatted_rows)
                # Save the master CSV safely
                pd.DataFrame(all_rows).to_csv(csv_path, index=False, encoding='utf-8')
                
                # Update Excel file every time a company fully finishes, or at the very end
                is_last_file = (idx == len(files_to_process))
                is_next_company_different = False
                if not is_last_file:
                    next_company = files_to_process[idx]['company']
                    is_next_company_different = (next_company != current_company)
                    
                if is_last_file or is_next_company_different:
                    try:
                        df_temp = pd.DataFrame(all_rows)
                        per_company_dir = output_dir / "Per_Company_Excel_Files"
                        per_company_dir.mkdir(exist_ok=True)
                        
                        comp_safe = re.sub(r'[\\/*?:\[\]]', '', current_company)
                        excel_path_temp = per_company_dir / f"{comp_safe}_extracted.xlsx"
                        
                        company_group = df_temp[df_temp['company'] == current_company]
                        with pd.ExcelWriter(excel_path_temp, engine='openpyxl') as writer:
                            for (dt_id, yr), sub_group in company_group.groupby(['doc_type_id', 'year']):
                                dt_id_str = str(dt_id)
                                dt_name_short = DOC_TYPE_MAP[dt_id_str][1].split()[0] if dt_id_str in DOC_TYPE_MAP else dt_id_str
                                sheet_name = f"{dt_name_short}_{yr}"[:31]
                                sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
                                sub_group.to_excel(writer, sheet_name=sheet_name, index=False)
                    except Exception as e:
                        pass
                
            pbar.update(1)        
            if extracted_rows:
                if not args.verbose:
                    print(f"[{idx}/{len(files_to_process)}] {company} / {doc_type} / {year}{part_str} -> {source_type} -> {len(extracted_rows):,} meaningful rows OK")
                else:
                    pbar.write(f"[{idx}/{len(files_to_process)}] {company} / {doc_type} / {year}{part_str} -> {source_type} -> {len(extracted_rows):,} meaningful rows OK")
        

        # Loop finished, so we must trigger the Excel generation for the very last company!
        if current_company is not None and all_rows:
            pd.DataFrame(all_rows).to_csv(csv_path, index=False, encoding='utf-8')
            print(f"\n[STREAMING] Finished extracting final company {current_company}! Generating Excel file...")
            if formatter_script.exists():
                subprocess.run([sys.executable, str(formatter_script), "--company", current_company], check=False)
    df = pd.DataFrame(all_rows)
    
    if not df.empty:
        # Deduplicate
        original_len = len(df)
        df = deduplicate_rows(df)
        dedup_len = len(df)
        if original_len != dedup_len:
            print(f"Removed {original_len - dedup_len:,} duplicate rows.")
            
        # Sort values
        df = df.sort_values(by=['company_id', 'doc_type_id', 'year', 'part', 'index'])
        
        # Drop internal part column
        df = df.drop(columns=['part'], errors='ignore')
        
        # Save flat CSV
        csv_path = output_dir / "Company Data Extraction.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"\nFlat CSV saved to: {csv_path}")
        
        # Export Excel based on output-mode
        if args.output_mode == 'combined':
            excel_path = output_dir / "Company Data Extraction.xlsx"
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for comp, group in df.groupby('company'):
                    sheet_name = comp[:31] # Excel limits sheet name to 31 chars
                    # Clean sheet name characters
                    sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
                    group.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Output saved to: {excel_path} ({df['company'].nunique()} sheets)")
            
        elif args.output_mode == 'by-doctype':
            for dt_id, dt_group in df.groupby('doc_type_id'):
                dt_name = DOC_TYPE_MAP[str(dt_id)][1].replace(' ', '_').replace('&', '').replace('/', '')
                excel_path = output_dir / f"{dt_id}_{dt_name}_extracted.xlsx"
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    for comp, comp_group in dt_group.groupby('company'):
                        sheet_name = comp[:31]
                        sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
                        comp_group.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Output saved to multiple files by doc type in {output_dir}")
            
        elif args.output_mode == 'by-company':
            for comp, comp_group in df.groupby('company'):
                comp_safe = re.sub(r'[\\/*?:\[\]]', '', comp)
                excel_path = output_dir / f"{comp_safe}_extracted.xlsx"
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    for (dt_id, yr), sub_group in comp_group.groupby(['doc_type_id', 'year']):
                        dt_name_short = DOC_TYPE_MAP[str(dt_id)][1].split()[0]
                        sheet_name = f"{dt_name_short}_{yr}"[:31]
                        sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
                        sub_group.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Output saved to multiple files by company in {output_dir}")

    # Save mapping and failures
    pd.DataFrame([{"company_name": k, "company_id": v} for k, v in company_id_map.items()]).to_csv(output_dir / "company_id_mapping.csv", index=False)
    
    if failed_files:
        pd.DataFrame(failed_files).to_csv(output_dir / "failed_extractions.csv", index=False, encoding='utf-8')
        
    elapsed = int(time.time() - start_time)
    mins = elapsed // 60
    secs = elapsed % 60
    
    print("\n=== EXTRACTION COMPLETE ===")
    print(f"Files processed: {len(files_to_process) - len(failed_files)} / {len(files_to_process)}")
    print(f"Files failed: {len(failed_files)} (see failed_extractions.csv)")
    if 'df' in locals() and not df.empty:
        print(f"Total rows extracted: {len(df):,}")
        print(f"Companies in output: {df['company'].nunique()}")
    print(f"Time elapsed: {int(elapsed//60)}m {int(elapsed%60)}s")
    
    print("\nExtraction streaming has completed.")

if __name__ == "__main__":
    main()
