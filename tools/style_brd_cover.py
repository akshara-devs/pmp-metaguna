"""Create an editable typographic cover without changing the document body."""
from pathlib import Path
from zipfile import ZipFile
import re
from lxml import etree as ET

WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': WORD_NS}
INK = '003E51'
TEAL = '00758D'
MUTED = '696F80'


def element(name, **attributes):
    return ET.Element(f'{{{WORD_NS}}}{name}', {f'{{{WORD_NS}}}{key}': str(value) for key, value in attributes.items()})


def paragraph(*, value, size=12, color=INK, bold=False, before=0, after=0, line=18, tracking=0, shading=None, rule=None, right_tab=False):
    paragraph = element('p')
    props = element('pPr')
    props.append(element('pStyle', val='Normal'))
    props.append(element('spacing', before=before*20, after=after*20, line=line*20, lineRule='exact'))
    props.append(element('outlineLvl', val='9'))
    props.append(element('keepNext', val='0'))
    props.append(element('keepLines'))
    if shading:
        props.append(element('shd', val='clear', fill=shading))
    if rule:
        borders = element('pBdr')
        borders.append(element('bottom', val='single', sz='12', space='10', color=rule))
        props.append(borders)
    if right_tab:
        tabs = element('tabs')
        tabs.append(element('tab', val='right', pos='9026'))
        props.append(tabs)
    paragraph.append(props)

    parts = re.split(r'([\n\t])', value)
    for part in parts:
        run = element('r')
        run_props = element('rPr')
        run_props.append(element('rFonts', ascii='Arial', hAnsi='Arial', cs='Arial'))
        run_props.append(element('sz', val=int(size*2)))
        run_props.append(element('color', val=color))
        run_props.append(element('spacing', val=int(tracking*20)))
        if bold:
            run_props.append(element('b'))
        run.append(run_props)
        if part == '\n':
            run.append(element('br'))
        elif part == '\t':
            run.append(element('tab'))
        else:
            content = element('t')
            content.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            content.text = part
            run.append(content)
        paragraph.append(run)

    return paragraph


def style_cover(path):
    with ZipFile(path) as archive:
        entries = [(item, archive.read(item.filename)) for item in archive.infolist()]

    parts = {item.filename: content for item, content in entries}
    document = ET.fromstring(parts['word/document.xml'])
    body = document.find('w:body', NS)
    toc_heading = next(p for p in body.findall('w:p', NS) if ''.join(p.itertext()).casefold() in ['table of contents', 'daftar isi'])
    leading_elements = list(body)[:list(body).index(toc_heading)]
    for node in leading_elements:
        if node.tag == f'{{{WORD_NS}}}p':
            body.remove(node)

    source = path.with_suffix('.md').read_text()
    version = re.search(r'Versi (\d+\.\d+)', source).group(1)
    date = re.search(r'Versi [^|]+\| ([^|]+)\|', source).group(1).strip()
    cover = [
        paragraph(value='  PMP-01     /     PERPUSTAKAAN KAMPUS', size=10, color='FFFFFF', bold=True, line=29, after=38, shading=INK, tracking=.5),
        paragraph(value='PROJECT DOCUMENT', size=10, color=TEAL, bold=True, line=16, after=17, tracking=1.8),
        paragraph(value='Perpus\nMerah Putih', size=48, color=INK, bold=True, line=54, after=22),
        paragraph(value='Aplikasi web untuk mengelola buku\ndan layanan peminjaman perpustakaan kampus.', size=12, color=MUTED, line=19, after=35),
        paragraph(value='BUSINESS REQUIREMENTS\nDOCUMENT', size=17, color=TEAL, bold=True, line=24, after=28, tracking=.4),
        paragraph(value='SCOPE  /  BOOK MANAGEMENT & BORROWING', size=9, color=MUTED, line=15, after=28, tracking=.5, rule=TEAL),
        paragraph(value=f'Version {version}\t{date}', size=11, line=18, after=9, right_tab=True),
        paragraph(value='Document status\tDraf untuk peninjauan', size=10, color=MUTED, line=17, after=54, right_tab=True),
        paragraph(value='BUSINESS REQUIREMENTS DOCUMENT   /   BRD', size=8, color=MUTED, line=13, tracking=.7),
    ]
    for index, node in enumerate(cover):
        body.insert(index, node)

    parts['word/document.xml'] = ET.tostring(document, encoding='UTF-8', xml_declaration=True, standalone=True)
    temporary = path.with_suffix('.cover.docx')
    with ZipFile(temporary, 'w') as archive:
        for item, content in entries:
            archive.writestr(item, parts[item.filename])
    temporary.replace(path)

    html_path = path.with_suffix('.html')
    if html_path.exists():
        html = html_path.read_text()
        cover_html = f'''<section class="brd-cover" aria-label="Cover BRD">
<div class="cover-band">PMP-01　 /　 PERPUSTAKAAN KAMPUS</div>
<p class="cover-kicker">PROJECT DOCUMENT</p>
<h1>Perpus<br>Merah Putih</h1>
<p class="cover-summary">Aplikasi web untuk mengelola buku<br>dan layanan peminjaman perpustakaan kampus.</p>
<p class="cover-kind">BUSINESS REQUIREMENTS<br>DOCUMENT</p>
<p class="cover-scope">SCOPE / BOOK MANAGEMENT &amp; BORROWING</p>
<p class="cover-meta"><span>Version {version}</span><span>{date}</span></p>
<p class="cover-meta cover-status"><span>Document status</span><span>Draf untuk peninjauan</span></p>
<p class="cover-foot">BUSINESS REQUIREMENTS DOCUMENT / BRD</p></section>'''
        css = '<style>.brd-cover{max-width:640px;min-height:850px;font-family:Arial,sans-serif;break-after:page}.cover-band{background:#003E51;color:white;padding:12px 16px;font-size:13px;font-weight:bold;letter-spacing:1px}.brd-cover .cover-kicker{margin:48px 0 20px;color:#00758D;font-size:13px;font-weight:bold;letter-spacing:2px}.brd-cover h1{font-family:Arial,sans-serif;font-size:64px;line-height:1.13;color:#003E51;margin:0 0 34px}.brd-cover .cover-summary{font-size:16px;line-height:1.6;color:#696F80}.brd-cover .cover-kind{font-weight:bold;font-size:23px;line-height:1.4;color:#00758D;margin-top:52px}.brd-cover .cover-scope{font-size:11px;color:#696F80;margin-top:44px;padding-bottom:16px;border-bottom:2px solid #00758D}.brd-cover .cover-meta{display:flex;justify-content:space-between;gap:16px;font-size:14px;margin-top:28px}.brd-cover .cover-status{color:#696F80;font-size:13px;margin-top:10px}.brd-cover .cover-foot{font-size:10px;letter-spacing:1px;color:#696F80;margin-top:80px}</style>'
        html = re.sub(r'<body>.*?(?=<h2[^>]*>Table of contents)', '<body>' + cover_html, html, count=1, flags=re.S)
        html_path.write_text(html.replace('</head>', css + '</head>'))


if __name__ == '__main__':
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'docs/BRD-perpus-merah-putih.docx'
    style_cover(path)
    print('Editable BRD cover updated.')
