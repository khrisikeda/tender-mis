import sys, os, json
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

from app.services.document_extractor import TenderDocumentExtractor

files = [
    'DAO supply of non contact tonometer on behalf of UR-HG LTD-Readvertised.doc',
    'DAO supply of gym equipment on behalf of UR-HG LTD.doc'
]

for filename in files:
    with open(filename, 'rb') as f:
        data = f.read()
    
    extracted = TenderDocumentExtractor.extract_from_file(data, filename)
    print('=================================================================')
    print('FILE:', filename)
    print('METADATA:', json.dumps(extracted['metadata'], indent=2))
    print('ITEMS EXTRACTED:', len(extracted['items']))
    for item in extracted['items']:
        specs_count = len(item.get('specs', []))
        matrix_count = len(item.get('specs_matrix', []))
        print(f"  - [{item.get('lot_id')}] {item.get('name')} (Qty: {item.get('quantity')}, Specs: {specs_count}, Matrix: {matrix_count})")
    print('TOTAL SPEC MATRIX ROWS:', len(extracted['spec_matrix']))
