"""Regenerate portable diagrams, Mermaid sources, and BRD exports."""
from pathlib import Path
from html import escape
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
OUT = DOCS / 'diagrams'
MODEL = json.loads((DOCS / 'source/model.json').read_text())
INK, ACCENT, MUTED, PAPER, SURFACE = '#003E51', '#00758D', '#696F80', '#FAFAF7', '#F7F7F7'
FONT_LINK = 'https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&family=Roboto:wght@400;500;700&display=swap'


def text(*, x, y, value, size=16, color=INK, weight=400, anchor='start', family='Arial'):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>'


def rect(*, x, y, width, height, fill='none', stroke=INK, radius=0):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def line(*, x1, y1, x2, y2, color=INK, dashed=False, width=1.8):
    dash = ' stroke-dasharray="7 5"' if dashed else ''
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>'


def cardinal(*, point, toward, kind):
    x, y = point
    tx, ty = toward
    dx, dy = tx - x, ty - y
    length = (dx * dx + dy * dy) ** .5
    ux, uy = dx / length, dy / length
    vx, vy = -uy, ux

    def pos(distance, side=0):
        return (x + ux * distance + vx * side, y + uy * distance + vy * side)

    def bar(distance):
        a, b = pos(distance, -7), pos(distance, 7)
        return line(x1=a[0], y1=a[1], x2=b[0], y2=b[1])

    def circle(distance):
        a, b = pos(distance)
        return f'<circle cx="{a}" cy="{b}" r="5" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>'

    if kind == 'one':
        return bar(8) + bar(16)

    if kind == 'optional':
        return bar(8) + circle(23)

    paths = []
    center = pos(21)
    for side in [-8, 0, 8]:
        tip = pos(1, side)
        paths.append(line(x1=center[0], y1=center[1], x2=tip[0], y2=tip[1]))

    return ''.join(paths) + circle(33)


def connector(*, points, parent_kind='one', child_kind='many', label, label_at):
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in points)
    lx, ly = label_at
    label_width = len(label) * 7.2 + 20
    return (f'<path d="{d}" fill="none" stroke="{PAPER}" stroke-width="8"/>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.8"/>'
            + cardinal(point=points[0], toward=points[1], kind=parent_kind)
            + cardinal(point=points[-1], toward=points[-2], kind=child_kind)
            + rect(x=lx-label_width/2, y=ly-16, width=label_width, height=25, fill=PAPER, stroke='none')
            + text(x=lx, y=ly+2, value=label, size=13, anchor='middle'))


def entity(*, key, x, y, width=360, fields=None, context=False):
    spec = MODEL['entities'][key]
    selected = spec['fields'] if fields is None else [f for f in spec['fields'] if f[0] in fields]
    height = 68 + len(selected) * 26
    parts = [rect(x=x, y=y, width=width, height=height, fill=PAPER, stroke=ACCENT, radius=4),
             rect(x=x, y=y, width=width, height=48, fill=ACCENT, stroke=ACCENT, radius=4),
             text(x=x+18, y=y+31, value=key, color='#FFFFFF', size=20, weight=700)]
    for i, (name, tag, dtype) in enumerate(selected):
        baseline = y + 76 + i * 26
        parts.extend([text(x=x+15, y=baseline, value=tag, size=11, color=ACCENT, weight=700),
                      text(x=x+74, y=baseline, value=name, size=14),
                      text(x=x+width-14, y=baseline, value=dtype, size=11, color=MUTED, anchor='end')])


    return ''.join(parts), height


def svg_page(*, slug, title, subtitle, width, height, content, notes):
    legend = []
    if slug.startswith('01'):
        for px, kind, label in [(80, 'one', 'Exactly one'), (330, 'optional', 'Zero or one'), (620, 'many', 'Zero or many')]:
            legend.append(line(x1=px, y1=height-88, x2=px+65, y2=height-88))
            legend.append(cardinal(point=(px,height-88), toward=(px+65,height-88), kind=kind))
            legend.append(text(x=px+80, y=height-82, value=label, size=15))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{slug}-title {slug}-desc">'
            f'<title id="{slug}-title">{escape(title)}</title><desc id="{slug}-desc">{escape(subtitle)}</desc>'
            + rect(x=0,y=0,width=width,height=height,fill=PAPER,stroke='none')
            + rect(x=64,y=48,width=48,height=5,fill=ACCENT,stroke='none')
            + text(x=64,y=98,value=title,size=30,weight=700)
            + text(x=64,y=130,value=subtitle,size=16,color=MUTED)
            + content + ''.join(legend)
            + line(x1=64,y1=height-120,x2=width-64,y2=height-120,color=MUTED,width=.7)
            + text(x=64,y=height-40,value=notes,size=14,color=MUTED) + '</svg>')


