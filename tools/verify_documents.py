"""Verify the delivered documents themselves, without running application requests."""
from pathlib import Path
from zipfile import ZipFile
import json
import re
import xml.etree.ElementTree as ET
from pypdf import PdfReader
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
OUT = DOCS / 'diagrams'
MODEL = json.loads((DOCS / 'source/model.json').read_text())
LANGUAGE = json.loads((DOCS / 'source/diagram-language.json').read_text())
NS = {'s': 'http://www.w3.org/2000/svg'}
results = {}

foreign_keys = {(entity, field) for entity, data in MODEL['entities'].items() for field, key, dtype in data['fields'] if 'FK' in key}
related_keys = {(child, fk) for parent, child, fk, p_kind, c_kind, label in MODEL['relations']}
assert foreign_keys == related_keys, 'Every foreign key must have a relationship.'
assert len(MODEL['relations']) == len(related_keys) == 12
assert len(MODEL['entities']) == 7
assert 'book_copies' not in MODEL['entities']
assert 'loan_renewals' not in MODEL['entities']
assert not any(field[0] in ['max_renewals','renewal_days'] for field in MODEL['entities']['lending_policies']['fields'])
assert all(field[0] != 'book_copy_id' for data in MODEL['entities'].values() for field in data['fields'])
assert next(field for field in MODEL['entities']['books']['fields'] if field[0] == 'isbn') == ['isbn', 'UK', 'varchar(20)']
assert not any(field[0] in ['quantity', 'stock', 'total_copies', 'inventory_code'] for field in MODEL['entities']['books']['fields'])
results['model'] = {'entities': 7, 'relationships': 12, 'all_foreign_keys_covered': True}

svg_files = sorted(OUT.glob('*.svg'))
assert len(svg_files) == 9
for path in svg_files:
    svg = ET.parse(path).getroot()
    assert svg.get('role') == 'img'
    assert svg[0].tag.endswith('title')
    ids = {element.get('id') for element in svg.iter() if element.get('id')}
    assert set(svg.get('aria-labelledby').split()) <= ids
    assert svg.find('s:desc', NS) is not None
    assert svg.findall('.//s:text', NS)
    assert not svg.findall('.//s:image', NS), 'SVG must contain editable vectors, not a bitmap.'
    width, height = map(float, [svg.get('width'), svg.get('height')])
    for element in svg.findall('.//s:text', NS):
        assert 0 <= float(element.get('x')) <= width
        assert 0 <= float(element.get('y')) <= height
    with Image.open(path.with_suffix('.png')) as image:
        scale = 2 if path.stem == '01-erd-lengkap' else 1
        assert image.size == (int(width) * scale, int(height) * scale), (path.name, image.size)
        image.verify()
    assert len(PdfReader(path.with_suffix('.pdf')).pages) == 1
results['diagrams'] = {'svg_png_pdf_sets': 9, 'editable_svg_text': True, 'accessible_names': True}
legacy_identifiers = set(LANGUAGE['identifiers'])
for path in OUT.glob('01*.svg'):
    values = {element.text or '' for element in ET.parse(path).findall('.//s:text', NS)}
    assert not values.intersection(legacy_identifiers), (path.name, values.intersection(legacy_identifiers))
for path in OUT.glob('0[2-7]-*.svg'):
    values = {element.text or '' for element in ET.parse(path).findall('.//s:text', NS)}
    assert {'Library Service', 'Database'} <= values
    assert values.intersection({'Web UI', 'Web PMP'})
    assert values.intersection({'Mahasiswa', 'Pustakawan'})
    assert any(value.startswith(('Pilih ', 'Verifikasi ', 'Masukkan ')) for value in values)
    assert not any(status in value for status in LANGUAGE['statuses'] for value in values)
results['diagram_language'] = {'english_erd': True, 'english_technical_components': True, 'indonesian_sequence_narrative': True}

source = (OUT / '01-erd-lengkap.mmd').read_text()
for parent, child, fk, p_kind, c_kind, label in MODEL['relations']:
    assert f': "{fk}"' in source
for path in sorted(OUT.glob('*.mmd')):
    if path.name.startswith('01'):
        continue
    body = path.read_text()
    assert body.startswith('sequenceDiagram')
    assert len(re.findall(r'^    (?:actor|participant) ', body, re.M)) == 4
    assert body.count('\n    alt ') == body.count('\n    else ') == body.count('\n    end') == 1
assert len(list(OUT.glob('*.mmd'))) == 6
results['mermaid'] = {'sources': 6, 'sequence_branch_balance': True}

