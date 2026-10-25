"""Measure full page reflow at two viewport widths and both sidebar states."""
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
screens = json.loads((OUT / 'assets.json').read_text())['frames']


def read(path):
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        return json.loads(archive.read('document.json'))['nodes']


def children(nodes, parent):
    return [nodes[str(i)] for i in parent.get('children', [])]


def position(n):
    return n.get('transform', [1, 0, 0, 1, 0, 0])[4:6]


def inspect_screen(*, nodes, ident, state, width):
    root = nodes[str(ident)]
    root_children = children(nodes, root)
    side = next(n for n in root_children if n['name'] == 'Sidebar')
    main = next(n for n in root_children if n['name'] == 'SidebarInset')
    nav = next(n for n in children(nodes, main) if n['name'] == 'Navbar')
    page = next(n for n in children(nodes, main) if n['name'] == 'PageContent')
    content_width = width - (72 if state == 'Collapsed' else 232)
    assert root['layout']['mode'] == 'horizontal'
    assert main['layout']['mode'] == page['layout']['mode'] == 'vertical'
    assert main['width'] == page['width'] == nav['width'] == content_width
    assert page['child_layout']['sizing_h'] == page['child_layout']['sizing_v'] == 'fill'
    assert len(children(nodes, main)) == 2
    inner_width = content_width - 80
    last_bottom = 0
    for n in children(nodes, page):
        px, py = position(n)
        assert abs(px-40) < .01
        assert abs(n['width']-inner_width) < .01, (ident, n['name'], n['width'], inner_width)
        assert py >= last_bottom - .01
        assert py+n['height'] <= page['height']-24+.01, (ident, n['name'], 'page overflow')
        last_bottom = py+n['height']
        if n['type'] == 'frame' and n.get('children'):
            assert n.get('layout'), (ident, n['name'], 'missing auto layout')

    menus = [n for n in children(nodes, side) if n.get('component') in [135, 138]]
    assert len(menus) == 5
    for menu in menus:
        icon = next(n for n in children(nodes, menu) if n['type'] == 'instance')
        assert icon['width'] == icon['height'] == 24
        assert position(icon) == [4, 4]
        assert menu['props']['Show label'] == (state == 'Expanded')

    measured = {}

    def check_flow(n):
        if n['type'] != 'frame':
            return
        descendants = children(nodes, n)
        if descendants:
            assert n.get('layout'), (ident, n['id'], n['name'], 'non-auto container')
        for child in descendants:
            if child['type'] == 'frame':
                check_flow(child)
        if n['name'] in ['Card / Book metadata', 'Table / Books', 'Table / Book copies', 'Field / Cari koleksi']:
            measured[n['name']] = n['width']
        if n['name'].startswith('Field /'):
            control = next(c for c in descendants if c['name'] in ['Input', 'Textarea'])
            assert abs(control['width']-n['width']) < .01
            assert control.get('layout')
        if n['name'].startswith('Table /'):
            head = next(c for c in descendants if c['name'] == 'TableHeader')
            head_cells = children(nodes, head)
            for row in descendants:
                if not row['name'].startswith('TableRow /'):
                    continue
                cells = children(nodes, row)
                assert len(cells) == len(head_cells)
                for cell, heading in zip(cells, head_cells):
                    assert abs(position(cell)[0]-position(heading)[0]) < .01
                    assert abs(cell['width']-heading['width']) < .01

    check_flow(page)
    return {'screen': ident, 'state': state, 'viewport_width': width, 'content_width': inner_width, 'regions': measured}


nodes = read(file)
sides = {ident: next(n['id'] for n in children(nodes, nodes[str(ident)]) if n['name'] == 'Sidebar') for ident in screens.values()}
checks = []
with tempfile.TemporaryDirectory(prefix='pmp-page-reflow-') as folder:
    temp = Path(folder)
    for width in [1440, 1280]:
        for state in ['Expanded', 'Collapsed']:
            plan = []
            for ident in screens.values():
                plan += [
                    {'command': 'node.set', 'params': {'ids': [ident], 'props': {'width': width}}},
                    {'command': 'instance.setProperties', 'params': {'ids': [sides[ident]], 'properties': {'State': state}}},
                ]
            (temp / 'plan.json').write_text(json.dumps(plan))
            target = temp / f'{width}-{state}.figcraft'
            subprocess.run([CLI, 'run', str(temp / 'plan.json'), '--in', str(file), '--out', str(target)],
                           capture_output=True, text=True, check=True)
            current = read(target)
            for ident in screens.values():
                checks.append(inspect_screen(nodes=current, ident=ident, state=state, width=width))

for width in [1440, 1280]:
    for ident in screens.values():
        expanded = next(c for c in checks if c['viewport_width'] == width and c['screen'] == ident and c['state'] == 'Expanded')
        collapsed = next(c for c in checks if c['viewport_width'] == width and c['screen'] == ident and c['state'] == 'Collapsed')
        for region, expanded_width in expanded['regions'].items():
            assert abs(collapsed['regions'][region]-expanded_width-160) < .01, (ident, region, 'does not expand by sidebar delta')

report = {'result': 'passed', 'screens': len(screens), 'viewports': [1440, 1280],
          'states': ['Expanded', 'Collapsed'], 'complete_screen_checks': len(checks),
          'body_width_delta': 160, 'forms_filters_tables_resize': True, 'nested_containers_auto_layout': True,
          'table_columns_aligned': True, 'page_overflow': False, 'checks': checks}
(OUT / 'responsive-pages-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, indent=2))