def save_diagram(*, slug, title, svg, mermaid=None):
    (OUT / f'{slug}.svg').write_text(svg)
    html = (f'<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>'
            f'<link href="{FONT_LINK.replace("&", "&amp;")}" rel="stylesheet"><style>body{{margin:0;color:{INK};background:{PAPER};font-family:Roboto,Arial,sans-serif}}'
            'h1{font-family:Inter,Arial,sans-serif;font-size:24px;margin:24px} .diagram-scroll{overflow-x:auto}svg{display:block;max-width:none;min-width:var(--diagram-width)}'
            f'</style></head><body><div class="diagram-scroll" style="--diagram-width:{re.search(r"width=\"(\d+)\"",svg).group(1)}px">{svg}</div></body></html>')
    (OUT / f'{slug}.html').write_text(html)
    if mermaid:
        (OUT / f'{slug}.mmd').write_text(mermaid)


def build_er():
    entities = MODEL['entities']
    er = ['erDiagram']
    for key, spec in entities.items():
        er.append(f'    {key} {{')
        for field, tag, dtype in spec['fields']:
            scalar = dtype.split('(')[0].split(' ')[0].replace('?', '')
            constraint = 'PK' if tag == 'PK' else 'FK' if 'FK' in tag else 'UK' if tag.startswith('UK') and '*' not in tag else ''
            er.append(f'        {scalar} {field} {constraint}')
        er.append('    }')

    for parent, child, fk, p_kind, c_kind, label in MODEL['relations']:
        p = '||' if p_kind == 'one' else '|o'
        c = 'o{' if c_kind == 'many' else 'o|'
        er.append(f'    {parent} {p}..{c} {child} : "{fk}"')

    (OUT / '01-erd-lengkap.mmd').write_text('\n'.join(er)+'\n')

    # Each FK is shown once across these three complementary views.
    panels = [
        ('01a-erd-koleksi-pengajuan','ERD 1/3 · Books and loan requests',1240,1220,
         [('categories',64,180,330,None),('books',530,180,430,None),('users',64,700,400,None),('loan_requests',650,700,430,None)],
         [dict(points=[(394,245),(530,245)],label='category_id',label_at=(462,218)),
          dict(points=[(745,456),(745,560),(810,560),(810,700)],label='book_id',label_at=(810,620)),
          dict(points=[(464,825),(650,825)],label='student_id',label_at=(557,795))],
         'One books record = one physical book per title. ISBN is required and unique. No quantity or copy records.'),
        ('01b-erd-sirkulasi','ERD 2/3 · Loans and fines',1100,1160,
         [('loan_requests',64,200,360,['id','student_id','book_id','status']),('loans',550,200,410,None),('fines',550,700,410,None)],
         [dict(points=[(424,290),(550,290)],child_kind='optional',label='loan_request_id',label_at=(487,260)),
          dict(points=[(750,502),(750,700)],child_kind='optional',label='loan_id',label_at=(840,600))],
         'Each loan identifies one physical book through its request. The due date cannot be extended.'),
        ('01c-erd-kebijakan-petugas','ERD 3/3 · Policies and transaction actors',1660,1360,
         [('users',64,180,410,None),('lending_policies',700,180,410,None),('loan_requests',64,880,410,['id','reviewed_by','policy_id']),('loans',700,880,430,['id','policy_id','issued_by','returned_to']),('fines',1230,880,360,['id','payment_recorded_by'])],
         [dict(points=[(474,250),(700,250)],label='created_by',label_at=(588,220)),
          dict(points=[(900,430),(900,880)],label='policy_id',label_at=(990,730)),
          dict(points=[(1110,380),(1170,380),(1170,1210),(270,1210),(270,1026)],parent_kind='optional',label='policy_id',label_at=(650,1210)),
          dict(points=[(160,430),(160,880)],parent_kind='optional',label='reviewed_by',label_at=(235,740)),
          dict(points=[(280,430),(280,580),(620,580),(620,960),(700,960)],label='issued_by',label_at=(450,580)),
          dict(points=[(390,430),(390,660),(540,660),(540,1020),(700,1020)],parent_kind='optional',label='returned_to',label_at=(465,660)),
          dict(points=[(474,350),(530,350),(530,150),(1490,150),(1490,880)],parent_kind='optional',label='payment_recorded_by',label_at=(1370,150))],
         'Policies are versioned. Staff foreign keys must reference LIBRARIAN users. See the data dictionary for other attributes.')
    ]
    for slug,title,w,h,nodes,edges,note in panels:
        content = ''.join(connector(**e) for e in edges)
        for key,x,y,nw,fields in nodes:
            rendered,_ = entity(key=key,x=x,y=y,width=nw,fields=fields,context=fields is not None)
            content += rendered
        save_diagram(slug=slug,title=title,svg=svg_page(slug=slug,title=title,subtitle='Relational model · crow\'s foot · PK / FK / UK · ? = nullable',width=w,height=h,content=content,notes=note))


