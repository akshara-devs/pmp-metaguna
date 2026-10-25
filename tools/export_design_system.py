"""Export the native Shark library in both modes, then restore Light for editing."""
from pathlib import Path
import json
import subprocess
import tempfile
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/design-system'
CLI='/Users/macbookpro/.local/bin/figcraft-cli'
FILE=ROOT / 'docs' / 'Perpus Merah Putih.figcraft'
assets=json.loads((OUT/'assets.json').read_text())
keys=['board.foundations','board.buttons','board.forms','board.patterns','screen.catalog','screen.admin','screen.mobile']
# Resolve inherited component values once before exporting the default mode.
commands=[{'command':'variable.setMode','params':{'ids':[page],'collection':'Shark Theme','mode':'Dark'}} for page in [1,88,193,278,381]]
for mode in ['Light','Dark']:
 for page in [1,88,193,278,381]:
  commands.append({'command':'variable.setMode','params':{'ids':[page],'collection':'Shark Theme','mode':mode}})
 for key in keys:
  stem=key.replace('.','-')+('-dark' if mode=='Dark' else '')
  for fmt in ['png','pdf','svg']:
   commands.append({'command':'file.export','params':{'ids':[assets[key]],'format':fmt,'svgOutlineText':False,'path':str(OUT/(stem+'.'+fmt))}})
for page in [1,88,193,278,381]:commands.append({'command':'variable.setMode','params':{'ids':[page],'collection':'Shark Theme','mode':'Light'}})
# Focused native Button exports make content positioning reviewable at actual size.
for sample,ident in [('default',96),('focus',105)]:
 commands.append({'command':'file.export','params':{'ids':[ident],'format':'png','scale':2,'path':str(OUT/('button-'+sample+'.png'))}})
commands.append({'command':'file.export','params':{'format':'fig','path':str(OUT/'Perpus-Merah-Putih-design-system.fig')}})
workspace=tempfile.TemporaryDirectory(prefix='pmp-design-export-')
plan=Path(workspace.name)/'export.json'
plan.write_text(json.dumps(commands))
result=subprocess.run([CLI,'run',str(plan),'--in',str(FILE),'--out',str(FILE)],capture_output=True,text=True)

errors=[json.loads(line) for line in result.stdout.splitlines() if line.startswith('{') and not json.loads(line).get('ok')]
if result.returncode or errors:raise RuntimeError((result.stderr,errors))
for mode in ['light','dark']:
 writer=PdfWriter()
 for key in keys:writer.append(PdfReader(OUT/(key.replace('.','-')+('-dark' if mode=='dark' else '')+'.pdf')))
 with (OUT/('Design-system'+('-dark' if mode=='dark' else '')+'.pdf')).open('wb') as target:writer.write(target)
print('Exported 14 Light/Dark boards and screens as PNG, PDF, SVG; editable .fig.')

workspace.cleanup()
