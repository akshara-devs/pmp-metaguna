"""Exercise both sidebar states on every actual screen, not only the component board."""
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
EXPECTED = {'Buku': 144, 'Peminjaman': 150, 'Mahasiswa': 174, 'Reservasi': 171, 'Denda': 183}


def read(path):
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        return json.loads(archive.read('document.json'))


doc = read(file)
sidebars = []
for ident in screens.values():
    screen = doc['nodes'][str(ident)]
    sidebars.append(next(i for i in screen['children'] if doc['nodes'][str(i)].get('component') in [1732, 1766]))

checks = []
with tempfile.TemporaryDirectory(prefix='pmp-all-sidebars-') as folder:
    temp = Path(folder)
    current = file
    for state in ['Collapsed', 'Expanded']:
        plan = [{'command': 'instance.setProperties', 'params': {'ids': [ident], 'properties': {'State': state}}} for ident in sidebars]
        (temp / 'plan.json').write_text(json.dumps(plan))
        target = temp / f'{state}.figcraft'
        subprocess.run([CLI, 'run', str(temp / 'plan.json'), '--in', str(current), '--out', str(target)],
                       capture_output=True, text=True, check=True)
        current = target
        nodes = read(target)['nodes']
        collapsed = state == 'Collapsed'
        for screen_id, side_id in zip(screens.values(), sidebars):
            side = nodes[str(side_id)]
            assert side['width'] == (72 if collapsed else 232)
            menus = [nodes[str(i)] for i in side['children'] if nodes[str(i)].get('component') in [135, 138]]
            assert len(menus) == 5
            for menu in menus:
                assert menu['width'] == (32 if collapsed else 192)
                assert menu['props']['Show label'] == (not collapsed)
                icon = next(nodes[str(i)] for i in menu['children'] if nodes[str(i)]['type'] == 'instance')
                label = next(nodes[str(i)] for i in menu['children'] if nodes[str(i)]['type'] == 'text')
                assert icon['component'] == EXPECTED[menu['props']['Label']]
                assert icon['width'] == icon['height'] == 24
                assert icon['transform'][4:6] == [4, 4]
                assert label.get('visible', True) == (not collapsed)
            inset = next(nodes[str(i)] for i in nodes[str(screen_id)]['children'] if nodes[str(i)]['name'] == 'SidebarInset')
            navbar = next(nodes[str(i)] for i in inset['children'] if nodes[str(i)]['name'] == 'Navbar')
            assert inset['width'] == navbar['width'] == (1368 if collapsed else 1208)
            trigger = next(nodes[str(i)] for i in side['children'] if nodes[str(i)]['name'].startswith('SidebarTrigger /'))
            while not trigger.get('interactions'):
                trigger = nodes[str(trigger['source'])]
            assert any(a['type'] == 'changeTo' and a['dest'] == (1732 if collapsed else 1766)
                       for interaction in trigger['interactions'] for a in interaction['actions'])
            checks.append({'screen': screen_id, 'state': state, 'aligned_icons': len(menus)})

report = {'result': 'passed', 'screens': len(sidebars), 'states': ['Collapsed', 'Expanded'],
          'menu_alignment_checks': sum(c['aligned_icons'] for c in checks),
          'navbar_reflow': True, 'prototype_toggle_targets': True, 'checks': checks}
(OUT / 'all-screen-sidebar-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, indent=2))