def arrow(*, start, end, y, label, dashed=False, accent=False):
    color = ACCENT if accent else INK
    direction = 1 if end > start else -1
    mid = (start + end) / 2
    width = len(label) * 7.1 + 18
    head = f'M{end} {y} L{end-direction*11} {y-5} L{end-direction*11} {y+5} Z'
    return (line(x1=start,y1=y,x2=end,y2=y,color=color,dashed=dashed)
            + f'<path d="{head}" fill="{color}"/>'
            + rect(x=mid-width/2,y=y-30,width=width,height=24,fill=PAPER,stroke='none')
            + text(x=mid,y=y-12,value=label,size=14,color=color,anchor='middle'))


def fragment(*, x, y, width, height, guard, alternate, divider):
    return (rect(x=x,y=y,width=width,height=height,stroke=MUTED)
            + rect(x=x,y=y,width=58,height=27,fill=SURFACE,stroke=MUTED)
            + text(x=x+13,y=y+19,value='alt',size=15,weight=700)
            + text(x=x+75,y=y+23,value=guard,size=14,color=ACCENT)
            + line(x1=x,y1=divider,x2=x+width,y2=divider,dashed=True,color=MUTED,width=1)
            + text(x=x+16,y=divider+25,value=alternate,size=14,color=MUTED))


