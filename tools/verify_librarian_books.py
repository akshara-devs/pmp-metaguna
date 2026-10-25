"""Verify the final one-book-per-ISBN design, navigation, and published exports."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/librarian-books'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--file', type=Path, default=ROOT / 'docs/Perpus Merah Putih.figcraft')
with ZipFile(parser.parse_args().file) as archive:
    assert archive.testzip() is None
    doc = json.loads(archive.read('document.json'))

nodes = doc['nodes']
assets = json.loads((OUT / 'assets.json').read_text())
frames = assets['frames']
assert set(frames) == {'list', 'add', 'detail', 'edit', 'isbn-error', 'deactivate', 'empty', 'list-collapsed'}
page = nodes[str(assets['page'])]
assert {i for i in page['children'] if nodes[str(i)]['type'] == 'frame'} == set(frames.values())
assert page['flows'][0]['start'] == frames['list']
assert len(doc['pages']) == 6
variables = {v['id'] for v in doc['variables']['variables']}


def descendants(ident):
    node = nodes[str(ident)]
    return [node] + [item for child in node.get('children', []) for item in descendants(child)]


texts = '\n'.join(n.get('characters', '') for n in nodes.values())
for stale in ['Tambah eksemplar', 'Edit eksemplar', 'Kode inventaris', 'Total eksemplar', 'Maksimal perpanjangan', 'Tambahan perpanjangan']:
    assert stale not in texts, stale

assert not re.search(r'\d+ eksemplar', texts)
assert not any('Book copies' in n['name'] for n in nodes.values())
assert len([n for n in nodes.values() if n['name'].startswith('Policy input /')]) == 4
assert 'ISBN sudah digunakan. Masukkan ISBN yang berbeda.' in texts
for key in ['add', 'edit', 'isbn-error']:
    assert any(n.get('characters') == 'ISBN *' for n in descendants(frames[key]))

for key in ['detail', 'deactivate']:
    screen = descendants(frames[key])
    assert any(n.get('characters') == 'Status buku' for n in screen)
    assert not any(n['name'].startswith('Table / Book copies') for n in screen)

for key in ['list', 'empty', 'list-collapsed']:
    summary = next(n for n in descendants(frames[key]) if n['name'] == 'Collection summary')
    stats = [nodes[str(i)] for i in summary['children'] if nodes[str(i)]['name'] == 'Collection statistic']
    values = [[n['characters'] for n in descendants(stat['id']) if n['type'] == 'text'] for stat in stats]
    assert [row[0] for row in values] == ['Jumlah buku', 'Tersedia', 'Dipinjam', 'Siap diambil']
    assert [row[1] for row in values] == ['48', '20', '18', '8']
    assert int(values[0][1]) == sum(int(row[1]) for row in values[1:]) + 2
    table = next(n for n in descendants(frames[key]) if n['name'] == 'Table / Books')
    header = next(nodes[str(i)] for i in table['children'] if nodes[str(i)]['name'] == 'TableHeader')
    assert len(header['children']) == 4

instance_count = 0
button_count = 0
for ident in frames.values():
    for node in descendants(ident):
        for child in node.get('children', []):
            assert nodes[str(child)]['parent'] == node['id']
        for variable in node.get('bound', {}).values():
            assert variable in variables
        if node['type'] == 'instance':
            instance_count += 1
            assert nodes[str(node['component'])]['type'] == 'component'
            if node['name'].startswith('Button /'):
                button_count += 1
                assert node['height'] == 36
                for child in [nodes[str(i)] for i in node['children'] if nodes[str(i)]['type'] == 'text']:
                    assert abs(child['transform'][5] - (36 - child['height']) / 2) < .01

for ident, target in assets['links']:
    current = nodes[str(ident)]
    seen = set()
    while not current.get('interactions'):
        assert current['id'] not in seen
        seen.add(current['id'])
        current = nodes[str(current['source'])]
    assert any(action['type'] == 'navigate' and action['dest'] == frames[target] for interaction in current['interactions'] for action in interaction['actions'])

for mode in ['light', 'dark']:
    assert len(PdfReader(OUT / f'Librarian-books-{mode}.pdf').pages) == 8
    for key, ident in frames.items():
        frame = nodes[str(ident)]
        assert (frame['width'], frame['height']) == (1440, 1000)
        with Image.open(OUT / f'{key}-{mode}.png') as image:
            assert image.size == (1440, 1000)
            image.verify()
        svg = ET.parse(OUT / f'{key}-{mode}.svg').getroot()
        assert len(svg.findall('.//{http://www.w3.org/2000/svg}text')) > 20
        for state in ['expanded', 'collapsed']:
            with Image.open(OUT / f'responsive-{key}-{state}-{mode}.png') as image:
                assert image.size == (1440, 1000)
                image.verify()

assert 'ISBN sudah digunakan' in (OUT / 'isbn-error-light.svg').read_text()
assert '1 pinjaman aktif tetap dapat dikembalikan' in (OUT / 'deactivate-light.svg').read_text()
assert 'Buku tidak ditemukan' in (OUT / 'empty-light.svg').read_text()
report = {'result': 'passed', 'screens': 8, 'modes': ['Light', 'Dark'], 'one_physical_book_per_isbn': True, 'isbn_required_and_unique': True, 'copy_inventory_removed': True, 'loan_renewals_removed': True, 'lending_policy_controls': 4, 'native_instances': instance_count, 'centered_buttons': button_count, 'navigation_links': len(assets['links']), 'responsive_pngs': 32, 'pdf_pages': 16}
(OUT / 'verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
