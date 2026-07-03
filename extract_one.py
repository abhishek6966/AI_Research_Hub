import sys
import json
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("Docling is not installed.", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) < 5:
        print("Usage: python extract_one.py <pdf_path> <tmp_json> <start_page> <end_page>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    tmp_json = sys.argv[2]
    start_page = int(sys.argv[3])
    end_page = int(sys.argv[4])

    if not pdf_path.exists():
        print(f"Error: {pdf_path} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize the AI model ONCE for this isolated chunk
        converter = DocumentConverter()
        
        # Convert the specific page range. This tuple format is mathematically exact and guaranteed to prevent Docling TypeError crashes.
        doc = converter.convert(pdf_path, page_range=(start_page, end_page)).document
        
        extracted_rows = []
        for item, level in doc.iterate_items():
            text = ""
            page_no = None
            if hasattr(item, 'label'):
                label_str = str(item.label)
            else:
                label_str = "text"
                
            if hasattr(item, 'text') and item.text:
                text = item.text.strip()
            elif hasattr(item, 'export_to_dataframe'):
                df = item.export_to_dataframe()
                if not df.empty:
                    text = df.to_string(index=False)
                    label_str = "table"
            
            if hasattr(item, 'prov') and item.prov:
                page_no = item.prov[0].page_no
            
            if text:
                extracted_rows.append({
                    "page": page_no,
                    "label": label_str,
                    "text": text
                })

        result_data = {
            "source": "docling",
            "rows": extracted_rows
        }

        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        print(f"Fatal error during isolated chunk extraction:\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