SEQUENCES = [
    dict(slug='02-pengajuan',title='Pengajuan pinjaman online',actor='Mahasiswa',interface='Web PMP',reference='FR-06, FR-07 · BR-01, BR-05, BR-06, BR-10',
         messages=[(0,1,230,'Pilih judul dan ajukan'),(1,2,300,'Kirim ID buku'),(2,3,370,'Baca aturan, kuota, antrean, status buku'),(3,2,440,'Hasil validasi ',True),(2,3,580,'Simpan sebagai WAITING atau QUEUED'),(3,2,650,'ID dan posisi antrean',True),(2,1,720,'Pengajuan tercatat',True,True),(1,0,790,'Tampilkan status dan posisi',True),(2,1,920,'Tolak beserta alasan',True),(1,0,990,'Tampilkan alasan',True)],
         branch=(490,1060,850,'[akun dan syarat valid]','[syarat tidak terpenuhi]'),
         notes=['Awal transaksi: kunci akun dan judul, lalu validasi kembali. Commit setelah data tersimpan.','WAITING jika buku tersedia; QUEUED jika tidak. Keduanya belum menahan buku atau kuota.']),
    dict(slug='03-persetujuan',title='Persetujuan dan penyiapan buku',actor='Pustakawan',reference='FR-08, FR-09 · BR-04, BR-05, BR-07, BR-08',
         messages=[(0,1,230,'Pilih pengajuan tertua'),(1,2,300,'Setujui pengajuan'),(2,3,370,'Kunci akun, buku, dan pengajuan'),(3,2,440,'Kuota, kelayakan, status buku, urutan',True),(2,3,580,'Simpan READY_FOR_PICKUP dan batas ambil'),(3,2,650,'Penyiapan dan versi kebijakan tersimpan',True),(2,1,720,'Persetujuan berhasil',True,True),(1,0,790,'Tampilkan ISBN dan batas ambil',True),(2,1,920,'Tolak tindakan beserta alasan',True),(1,0,990,'Tampilkan konflik atau ketidaklayakan',True)],
         branch=(490,1060,850,'[urutan, buku, dan syarat valid]','[buku, urutan, atau syarat tidak valid]'),
         notes=['Satu buku hanya boleh disiapkan untuk satu pemohon. Commit status + kebijakan; batas awal 2 hari.','Jika pemohon tidak layak, petugas dapat menolak dengan alasan. Konflik ketersediaan tidak menolak pemohon otomatis.']),
    dict(slug='04-pengambilan',title='Pengambilan dan pencatatan pinjaman',actor='Pustakawan',reference='FR-09, FR-10 · BR-02, BR-09, BR-13, BR-14',
         messages=[(0,1,230,'Verifikasi mahasiswa dan ISBN'),(1,2,300,'Konfirmasi penyerahan'),(2,3,370,'Kunci buku; cek status, batas, kuota'),(3,2,440,'Hasil validasi dan kebijakan terbaru',True),(2,3,580,'Buat pinjaman; pengajuan COMPLETED'),(3,2,650,'ID pinjaman dan jatuh tempo',True),(2,1,720,'Penyerahan tercatat',True,True),(1,0,790,'Tampilkan bukti dan jatuh tempo',True),(2,3,920,'Kedaluwarsa? Lepaskan penyiapan buku'),(3,2,990,'Status akhir atau alasan penolakan',True),(2,1,1060,'Tolak penyerahan beserta alasan',True)],
         branch=(490,1130,850,'[buku disiapkan dan pemohon valid]','[kedaluwarsa atau syarat tidak valid]'),
         notes=['Pinjaman dimulai saat penyerahan. Versi kebijakan pinjaman diambil saat penyerahan, bukan saat pengajuan.','Batas awal 5 hari. Jika kuota turun, persetujuan lama tidak dibatalkan otomatis; petugas membatalkannya.']),
    dict(slug='05-pengembalian',title='Pengembalian dan perhitungan denda',actor='Pustakawan',reference='FR-07, FR-11, FR-12 · BR-03, BR-11, BR-12',
         messages=[(0,1,230,'Masukkan pinjaman dan kondisi buku'),(1,2,300,'Catat pengembalian'),(2,3,370,'Kunci buku, pengajuan, dan pinjaman'),(3,2,440,'Pinjaman aktif dan tarif historis',True),(2,3,510,'Tutup pinjaman; simpan kondisi'),(2,3,650,'Buat satu denda final'),(3,2,720,'Tagihan tersimpan',True),(3,2,850,'Tidak ada tagihan',True),(2,3,940,'Buku tersedia; evaluasi antrean tertua'),(3,2,1010,'Commit pengembalian dan antrean',True),(2,1,1080,'Pengembalian tercatat',True,True),(1,0,1150,'Tampilkan bukti dan jumlah denda',True)],
         branch=(560,890,770,'[terlambat dan tarif lebih dari 0]','[tepat waktu atau tarif 0]'),
         notes=['Denda = selisih tanggal lokal positif × tarif pinjaman. Kembali 31 Okt, tempo 29 Okt: 2 × Rp1.000.','Buku tidak layak dinonaktifkan dalam transaksi yang sama. Antrean tetap memerlukan persetujuan.']),
    dict(slug='06-pelunasan',title='Pencatatan pelunasan denda',actor='Pustakawan',reference='FR-12 · BR-12, BR-16',
         messages=[(0,1,230,'Verifikasi pembayaran penuh di luar aplikasi'),(1,2,300,'Catat pelunasan dan referensi bukti'),(2,3,370,'Kunci tagihan dan periksa status'),(3,2,440,'Jumlah dan status tagihan',True),(2,3,580,'Simpan petugas, waktu, referensi bayar'),(3,2,650,'Commit tagihan lunas',True),(2,1,720,'Pelunasan tercatat',True,True),(1,0,790,'Tampilkan bukti pencatatan',True),(2,1,920,'Kembalikan status yang sudah lunas',True),(1,0,990,'Tidak mencatat pelunasan kedua',True)],
         branch=(490,1060,850,'[tagihan belum lunas dan bukti valid]','[tagihan sudah lunas, kiriman ulang]'),
         notes=['Aplikasi hanya mencatat pelunasan penuh. Tidak memproses pembayaran, cicilan, atau penghapusan denda.','Bukti kosong atau jumlah tidak sesuai ditolak sebelum penulisan. Hanya pustakawan dapat mencatat lunas.'])
]


