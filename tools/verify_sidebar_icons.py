"""Prove icon choices survive native layout edits, property swaps, and reopen."""
from pathlib import Path
from zipfile import ZipFile
import json
import subprocess
import tempfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'docs' / 'Perpus Merah Putih.figcraft'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--file', type=Path, default=FILE)
FILE = parser.parse_args().file
OUT = ROOT / 'docs/librarian-books'
CLI = '/Users/macbookpro/.local/bin/figcraft-cli'
EXPECTED = {'Buku': 144, 'Katalog': 144, 'Peminjaman': 150, 'Mahasiswa': 174, 'Reservasi': 171, 'Denda': 183}


def read(path):
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        return json.loads(archive.read('document.json'))


def normalized_shape(network):
    vertices = network['vertices']
    left, top = min(v['x'] for v in vertices), min(v['y'] for v in vertices)
    width = max(v['x'] for v in vertices) - left
    height = max(v['y'] for v in vertices) - top
    points = [(round((v['x']-left)/width, 6), round((v['y']-top)/height, 6)) for v in vertices]
    segments = [(s['a'], s['b'], tuple(round(v/size, 6) for v, size in zip(s['ta'], [width, height])),
                 tuple(round(v/size, 6) for v, size in zip(s['tb'], [width, height]))) for s in network['segments']]
    return json.dumps([points, segments, network['regions']], sort_keys=True)


def check(doc):
    nodes = doc['nodes']
    checked = []
    shapes = set()
    for ident in [135, 138]:
        n = nodes[str(ident)]
        assert n['layout']['mode'] == 'horizontal'
        assert n['props']['Icon']['type'] == 'instanceSwap'
        assert n['props']['Show label']['type'] == 'boolean'

    for n in nodes.values():
        if n['type'] != 'instance' or n.get('component') not in [135, 138]:
            continue
        label = n['props']['Label']
        assert n['props']['Icon'] == EXPECTED[label], (n['id'], label, 'wrong Icon property')
        icon = next(nodes[str(i)] for i in n['children'] if nodes[str(i)]['type'] == 'instance')
        assert icon['component'] == EXPECTED[label], (n['id'], label, 'wrong nested icon')
        property_source = icon
        visited = set()
        while 'mainComponent' not in property_source.get('prop_refs', {}):
            assert property_source['id'] not in visited
            visited.add(property_source['id'])
            property_source = nodes[str(property_source['source'])]
        assert property_source['prop_refs']['mainComponent'] == 'Icon'
        glyph = nodes[str(icon['children'][0])]
        original = nodes[str(nodes[str(EXPECTED[label])]['children'][0])]
        assert normalized_shape(glyph['network']) == normalized_shape(original['network']), (n['id'], label, 'wrong rendered shape')
        text = next(nodes[str(i)] for i in n['children'] if nodes[str(i)]['type'] == 'text')
        assert text['characters'] == label
        assert text.get('visible', True) == n['props']['Show label']
        assert icon['width'] == icon['height'] == 24
        if not n['props']['Show label']:
            assert abs(icon['transform'][4] + icon['width']/2 - n['width']/2) < 0.01
            assert abs(icon['transform'][5] + icon['height']/2 - n['height']/2) < 0.01
            for axis, dimension in [(4, 'width'), (5, 'height')]:
                actual_center = glyph['transform'][axis] + glyph[dimension]/2
                source_center = original['transform'][axis] + original[dimension]/2
                assert abs(actual_center - source_center) < 0.01
        shapes.add(normalized_shape(glyph['network']))
        checked.append(n['id'])

    assert len(checked) == 50 and len(shapes) == 5
    return checked


original = read(FILE)
checked = check(original)
loans = next(n['id'] for n in original['nodes'].values()
             if n['type'] == 'instance' and n.get('component') == 135 and n.get('props', {}).get('Label') == 'Peminjaman')

with tempfile.TemporaryDirectory(prefix='pmp-sidebar-icons-') as folder:
    temp = Path(folder)
    plan = [
        {'command': 'node.set', 'params': {'ids': [135, 138], 'props': {'layout': 'vertical', 'gap': 12}}},
        {'command': 'node.set', 'params': {'ids': [135, 138], 'props': {'layout': 'horizontal', 'gap': 8, 'padding': [4, 4, 4, 4]}}},
        {'command': 'instance.setProperties', 'params': {'ids': [loans], 'properties': {'Icon': 183}}},
        {'command': 'instance.setProperties', 'params': {'ids': [loans], 'properties': {'Icon': 150}}},
    ]
    (temp / 'plan.json').write_text(json.dumps(plan))
    result = subprocess.run([CLI, 'run', str(temp / 'plan.json'), '--in', str(FILE), '--out', str(temp / 'refreshed.figcraft')],
                            capture_output=True, text=True, check=True)
    assert all(json.loads(line).get('ok') for line in result.stdout.splitlines() if line.startswith('{'))
    check(read(temp / 'refreshed.figcraft'))
    # A second CLI invocation reloads and resolves the saved component graph.
    (temp / 'reopen.json').write_text(json.dumps([{'command': 'component.properties', 'params': {'id': 135}}]))
    subprocess.run([CLI, 'run', str(temp / 'reopen.json'), '--in', str(temp / 'refreshed.figcraft'), '--out', str(temp / 'reopened.figcraft')],
                   capture_output=True, text=True, check=True)
    check(read(temp / 'reopened.figcraft'))

report = {'result': 'passed', 'menu_instances': len(checked), 'distinct_icons': 5,
          'auto_layout_direction_round_trip': True, 'icon_swap_round_trip': True, 'reopen': True}
(OUT / 'icon-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