brd_source = (DOCS / 'BRD-perpus-merah-putih.md').read_text()
erd_images = re.findall(r'!\[ERD [^\]]+\]\((diagrams/[^)]+\.png)\)', brd_source)
assert erd_images == ['diagrams/01-erd-lengkap.png']
brd_html = (DOCS / 'BRD-perpus-merah-putih.html').read_text()
for image_path in erd_images:
    assert f'src="{image_path}"' in brd_html

embedded_text = {
    element.text or ''
    for image_path in erd_images
    for element in ET.parse((DOCS / image_path).with_suffix('.svg')).findall('.//s:text', NS)
}
for entity, spec in MODEL['entities'].items():
    assert entity in embedded_text
    assert all(field in embedded_text for field, key, dtype in spec['fields'])

assert all(fk in embedded_text for parent, child, fk, p_kind, c_kind, label in MODEL['relations'])

brd_pdf = PdfReader(DOCS / 'BRD-perpus-merah-putih.pdf')
brd_text = '\n'.join(page.extract_text() for page in brd_pdf.pages)
cover_text = re.sub(r'\s+', ' ', brd_pdf.pages[0].extract_text())
for phrase in ['Perpus Merah Putih', 'PROJECT DOCUMENT', 'BUSINESS REQUIREMENTS', 'Draf untuk peninjauan']:
    assert phrase in cover_text
assert 'Table of contents' in brd_pdf.pages[1].extract_text()
results['cover'] = {'dedicated_first_page': True, 'contents_on_second_page': True}
for prefix, count in [('FR', 14), ('NFR', 7)]:
    for number in range(1, count+1):
        assert f'{prefix}-{number:02}' in brd_text, (prefix, number)
for phrase in ['Rp1.000', '5 hari', '2 hari', 'Acknowledgement & Approval']:
    assert phrase in brd_text, phrase
assert sum(len(page.images) for page in brd_pdf.pages) >= len(erd_images)
for heading in ['5.3. Entity Relationship Diagram']:
    assert heading in brd_text

with ZipFile(DOCS / 'BRD-perpus-merah-putih.docx') as docx:
    word_images = [docx.read(name) for name in docx.namelist() if name.startswith('word/media/')]
    for image_path in erd_images:
        assert (DOCS / image_path).read_bytes() in word_images

    results['brd_erd'] = {'embedded_views': 1, 'entities': 7, 'relationships': 12, 'formats': ['Markdown', 'HTML', 'Word', 'PDF']}
    document_xml = ET.fromstring(docx.read('word/document.xml'))
    word_ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    word_attr = '{' + word_ns['w'] + '}'
    assert len(word_images) == 1, 'The BRD must embed only the combined ERD.'
    landscape = document_xml.findall('.//w:sectPr/w:pgSz', word_ns)
    assert sum(size.get(word_attr + 'orient') == 'landscape' for size in landscape) == 1
    erd_pdf_pages = [page for page in brd_pdf.pages if page.images]
    assert len(erd_pdf_pages) == 1
    assert float(erd_pdf_pages[0].mediabox.width) > float(erd_pdf_pages[0].mediabox.height)
    tables = document_xml.findall('.//w:tbl', word_ns)
    assert len(tables) == 5
    for table in tables:
        for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = table.find(f'w:tblPr/w:tblBorders/w:{edge}', word_ns)
            assert border is not None and border.get(word_attr + 'val') == 'single'
        for cell in table.findall('.//w:tc', word_ns):
            for edge in ['top', 'left', 'bottom', 'right']:
                border = cell.find(f'w:tcPr/w:tcBorders/w:{edge}', word_ns)
                assert border is not None and border.get(word_attr + 'val') == 'single'
    results['word_tables'] = {'tables_with_all_borders': len(tables), 'all_cells_bordered': True}
    instructions = [element.text or '' for element in document_xml.findall('.//w:instrText', word_ns)]
    toc_fields = [instruction for instruction in instructions if instruction.strip().startswith('TOC ')]
    assert len(toc_fields) == 1
    assert '\\o "1-3"' in toc_fields[0] and '\\h' in toc_fields[0]
    toc_entries = []
    bookmark_names = {element.get(word_attr + 'name') for element in document_xml.findall('.//w:bookmarkStart', word_ns)}
    for paragraph in document_xml.findall('.//w:p', word_ns):
        style = paragraph.find('w:pPr/w:pStyle', word_ns)
        is_contents_entry = style is not None and style.get(word_attr + 'val') in ['TOC1', 'TOC2', 'TOC3']
        if not is_contents_entry:
            continue

        cached_text = ''.join(element.text or '' for element in paragraph.findall('.//w:t', word_ns)).strip()
        if not cached_text:
            continue

        assert re.search(r'\d+$', cached_text), f'TOC page number is missing: {cached_text}'
        links = paragraph.findall('.//w:hyperlink', word_ns)
        assert links and all(link.get(word_attr + 'anchor') in bookmark_names for link in links)
        toc_entries.append(cached_text)

    brd_source = (DOCS / 'BRD-perpus-merah-putih.md').read_text()
    expected_headings = re.findall(r'^#{2,4} (\d+\..+)$', brd_source, re.M)
    assert len(toc_entries) == len(expected_headings), f'Expected {len(expected_headings)} populated TOC entries, found {len(toc_entries)}.'
    for heading in expected_headings:
        assert any(entry.startswith(heading) for entry in toc_entries), f'TOC entry is missing: {heading}'
        entry = next(entry for entry in toc_entries if re.fullmatch(re.escape(heading) + r'\d+', entry))
        page_number = int(entry[len(heading):])
        assert 1 <= page_number <= len(brd_pdf.pages)
        page_text = re.sub(r'\s+', ' ', brd_pdf.pages[page_number-1].extract_text()).strip()
        assert heading in page_text, f'TOC page does not contain its heading: {entry}'
    assert len(re.findall(r'^## \d+\.', brd_source, re.M)) == 6
    detailed_spec = (DOCS / 'Spesifikasi-detail.md').read_text()
    assert all(f'BR-{number:02}' in detailed_spec for number in range(1, 17))
    document_styles = ET.fromstring(docx.read('word/styles.xml'))
    for style_name in ['TOC1', 'TOC2', 'TOC3']:
        style = document_styles.find(f'w:style[@w:styleId="{style_name}"]', word_ns)
        tab = style.find('w:pPr/w:tabs/w:tab', word_ns)
        assert tab.get(word_attr + 'leader') == 'dot'
        assert tab.get(word_attr + 'val') == 'right'
    settings_xml = ET.fromstring(docx.read('word/settings.xml'))
    update_fields = settings_xml.find('w:updateFields', word_ns)
    if update_fields is not None:
        assert update_fields.get(word_attr + 'val') in ['true', '1']

    results['word_contents'] = {'native_toc_fields': 1, 'heading_levels': 3, 'populated_linked_entries': len(toc_entries), 'dot_leaders': True, 'page_numbers_cached': True}