def build_sequences():
    xs = [160, 550, 1000, 1480]
    for item in SEQUENCES:
        slug, title = item['slug'], item['title']
        last_y = max(m[2] for m in item['messages'])
        diagram_bottom = max(last_y+65, item['branch'][1]+35)
        height = diagram_bottom+210
        content = ''
        participants = [item['actor'], item.get('interface', 'Web UI'), 'Library Service', 'Database']
        for x,label in zip(xs,participants):
            content += rect(x=x-125,y=146,width=250,height=48,fill=SURFACE,stroke=ACCENT)
            content += text(x=x,y=177,value=label,size=17,weight=700,anchor='middle')
            content += line(x1=x,y1=194,x2=x,y2=diagram_bottom,dashed=True,color=MUTED,width=1)

        content += rect(x=xs[2]-5,y=293,width=10,height=diagram_bottom-310,fill='#D8E9EC',stroke=ACCENT)
        content += rect(x=xs[3]-5,y=363,width=10,height=diagram_bottom-385,fill='#E2E5E9',stroke=MUTED)
        fy,fb,divider,guard,alternate=item['branch']
        content += fragment(x=65,y=fy,width=1480,height=fb-fy,guard=guard,alternate=alternate,divider=divider)
        for msg in item['messages']:
            a,b,y,label,*options=msg
            content += arrow(start=xs[a],end=xs[b],y=y,label=label,dashed=options[0] if options else False,accent=options[1] if len(options)>1 else False)
        for n,note in enumerate(item['notes']):
            content += text(x=64,y=diagram_bottom+38+n*27,value=note,size=14,color=MUTED)
        svg = svg_page(slug=slug,title=title,subtitle=item['reference']+' · waktu bergerak dari atas ke bawah',width=1620,height=height,content=content,notes='Garis penuh = call; garis putus-putus = return. Alt = percabangan. Kotak tipis = activation bar.')
        mermaid=['sequenceDiagram','    autonumber']
        for i,label in enumerate(participants):
            mermaid.append(f'    {"actor" if i == 0 else "participant"} P{i} as {label}')
        branch_open=False
        alternate_open=False
        for msg in item['messages']:
            a,b,y,label,*options=msg
            if not branch_open and y>fy:
                mermaid.append(f'    alt {guard}')
                branch_open=True
            if branch_open and not alternate_open and y>divider:
                mermaid.append(f'    else {alternate}')
                alternate_open=True
            if branch_open and y>fb:
                mermaid.append('    end')
                branch_open=False
                fy=100000
            symbol='-->>' if options and options[0] else '->>'
            mermaid.append(f'    P{a}{symbol}P{b}: {label}')
        if branch_open:
            mermaid.append('    end')
        for note in item['notes']:
            mermaid.append(f'    Note over P0,P3: {note}')
        save_diagram(slug=slug,title=title,svg=svg,mermaid='\n'.join(mermaid)+'\n')


def build_dictionary():
    target = DOCS / 'Kamus-data.md'
    body = target.read_text().split('\n<!-- GENERATED FIELDS -->')[0]
    rows=['\n<!-- GENERATED FIELDS -->','\n## Daftar atribut lengkap\n']
    for key,spec in MODEL['entities'].items():
        rows.extend([f'### {spec["label"]} · `{key}`\n','| Atribut | Kunci | Tipe logis |','| --- | --- | --- |'])
        for name,tag,dtype in spec['fields']:
            rows.append(f'| {name} | {tag or "-"} | {dtype} |')
        rows.append('')
    target.write_text(body+'\n'.join(rows))


