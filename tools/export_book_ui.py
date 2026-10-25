"""Export current book screens in Light/Dark and both sidebar states."""
from pathlib import Path
from zipfile import ZipFile
import json
import subprocess
import tempfile
import shutil
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/librarian-books'
FILE = ROOT / 'docs' / 'Perpus Merah Putih.figcraft'
assets = json.loads((OUT / 'assets.json').read_text())
with ZipFile(FILE) as archive:
    nodes = json.loads(archive.read('document.json'))['nodes']

sidebars = {}
for key, ident in assets['frames'].items():
    sidebars[key] = next(nodes[str(i)] for i in nodes[str(ident)]['children'] if nodes[str(i)]['name'] == 'Sidebar')

workspace = tempfile.TemporaryDirectory(prefix='pmp-book-export-')
pdf_dir = Path(workspace.name)
commands = []
for mode in ['Light', 'Dark']:
    commands.append({'command': 'variable.setMode', 'params': {'ids': [assets['page']], 'collection': 'Shark Theme', 'mode': mode}})
    for key, ident in assets['frames'].items():
        for fmt in ['png', 'svg', 'pdf']:
            commands.append({'command': 'file.export', 'params': {'ids': [ident], 'format': fmt, 'svgOutlineText': False, 'path': str((pdf_dir if fmt == 'pdf' else OUT) / f'{key}-{mode.lower()}.{fmt}')}})

for mode in ['Light', 'Dark']:
    commands.append({'command': 'variable.setMode', 'params': {'ids': [assets['page']], 'collection': 'Shark Theme', 'mode': mode}})
    for state in ['Expanded', 'Collapsed']:
        for sidebar in sidebars.values():
            commands.append({'command': 'instance.setProperties', 'params': {'ids': [sidebar['id']], 'properties': {'State': state}}})
        for key, ident in assets['frames'].items():
            commands.append({'command': 'file.export', 'params': {'ids': [ident], 'format': 'png', 'path': str(OUT / f'responsive-{key}-{state.lower()}-{mode.lower()}.png')}})

for sidebar in sidebars.values():
    commands.append({'command': 'instance.setProperties', 'params': {'ids': [sidebar['id']], 'properties': {'State': ('Collapsed' if sidebar['width'] == 72 else 'Expanded')}}})

commands.append({'command': 'variable.setMode', 'params': {'ids': [assets['page']], 'collection': 'Shark Theme', 'mode': 'Light'}})
plan = pdf_dir / 'export.json'
plan.write_text(json.dumps(commands))
result = subprocess.run(['/Users/macbookpro/.local/bin/figcraft-cli', 'run', str(plan), '--in', str(FILE), '--out', str(FILE)], capture_output=True, text=True)

failures = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{') and not json.loads(line).get('ok')]
if result.returncode or failures:
    raise RuntimeError((result.stderr, failures))

shutil.copyfile(OUT / 'responsive-list-collapsed-light.png', OUT / 'sidebar-swap-proof.png')

for mode in ['light', 'dark']:
    writer = PdfWriter()
    for key in assets['frames']:
        writer.append(PdfReader(pdf_dir / f'{key}-{mode}.pdf'))
    with (OUT / f'Librarian-books-{mode}.pdf').open('wb') as target:
        writer.write(target)

labels = {'list': 'Daftar buku', 'add': 'Tambah buku', 'detail': 'Detail buku', 'edit': 'Edit buku', 'deactivate': 'Nonaktifkan buku', 'empty': 'Pencarian kosong', 'list-collapsed': 'Daftar dengan sidebar collapsed', 'isbn-error': 'ISBN sudah digunakan'}
html = '''<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kelola buku per ISBN</title><style>body{margin:0;font-family:var(--font-sans,Arial);color:var(--foreground,#000)}.controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}select{padding:8px;border:1px solid var(--border,#000);border-radius:6px;background:var(--card,#fff);color:inherit}#screen{flex:1;min-width:190px}.canvas{overflow:auto;border:1px solid var(--border,#000);border-radius:8px}img{display:none;width:100%;height:auto}</style><div class="controls"><select id="screen" aria-label="Layar">'''
html += ''.join(f'<option value="{key}">{labels[key]}</option>' for key in assets['frames'])
html += '''</select><select id="mode" aria-label="Mode"><option value="light">Light</option><option value="dark">Dark</option></select><select id="state" aria-label="Sidebar"><option value="expanded">Expanded</option><option value="collapsed">Collapsed</option></select></div><div class="canvas">'''
for key in assets['frames']:
    for mode in ['light', 'dark']:
        for state in ['expanded', 'collapsed']:
            name = f'responsive-{key}-{state}-{mode}'
            html += f'<img id="{key}-{state}-{mode}" src="{name}.png" alt="{labels[key]} · {state} · {mode}">'
html += '''</div><script>const screen=document.getElementById('screen'),mode=document.getElementById('mode'),state=document.getElementById('state');function update(){document.querySelectorAll('img').forEach(im=>im.style.display=im.id===screen.value+'-'+state.value+'-'+mode.value?'block':'none')}for(const el of[screen,mode,state])el.addEventListener('change',update);update();</script></html>'''
for name in ['preview.html', 'responsive-preview.html']:
    (OUT / name).write_text(html)

print('Exported 8 screens in both modes, responsive previews, and 8-page PDFs.')

workspace.cleanup()
