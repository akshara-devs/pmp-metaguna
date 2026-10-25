"""Create fresh instances from each initial variant and exercise both switching APIs."""
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
COMPONENT = {'Expanded': 1732, 'Collapsed': 1766}


def read(path):
    with ZipFile(path) as archive:
        return json.loads(archive.read('document.json'))['nodes']


def run(*, plan, source, target, folder):
    script = folder / 'plan.json'
    script.write_text(json.dumps(plan))
    result = subprocess.run([CLI, 'run', str(script), '--in', str(source), '--out', str(target)],
                            capture_output=True, text=True, check=True)
    return [json.loads(line)['result'] for line in result.stdout.splitlines() if line.startswith('{')]


def check(*, nodes, ident, state):
    sidebar = nodes[str(ident)]
    assert sidebar['component'] == COMPONENT[state]
    assert sidebar['width'] == (232 if state == 'Expanded' else 72)
    menus = [nodes[str(i)] for i in sidebar['children'] if nodes[str(i)].get('component') in [135, 138]]
    assert len(menus) == 5
    for menu in menus:
        assert menu['layout']['padding'] == [4, 4, 4, 4]
        assert menu['layout']['main_align'] == 'min'
        assert menu['layout']['cross_align'] == 'center'
        assert menu['width'] == (192 if state == 'Expanded' else 32)
        assert menu.get('transform', [0]*6)[4] == 20
        icon = next(nodes[str(i)] for i in menu['children'] if nodes[str(i)]['type'] == 'instance')
        assert icon['width'] == icon['height'] == 24
        assert icon.get('transform', [0]*6)[4:6] == [4, 4]
        label = next(nodes[str(i)] for i in menu['children'] if nodes[str(i)]['type'] == 'text')
        assert label.get('visible', True) == (state == 'Expanded')


checks = []
with tempfile.TemporaryDirectory(prefix='pmp-initial-sidebar-') as folder:
    temp = Path(folder)
    for method in ['instance.setProperties', 'instance.swap']:
        for initial in ['Expanded', 'Collapsed']:
            source = temp / f'{method}-{initial}-initial.figcraft'
            # Creation directly from the selected master is intentional. Setting a
            # pre-existing instance's State would miss the reported starting-state bug.
            result = run(plan=[{'command': 'instance.create', 'params': {'component': COMPONENT[initial], 'parent': 741, 'x': 5000, 'y': 0}}],
                         source=file, target=source, folder=temp)
            ident = result[0]['id']
            check(nodes=read(source), ident=ident, state=initial)
            opposite = 'Collapsed' if initial == 'Expanded' else 'Expanded'
            for turn, state in enumerate([opposite, initial, opposite]):
                params = {'ids': [ident], 'properties': {'State': state}} if method == 'instance.setProperties' else {'ids': [ident], 'component': COMPONENT[state]}
                target = temp / f'{method}-{initial}-{turn}.figcraft'
                run(plan=[{'command': method, 'params': params}], source=source, target=target, folder=temp)
                check(nodes=read(target), ident=ident, state=state)
                checks.append({'initial': initial, 'method': method, 'state': state, 'aligned_icons': 5})
                source = target

report = {'result': 'passed', 'fresh_initial_variants': ['Expanded', 'Collapsed'],
          'switching_methods': ['instance.setProperties', 'instance.swap'],
          'transitions': len(checks), 'icon_alignment_checks': len(checks)*5,
          'identical_padding_alignment_icon_position': True, 'checks': checks}
(OUT / 'sidebar-initial-state-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, indent=2))