def build_brd_exports():
    import markdown
    from bs4 import BeautifulSoup
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

    src = DOCS / 'BRD-perpus-merah-putih.md'
    rendered=markdown.markdown(src.read_text(),extensions=['tables'])
    css=f'body{{font-family:Roboto,Arial,sans-serif;color:{INK};max-width:1000px;margin:40px auto;line-height:1.6;padding:0 20px}}h1,h2,h3,h4{{font-family:Inter,Arial,sans-serif}}h1,h2{{color:{ACCENT}}}table{{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}}th,td{{border:1px solid #ccd8dc;text-align:left;padding:10px;vertical-align:top}}th{{background:{SURFACE}}}a{{color:{ACCENT}}}@media print{{body{{margin:0;max-width:none}}h2,h3{{break-after:avoid}}tr{{break-inside:avoid}}}}'
    (DOCS/'BRD-perpus-merah-putih.html').write_text(f'<!doctype html><html lang="id"><head><meta charset="utf-8"><title>BRD Perpus Merah Putih</title><link href="{FONT_LINK.replace("&","&amp;")}" rel="stylesheet"><style>{css}</style></head><body>{rendered}</body></html>')
    subprocess.run(['pandoc',str(src),'-o',str(DOCS/'BRD-perpus-merah-putih.docx'),'--metadata','lang=id-ID'],check=True)
    from update_docx_toc import update_toc
    update_toc(DOCS / 'BRD-perpus-merah-putih.docx')
    from style_brd_cover import style_cover
    style_cover(DOCS / 'BRD-perpus-merah-putih.docx')

    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyID',fontName='Helvetica',fontSize=9.5,leading=14,spaceAfter=7,textColor=colors.HexColor(INK)))
    styles.add(ParagraphStyle(name='CellID',parent=styles['BodyID'],fontSize=8,leading=11,spaceAfter=0))
    for level,size in [('Heading1',25),('Heading2',17),('Heading3',12),('Heading4',10)]:
        styles[level].textColor=colors.HexColor(ACCENT)
        styles[level].fontSize=size
        styles[level].leading=size*1.25
        styles[level].spaceBefore=14
        styles[level].spaceAfter=8
    story=[]
    soup=BeautifulSoup(rendered,'html.parser')
    def clean(element):
        s=str(element)
        s=re.sub(r'<code>(.*?)</code>',r'<font name="Courier">\1</font>',s)
        return re.sub(r'</?(p|h[1-6])[^>]*>','',s)
    for element in soup.children:
        name=getattr(element,'name',None)
        if name is None:
            continue
        if name in ['h1','h2','h3','h4']:
            story.append(Paragraph(element.get_text(),styles['Heading'+name[1]]))
        elif name=='p':
            story.append(Paragraph(clean(element),styles['BodyID']))
        elif name in ['ul','ol']:
            for i,li in enumerate(element.find_all('li',recursive=False)):
                prefix=f'{i+1}.' if name=='ol' else '-'
                story.append(Paragraph(prefix+' '+li.decode_contents(),styles['BodyID']))
        elif name=='table':
            data=[[Paragraph(cell.decode_contents(),styles['CellID']) for cell in row.find_all(['th','td'])] for row in element.find_all('tr')]
            count=len(data[0])
            widths={2:[120,387],3:[58,155,294],4:[110,130,130,137]}.get(count,[507/count]*count)
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F0F2')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#C7D4D8')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,10)])

    def footer(canvas,doc):
        canvas.saveState()
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(44,28,'Perpus Merah Putih | BRD v1.3 | Draf untuk peninjauan')
        canvas.drawRightString(A4[0]-44,28,str(doc.page))
        canvas.restoreState()

    pdf=SimpleDocTemplate(str(DOCS/'BRD-perpus-merah-putih.pdf'),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=40,bottomMargin=44,title='BRD Perpus Merah Putih',author='Penyusun proyek')
    pdf.build(story,onFirstPage=footer,onLaterPages=footer)


def build_gallery():
    diagrams=sorted(OUT.glob('*.svg'))
    figures=[]
    for path in diagrams:
        content=path.read_text()
        title=re.search(r'<title[^>]*>(.*?)</title>',content).group(1)
        figures.append(f'<section><h2>{title}</h2><div class="diagram-scroll">{content}</div></section>')
    css='body{margin:0;color:#003E51;background:#FAFAF7;font-family:Roboto,Arial,sans-serif}main{padding:32px}h1,h2{font-family:Inter,Arial,sans-serif}h1{font-size:30px}h2{font-size:20px}section{margin-top:32px}.diagram-scroll{overflow-x:auto;border:1px solid #ccd8dc}svg{display:block;min-width:1200px;width:100%;height:auto}p{max-width:850px;line-height:1.6}'
    (DOCS/'diagram-perpustakaan.html').write_text(f'<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Diagram Perpus Merah Putih</title><link href="{FONT_LINK.replace("&","&amp;")}" rel="stylesheet"><style>{css}</style></head><body><main><h1>Diagram Perpus Merah Putih</h1><p>Tiga lembar ERD dan lima diagram sequence. Gulir di dalam setiap diagram untuk membaca pada ukuran asli. Warna mengikuti situs Metaguna. Berkas SVG, Mermaid, dan FigCraft tersedia terpisah.</p>{"".join(figures)}</main></body></html>')


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    build_er()
    build_sequences()
    build_dictionary()
    build_brd_exports()
    build_gallery()
    print('Generated BRD exports, dictionary, 3 ERD views, and 5 sequence diagrams.')
