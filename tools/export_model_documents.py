"""Export the saved ERD/sequence FigCraft document without touching the live session."""
from pathlib import Path
from zipfile import ZipFile
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'docs' / 'Perpus Merah Putih — BRD dan diagram.figcraft'
OUT = ROOT / 'docs/diagrams'
with ZipFile(FILE) as archive:
    doc = json.loads(archive.read('document.json'))

names = {'01-erd-lengkap': 'Complete ERD · Perpus Merah Putih', '01a-erd-koleksi-pengajuan': 'ERD 1/3 · Books and loan requests', '01b-erd-sirkulasi': 'ERD 2/3 · Loans and fines', '01c-erd-kebijakan-petugas': 'ERD 3/3 · Policies and transaction actors'}
slugs = list(names) + ['02-pengajuan', '03-persetujuan', '04-pengambilan', '05-pengembalian', '06-pelunasan']
commands = []
for slug in slugs:
    frame = next(n for n in doc['nodes'].values() if n['type'] == 'frame' and n['name'] == names.get(slug, slug))
    for fmt in ['png', 'pdf']:
        commands.append({'command': 'file.export', 'params': {'ids': [frame['id']], 'format': fmt, 'scale': 2 if slug == '01-erd-lengkap' and fmt == 'png' else 1, 'path': str(OUT / (slug + '.' + fmt))}})

commands.append({'command': 'file.export', 'params': {'format': 'fig', 'path': str(ROOT / 'docs/Perpus-Merah-Putih.fig')}})
workspace = tempfile.TemporaryDirectory(prefix='pmp-diagram-export-')
plan = Path(workspace.name) / 'export.json'
plan.write_text(json.dumps(commands))
result = subprocess.run(['/Users/macbookpro/.local/bin/figcraft-cli', 'run', str(plan), '--in', str(FILE)], capture_output=True, text=True)
failures = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{') and not json.loads(line).get('ok')]
if result.returncode or failures:
    raise RuntimeError((result.stderr, failures))

print('Exported all 9 diagram PNG/PDF files and the editable experimental Figma copy.')

workspace.cleanup()
