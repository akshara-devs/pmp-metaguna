"""Verify the saved sidebar variants, screen instances, reflow, and renders."""
from pathlib import Path
from zipfile import ZipFile
import json
import argparse
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/librarian-books'
assets = json.loads((OUT / 'sidebar-assets.json').read_text())
screens = json.loads((OUT / 'assets.json').read_text())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--file', type=Path, default=ROOT / 'docs' / 'Perpus Merah Putih.figcraft')
with ZipFile(parser.parse_args().file) as archive:
    assert archive.testzip() is None
    doc = json.loads(archive.read('document.json'))
nodes = doc['nodes']


def subtree(ident):
    n = nodes[str(ident)]
    return [n] + [descendant for child in n.get('children', []) for descendant in subtree(child)]


component_set = nodes[str(assets['set'])]
assert component_set['type'] == 'componentSet'
assert component_set['name'] == 'Sidebar'
assert set(component_set['children']) == {assets['expanded'], assets['collapsed']}
for key, width in [('expanded', 232), ('collapsed', 72)]:
    master = nodes[str(assets[key])]
    assert master['type'] == 'component'
    assert master['name'] == f'State={key.title()}'
    assert (master['width'], master['height']) == (width, 1000)

collapsed = subtree(assets['collapsed'])
assert all(n.get('visible') is False for n in collapsed if n['type'] == 'text')
nav_items = [n for n in collapsed if n['name'].startswith('SidebarMenuButton /')]
assert len(nav_items) == 5
assert all(n['width'] == 32 and n['transform'][4] == 20 for n in nav_items)
assert any(n['name'] == 'Sidebar account icon' and n.get('visible', True) for n in collapsed)
for trigger, destination in zip(assets['triggers'], [assets['collapsed'], assets['expanded']]):
    n = nodes[str(trigger)]
    assert n['width'] == n['height'] == 32
    assert any(a['type'] == 'changeTo' and a['dest'] == destination
               for interaction in n['interactions'] for a in interaction['actions'])

assert len(assets['instances']) == len(screens['frames']) == 8
for ident in screens['frames'].values():
    screen = nodes[str(ident)]
    sidebar = next(nodes[str(child)] for child in screen['children'] if nodes[str(child)]['name'] == 'Sidebar')
    inset = next(nodes[str(child)] for child in screen['children'] if nodes[str(child)]['name'] == 'SidebarInset')
    assert screen['layout']['mode'] == 'horizontal'
    assert sidebar['type'] == 'instance'
    assert sidebar['component'] in [assets['expanded'], assets['collapsed']]
    assert inset['child_layout']['sizing_h'] == 'fill'
    assert inset['width'] + sidebar['width'] == screen['width'] == 1440
    assert inset['transform'][4] == sidebar['width']
    if ident == screens['frames']['list-collapsed']:
        assert sidebar['width'] == 72 and inset['width'] == 1368
    else:
        assert sidebar['width'] == 232 and inset['width'] == 1208

# This image was exported after changing the original screen's State property,
# independently of the preconfigured collapsed reference screen.
with Image.open(OUT / 'sidebar-swap-proof.png') as proof, Image.open(OUT / 'list-collapsed-light.png') as sample:
    assert proof.size == sample.size == (1440, 1000)
    assert ImageChops.difference(proof.convert('RGB'), sample.convert('RGB')).getbbox() is None

for mode in ['light', 'dark']:
    for key, width in [('expanded', 232), ('collapsed', 72)]:
        with Image.open(OUT / f'sidebar-{key}-{mode}.png') as image:
            assert image.size == (width, 1000)
            image.verify()

report = {'result': 'passed', 'variants': ['Expanded', 'Collapsed'], 'widths': [232, 72],
          'screen_instances': 8, 'visible_collapsed_text_layers': 0,
          'toggle_directions': 2, 'native_variant_swap_matches_collapsed_reference': True,
          'inset_widths': [1208, 1368], 'modes': ['Light', 'Dark']}
(OUT / 'sidebar-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