combined = PdfReader(DOCS / 'Diagram-Perpus-Merah-Putih.pdf')
assert len(combined.pages) == 9
results['documents'] = {'brd_pdf_pages': len(brd_pdf.pages), 'diagram_pdf_pages': 9, 'docx_xml_valid': True}

with ZipFile(ROOT / 'docs' / 'Perpus Merah Putih — BRD dan diagram.figcraft') as native:
    assert native.testzip() is None
    document = json.loads(native.read('document.json'))
    assert len(document['pages']) == 6
    text_nodes = [node for node in document['nodes'].values() if node.get('type', '').lower() == 'text']
    assert len(text_nodes) > 200
    for node in text_nodes:
        assert not any(re.search(r'\b' + status + r'\b', node.get('characters', '')) for status in LANGUAGE['statuses']), node.get('characters')
    assert not any('book_copies' in node.get('characters','') or 'book_copy_id' in node.get('characters','') for node in text_nodes)
    assert any(node.get('characters') == 'Web PMP' for node in text_nodes)
    assert any(node.get('characters') == 'Simpan sebagai WAITING atau QUEUED' for node in text_nodes)
    complete_page = next(document['nodes'][str(page)] for page in document['pages'] if document['nodes'][str(page)]['name'] == '06 · Complete ERD')
    complete_frame = next(node for node in document['nodes'].values() if node.get('name') == 'Complete ERD · Perpus Merah Putih' and node.get('type') == 'frame')
    assert complete_frame['id'] in complete_page['children']
    descendants = set(complete_frame['children'])
    complete_text = [node.get('characters', '') for key, node in document['nodes'].items() if node['id'] in descendants and node.get('type') == 'text']
    for entity, spec in MODEL['entities'].items():
        assert complete_text.count(entity) == 1
        assert all(field in complete_text for field, key, dtype in spec['fields'])

    results['figcraft'] = {'pages': 6, 'editable_text_nodes': len(text_nodes)}

with ZipFile(DOCS / 'Perpus-Merah-Putih-dokumen.zip') as bundle:
    assert bundle.testzip() is None
    names = bundle.namelist()
    assert 'docs/BRD-perpus-merah-putih.pdf' in names
    assert 'docs/Diagram-Perpus-Merah-Putih.pdf' in names
    assert 'docs/Perpus Merah Putih — BRD dan diagram.figcraft' in names
    assert bundle.read('docs/BRD-perpus-merah-putih.docx') == (DOCS / 'BRD-perpus-merah-putih.docx').read_bytes()
results['archive'] = {'integrity': 'passed'}
print(json.dumps(results, indent=2))
