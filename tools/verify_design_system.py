"""Verify the final native shadcn library, source tokens, instances, and exports."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib
import json
import argparse
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/design-system'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--file', type=Path, default=ROOT / 'docs' / 'Perpus Merah Putih.figcraft')
with ZipFile(parser.parse_args().file) as archive:
 assert archive.testzip() is None
 document=json.loads(archive.read('document.json'))
nodes=document['nodes'];assets=json.loads((OUT/'assets.json').read_text())
source=json.loads((OUT/'tweakcn-shark-theme.json').read_text())
manifest=json.loads((OUT/'shadcn-components.json').read_text())
counts=Counter(n['type'] for n in nodes.values())
assert {1,88,193,278,381} <= set(document['pages'])
sidebar_variants = 2 if (ROOT/'docs/librarian-books/sidebar-assets.json').exists() else 0
navbar_components = 1 if (ROOT/'docs/librarian-books/navbar-assets.json').exists() else 0
assert counts['component']==68+sidebar_variants+navbar_components and counts['componentSet']==7+bool(sidebar_variants) and counts['instance']>=29
assert len(document['styles'])==15
collection,=document['variables']['collections'];assert collection['name']=='Shark Theme'
modes={m['name'].lower():m['id'] for m in collection['modes']};assert set(modes)=={'light','dark'}
variables={v['name']:v for v in document['variables']['variables']};var_ids={v['id'] for v in variables.values()}
for mode,values in source['styles'].items():
 for name,value in values.items():
  actual=variables[name]['values'][modes[mode]]['value']
  if value.startswith('#'):
   expected=[int(value[i:i+2],16)/255 for i in (1,3,5)]+[1]
   assert all(abs(actual[c]-v)<1e-6 for c,v in zip(('r','g','b','a'),expected)),(mode,name)
  else:assert actual==value,(mode,name)
for n in nodes.values():
 for target in n.get('bound',{}).values():assert target in var_ids,(n['id'],target)
 if n['type']=='text':assert n['style']['font_family']=='Inter Tight'
 if n['type']=='component':assert n.get('description','').startswith(('shadcn/ui','Lucide official')),n['name']
 if n['type']=='instance':assert str(n['component']) in nodes
for page in document['pages']:assert nodes[str(page)]['var_modes'][collection['id']]==modes['light']
for key in ['checkbox.false','checkbox.true','switch.false','switch.true']:
 n=nodes[str(assets[key])]
 assert any(a.get('type')=='changeTo' for i in n.get('interactions',[]) for a in i.get('actions',[]))
for key in ['book.available','book.unavailable']:
 n=nodes[str(assets[key])]
 assert {'Title','Cover title','Category','Availability'}<=set(n['props'])
 assert {'CardHeader','CardContent','CardFooter'}<={nodes[str(c)]['name'] for c in n['children']}
button_set=nodes['131'];buttons=[nodes[str(i)] for i in button_set['children']]
assert {n['name'].split(',')[0] for n in buttons}=={'Variant='+v for v in manifest['button_variants']}
for n in buttons:
 size=n['name'].split('Size=')[1].split(',')[0]
 assert n['height']=={'default':36,'xs':24,'sm':32,'lg':40,'icon':36}[size]
for n in nodes.values():
 if n['type']=='instance' and n.get('component') in [96,114,123,129]:assert n['height']==36,(n['id'],n['height'])
# Verify final native geometry, not only the height token or alignment setting.
# Previously the label retained y=12 from a 44 px control inside a 36 px button.
checked_button_children=0
for n in nodes.values():
 if n['type'] not in ['component','instance']:continue
 definition=nodes[str(n['component'])] if n['type']=='instance' else n
 if '/button.json' not in definition.get('description',''):continue
 for child_id in n.get('children',[]):
  child=nodes[str(child_id)]
  if child['type'] not in ['text','vector']:continue
  assert abs(child.get('transform',[1,0,0,1,0,0])[5]-(n['height']-child['height'])/2)<.01,(n['id'],child_id,'Button content is not vertically centered')
  checked_button_children+=1
assert checked_button_children>=30
for id in [203,209,215,221,227]:assert nodes[str(id)]['height']==36
assert nodes['215']['bound']['stroke']==variables['ring']['id']
assert nodes['215']['effects'][0]['spread']==3
assert nodes['221']['bound']['stroke']==variables['destructive']['id']
for id in [234,237]:assert (nodes[str(id)]['width'],nodes[str(id)]['height'])==(16,16)
for id in [241,245]:assert (nodes[str(id)]['width'],nodes[str(id)]['height'])==(32,18.4)
for id in [406,572]:assert nodes[str(id)]['bound']['fill']==variables['card']['id']
for id in [253,257,261]:
 n=nodes[str(id)];assert n['bound']['fill']==variables['card']['id'];assert n['bound']['stroke']==variables['border']['id']
 assert {'AlertTitle','AlertDescription'}<={nodes[str(c)]['name'] for c in n['children']}
assert nodes['263']['bound']['fill']==variables['destructive']['id']
badges=[nodes[str(i)] for i in nodes['321']['children']]
assert len(badges)==14 and {n['name'].split('Variant=')[1] for n in badges}==set(manifest['button_variants'])
assert all(n['height']==22 and n['width']<150 for n in badges)
assert nodes['275']['characters']=='Kembali' and nodes['275']['bound']['fill']==variables['foreground']['id']
assert nodes['343']['align_h']=='center' and nodes['343']['width']==542
for name,entry in manifest['sources'].items():
 data=(OUT/'shadcn-source'/(name+'.json')).read_bytes();assert hashlib.sha256(data).hexdigest()==entry['sha256']
assert len(manifest['sources'])==18
connect=json.loads((OUT/'shadcn-code-connect.json').read_text())
assert len(connect['links'])==30
assert {'Button','Field','Badge','Alert','Card','Checkbox','Switch','SidebarMenuButton','AlertDialog','Table','Empty','Toaster'}<={link['name'] for link in connect['links']}
keys=['board.foundations','board.buttons','board.forms','board.patterns','screen.catalog','screen.admin','screen.mobile']
for mode in ['light','dark']:
 for key in keys:
  frame=nodes[str(assets[key])];stem=key.replace('.','-')+('-dark' if mode=='dark' else '')
  with Image.open(OUT/(stem+'.png')) as image:
   assert image.size==(int(frame['width']),int(frame['height']))
   image.verify()
  assert len(PdfReader(OUT/(stem+'.pdf')).pages)==1
  assert ET.parse(OUT/(stem+'.svg')).getroot().findall('.//{http://www.w3.org/2000/svg}text')
 assert len(PdfReader(OUT/('Design-system'+('-dark' if mode=='dark' else '')+'.pdf')).pages)==7
 with Image.open(OUT/('screen-catalog'+('-dark' if mode=='dark' else '')+'.png')) as image:
  for point,token in [((240,100),'background'),((10,100),'sidebar'),((300,720),'primary'),((1280,320),'secondary')]:
   expected=tuple(int(source['styles'][mode][token][i:i+2],16) for i in (1,3,5))
   assert image.convert('RGB').getpixel(point)==expected,(mode,token,image.getpixel(point))
 with Image.open(OUT/('board-forms'+('-dark' if mode=='dark' else '')+'.png')) as image:
  expected=tuple(int(source['styles'][mode]['card'][i:i+2],16) for i in (1,3,5))
  assert image.convert('RGB').getpixel((800,1120))==expected,'Alert must use the standard card surface.'
# Check the rendered pixels as well as native geometry. The white label must be
# centered within the native button, allowing the font's small optical offset.
with Image.open(OUT/'button-default.png') as image:
 image=image.convert('RGBA')
 label_pixels=[(x,y) for y in range(image.height) for x in range(image.width) if all(c>245 for c in image.getpixel((x,y))[:3]) and image.getpixel((x,y))[3]>245]
 assert label_pixels
 label_center=(min(y for x,y in label_pixels)+max(y for x,y in label_pixels))/2
 assert abs(label_center-image.height/2)<=3,('Rendered Button label is too low',label_center,image.height)
css=(OUT/'shark-theme.css').read_text()
for values in source['styles'].values():
 for name,value in values.items():assert '--'+name+': '+value+';' in css
for name in ['variables.json','variables.css','tokens.json','README.md','shadcn-source/shadcn-LICENSE.md','shadcn-source/lucide-LICENSE']:
 assert (OUT/name).stat().st_size>0
font_temp=tempfile.TemporaryDirectory(prefix='pmp-font-check-');font_plan=Path(font_temp.name)/'fonts.json';font_plan.write_text(json.dumps([{'command':'text.fonts','params':{'family':f}} for f in ['Inter Tight','DM Sans','Space Mono']]))
r=subprocess.run(['/Users/macbookpro/.local/bin/figcraft-cli','run',str(font_plan)],capture_output=True,text=True,check=True)
fonts=[json.loads(line) for line in r.stdout.splitlines() if line.startswith('{')];assert len(fonts)==3 and all(f['ok'] and 'Regular' in f['result'] for f in fonts)

def luminance(value):
 rgb=[int(value[i:i+2],16)/255 for i in (1,3,5)]
 return sum((c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4)*w for c,w in zip(rgb,[.2126,.7152,.0722]))
def contrast(a,b):
 x,y=sorted([luminance(a),luminance(b)]);return round((y+.05)/(x+.05),2)
ratios={mode:{bg:contrast(values[fg],values[bg]) for bg,fg in [('primary','primary-foreground'),('secondary','secondary-foreground'),('accent','accent-foreground'),('destructive','destructive-foreground')]} for mode,values in source['styles'].items()}
report={'status':'passed','component_library':'shadcn/ui New York v4 / Radix','exact_source_tokens_per_mode':44,'source_colors_modified':False,'modes':['Light','Dark'],'pages':len(document['pages']),'main_components':counts['component'],'component_sets':counts['componentSet'],'instances':counts['instance'],'variables':len(variables),'styles':15,'exported_boards_and_screens':14,'official_registry_snapshots':18,'code_connections':len(connect['links']),'standard_alert_and_badge':True,'nested_button_instances_height':36,'editable_card_slots':True,'vertically_centered_button_children':checked_button_children,'source_fonts_available':['Inter Tight','DM Sans','Space Mono'],'raw_theme_contrast_ratios':ratios,'contrast_note':'Raw source-token ratios only. Component opacity modifiers and fixed text-white recipes follow upstream shadcn source. No blanket AA claim.'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

font_temp.cleanup()
