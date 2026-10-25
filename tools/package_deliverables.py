"""Combine the current diagrams and build an optional local delivery bundle."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
writer = PdfWriter()
for path in sorted((DOCS / 'diagrams').glob('*.pdf')):
    writer.append(PdfReader(path))

with (DOCS / 'Diagram-Perpus-Merah-Putih.pdf').open('wb') as target:
    writer.write(target)

archive = DOCS / 'Perpus-Merah-Putih-dokumen.zip'
with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as bundle:
    for folder in [DOCS, ROOT / 'tools', ROOT / 'code']:
        for path in sorted(folder.rglob('*')):
            include = path.is_file() and path != archive and '__pycache__' not in path.parts and path.name != '.DS_Store' and not path.name.startswith('~$')
            if include:
                bundle.write(path, path.relative_to(ROOT))

print(f'Packaged docs/{archive.name}')
