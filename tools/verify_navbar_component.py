"""Check native navbar instances, editable text, and sidebar-driven resizing."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/librarian-books'
CLI = '/Users/macbookpro/.local/bin/figcraft-cli'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--file', type=Path, default=ROOT / 'docs' / 'Perpus Merah Putih.figcraft')
file = parser.parse_args().file
assets = json.loads((OUT / 'navbar-assets.json').read_text())
screens = json.loads((OUT / 'assets.json').read_text())


def read(path):
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        return json.loads(archive.read('document.json'))


def check(doc):
    nodes = doc['nodes']
    master = nodes[str(assets['component'])]
    assert master['type'] == 'component' and master['name'] == 'Navbar'
    assert master['layout']['mode'] == 'horizontal'
    assert set(master['props']) == {'Breadcrumb', 'Date'}
    for ident in assets['instances']:
        n = nodes[str(ident)]
        inset = nodes[str(n['parent'])]
        assert n['type'] == 'instance' and n['component'] == master['id']
        assert n['width'] == inset['width']
        assert n['height'] == 69
        assert n.get('transform', [1, 0, 0, 1, 0, 0])[4:] == [0, 0]
        assert n['constraints']['horizontal'] == 'leftRight'
        divider = next(nodes[str(i)] for i in n['children'] if nodes[str(i)]['name'] == 'Separator')
        assert divider['width'] == n['width'] and divider['transform'][5] == 68
    assert len(assets['instances']) == 8


doc = read(file)
check(doc)
first = assets['instances'][0]
sidebar = json.loads((OUT / 'sidebar-assets.json').read_text())['instances'][0]
with tempfile.TemporaryDirectory(prefix='pmp-navbar-') as folder:
    temp = Path(folder)
    plan = [
        {'command': 'instance.setProperties', 'params': {'ids': [sidebar], 'properties': {'State': 'Collapsed'}}},
        {'command': 'instance.setProperties', 'params': {'ids': [first], 'properties': {'Breadcrumb': 'Perpustakaan / Detail buku', 'Date': '25 Oktober 2026'}}},
    ]
    (temp / 'plan.json').write_text(json.dumps(plan))
    subprocess.run([CLI, 'run', str(temp / 'plan.json'), '--in', str(file), '--out', str(temp / 'changed.figcraft')],
                   capture_output=True, text=True, check=True)
    changed = read(temp / 'changed.figcraft')
    check(changed)
    navbar = changed['nodes'][str(first)]
    assert navbar['width'] == 1368
    texts = [changed['nodes'][str(i)]['characters'] for i in navbar['children'] if changed['nodes'][str(i)]['type'] == 'text']
    assert texts == ['Perpustakaan / Detail buku', '25 Oktober 2026']
    assert navbar['props']['Breadcrumb'] == 'Perpustakaan / Detail buku'

report = {'result': 'passed', 'component': 'Navbar', 'screen_instances': 8,
          'properties': ['Breadcrumb', 'Date'], 'responsive_widths': [1208, 1368],
          'sidebar_collapse': True, 'text_overrides': True}
(OUT / 'navbar-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
